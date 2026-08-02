# -*- coding: utf-8 -*-
"""从《IGCSE 自然科学英语核心词汇表》PDF 解析出结构化词表。

用法：python3 src/parse_pdf.py <pdf 路径> > src/parsed.json
依赖：PyMuPDF (pip install pymupdf)

PDF 是三栏表格（英文 / 中文释义 / 例句+翻译），按 y 坐标把每个英文词条
作为锚点分行；第九节「常用科学英语句型」是四栏，单独处理。
"""
import fitz, re, json, sys

CJK = re.compile(r'[一-鿿]')
SKIP_HEADERS = ('English term', '中文释义', 'Example sentence / 例句翻译',
                '内容目录', '用途', '句型框架', '英文例句', '中文翻译')


def parse(path):
    doc = fitz.open(path)
    sections, rows, frames = [], [], []
    in_frames = False

    for pi in range(1, len(doc)):                 # 第 0 页是封面
        L = []
        for b in doc[pi].get_text("dict")["blocks"]:
            if b["type"] != 0:
                continue
            for l in b["lines"]:
                t = "".join(s["text"] for s in l["spans"]).strip()
                if t:
                    L.append((round(l["bbox"][0]), round(l["bbox"][1]),
                              max(s["size"] for s in l["spans"]), t))
        L.sort(key=lambda t: (t[1], t[0]))

        terms, zh, ex, fr = [], [], [], []
        for x, y, size, t in L:
            if 280 < x < 340 and t.isdigit():             # 页码
                continue
            if t in SKIP_HEADERS or re.search(r'（\d+\s*[词组]）', t):   # 表头 / 目录
                continue
            if re.match(r'^[一二三四五六七八九十]、', t):              # 章标题
                title = re.sub(r'（.*?）', '', t).strip()
                sections.append({'title': title, 'key': (pi, y), 'items': []})
                in_frames = title.startswith('九')
                continue
            if size > 12:                                  # 标题折行
                if sections:
                    sections[-1]['title'] += ' ' + t
                continue
            if t.startswith('本节共') or t.startswith('这些句型'):
                continue
            if in_frames:
                fr.append((x, y, t))
            elif x < 100:
                if not CJK.search(t):
                    terms.append((y, t))
            elif x < 330:
                zh.append((y, t))
            else:
                ex.append((y, t))

        # 三栏词条：以英文词的 y 为中心，取相邻词条 y 的中点作为行边界
        terms.sort()
        for i, (y, t) in enumerate(terms):
            lo = -1e9 if i == 0 else (terms[i - 1][0] + y) / 2
            hi = 1e9 if i == len(terms) - 1 else (terms[i + 1][0] + y) / 2
            exl = [s for yy, s in sorted(ex) if lo <= yy < hi]
            rows.append(((pi, y), {
                'w': t,
                'zh': ' '.join(s for yy, s in sorted(zh) if lo <= yy < hi).strip(),
                'ex': ' '.join(s for s in exl if not CJK.search(s)).strip(),
                'exzh': ''.join(s for s in exl if CJK.search(s)).strip(),
            }))

        # 四栏句型
        if fr:
            anchors = sorted([(y, t) for x, y, t in fr if x < 100])
            for i, (y, t) in enumerate(anchors):
                lo = -1e9 if i == 0 else (anchors[i - 1][0] + y) / 2
                hi = 1e9 if i == len(anchors) - 1 else (anchors[i + 1][0] + y) / 2
                col = lambda a, b: ' '.join(s for x, yy, s in sorted(fr, key=lambda q: q[1])
                                            if a <= x < b and lo <= yy < hi).strip()
                frames.append({'use': t, 'frame': col(150, 290),
                               'ex': col(290, 420), 'exzh': col(420, 999).replace(' ', '')})

    for key, item in rows:                        # 词条归到它上方最近的章节
        sec = [s for s in sections if s['key'] <= key]
        sec[-1]['items'].append(item)
    return {'sections': [{'title': s['title'], 'items': s['items']}
                         for s in sections if s['items']], 'frames': frames}


if __name__ == '__main__':
    out = parse(sys.argv[1])
    for s in out['sections']:
        print(len(s['items']), s['title'], file=sys.stderr)
    print('TOTAL', sum(len(s['items']) for s in out['sections']),
          'frames', len(out['frames']), file=sys.stderr)
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
