# -*- coding: utf-8 -*-
"""把 src/parsed.json + src/phon.py 合成 src/data.json，再注入 src/tpl.html 生成 index.html。

用法：python3 src/build.py
产物：项目根目录的 index.html（单文件，含内嵌字体与全部词条，可离线打开）
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from phon import PHON                       # noqa: E402


def build_data():
    """parsed.json（PDF 原文）+ PHON（手写音标/音节/助记）→ data.json"""
    src = os.path.join(HERE, 'parsed.json')
    if not os.path.exists(src):              # 已经有合成好的 data.json 就直接用
        return json.load(open(os.path.join(HERE, 'data.json'), encoding='utf-8'))

    d = json.load(open(src, encoding='utf-8'))
    out, sid = {'sections': [], 'frames': d['frames']}, 0
    for s in d['sections']:
        if not s['items']:
            continue
        body = re.match(r'^[一二三四五六七八九]、(.+)$', s['title']).group(1)
        m = re.search(r'(?<=[一-鿿])(?=[A-Za-z])', body)     # 中英文标题分界
        cn, en = (body[:m.start()].strip(), body[m.start():].strip()) if m else (body, '')
        sid += 1
        words = []
        for it in s['items']:
            syl, tip = PHON[it['w']]
            # "ob=ˌɒb|ser=zə" → [[{t:'ob',p:'ˌɒb'},…]]，词与词之间用 " / " 分隔
            sw = [[{'t': x.split('=')[0], 'p': x.split('=')[1]} for x in p.split('|')]
                  for p in syl.split(' / ')]
            ipa = '/' + ' '.join(''.join(y['p'] for y in p) for p in sw) + '/'
            words.append({**it, 'ipa': ipa, 'syl': sw, 'tip': tip})
        out['sections'].append({'id': sid, 'cn': cn, 'en': en, 'words': words})

    json.dump(out, open(os.path.join(HERE, 'data.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    return out


def check(data):
    """音节拼写拼回原词必须一致，否则说明 PHON 写错了"""
    bad = []
    for s in data['sections']:
        for w in s['words']:
            rebuilt = ' '.join(''.join(y['t'] for y in p) for p in w['syl'])
            norm = lambda x: x.replace('-', '').replace(' ', '').lower()
            if norm(rebuilt) != norm(w['w']):
                bad.append((w['w'], rebuilt))
    if bad:
        raise SystemExit('音节拼写与原词不符: %s' % bad)
    return sum(len(s['words']) for s in data['sections'])


if __name__ == '__main__':
    data = build_data()
    n = check(data)
    tpl = open(os.path.join(HERE, 'tpl.html'), encoding='utf-8').read()
    assert '__DATA__' in tpl, 'tpl.html 缺少 __DATA__ 占位符'
    html = tpl.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    dst = os.path.join(ROOT, 'index.html')
    open(dst, 'w', encoding='utf-8').write(html)
    print('built %s — %d 词, %d KB' % (dst, n, round(os.path.getsize(dst) / 1024)))
