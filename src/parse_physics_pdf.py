# -*- coding: utf-8 -*-
"""从《Cambridge IGCSE Physics 0625 核心词汇表》PDF 解析出结构化词表。

用法：python3 src/parse_physics_pdf.py <pdf 路径> > src/parsed_phy.json
     python3 src/parse_physics_pdf.py <pdf 路径> --selftest
依赖：PyMuPDF (pip install pymupdf)

与 parse_pdf.py 处理的那份 PDF 结构不同：这份是真表格，四栏
（Key word / 中文 / English example / 例句中文），章标题是字号 >=13 的
「English / 中文」蓝色文本。
"""
import contextlib, io, fitz, json, sys

# 同一个词在两章里各出现一次时，保留定义性更强的那条
KEEP_DUP = {('temperature', '热学'), ('current', '电与磁')}
DUP_WORDS = {w for w, _ in KEEP_DUP}


def parse(path):
    doc = fitz.open(path)
    events = []                       # (页码, y, 类型, 内容)，最后按阅读顺序排

    for pi in range(len(doc)):
        pg = doc[pi]
        for b in pg.get_text("dict")["blocks"]:
            if b["type"] != 0:
                continue
            for l in b["lines"]:
                txt = "".join(s["text"] for s in l["spans"]).strip()
                size = max(s["size"] for s in l["spans"])
                # 章标题：大号字 + 「English / 中文」，排除页眉
                if size >= 13 and "/" in txt and not txt.startswith("Cambridge"):
                    events.append((pi, l["bbox"][1], "sec", txt))
        # find_tables() 会向 stdout 打印一条推广提示（"Consider using the
        # pymupdf_layout package..."），而本脚本的输出协议就是把 JSON 写到
        # stdout（`> src/parsed_phy.json`），这条提示混进去会把产物变成非法
        # JSON，所以要在调用期间把 stdout 接走。
        with contextlib.redirect_stdout(io.StringIO()):
            tables = pg.find_tables().tables
        for t in tables:
            for r in t.extract():
                cells = [(c or "").replace("\n", " ").strip() for c in r]
                if len(cells) < 4 or cells[0] == "Key word":
                    continue
                events.append((pi, t.bbox[1], "row", cells[:4]))

    events.sort(key=lambda e: (e[0], e[1]))

    sections = []
    for _, _, kind, pay in events:
        if kind == "sec":
            en, cn = [x.strip() for x in pay.split("/", 1)]
            sections.append({"cn": cn, "en": en, "items": []})
            continue
        if not sections:
            continue
        w, zh, ex, exzh = pay
        if not w:                                  # 跨页续行：首列为空，并回上一条
            if sections[-1]["items"]:
                prev = sections[-1]["items"][-1]
                prev["ex"] = (prev["ex"] + " " + ex).strip()
                prev["exzh"] = (prev["exzh"] + exzh).strip()
            continue
        if w in DUP_WORDS and (w, sections[-1]["cn"]) not in KEEP_DUP:
            continue                               # 重复词只留定义句更强的那章
        sections[-1]["items"].append({"w": w, "zh": zh, "ex": ex, "exzh": exzh})

    # 高频答题句型那章没有表格，解析后是空章，丢掉
    return {"sections": [s for s in sections if s["items"]]}


def selftest(out):
    secs = out["sections"]
    words = [it["w"] for s in secs for it in s["items"]]
    assert len(secs) == 11, "应有 11 章，实得 %d" % len(secs)
    assert len(words) == 162, "应有 162 词，实得 %d" % len(words)
    assert len(set(words)) == 162, "有重复词: %s" % [
        w for w in set(words) if words.count(w) > 1]
    for s in secs:
        for it in s["items"]:
            for k in ("w", "zh", "ex", "exzh"):
                assert it[k], "%s 的 %s 为空" % (it["w"], k)
    print("selftest OK — 11 章 162 词", file=sys.stderr)


if __name__ == '__main__':
    out = parse(sys.argv[1])
    if '--selftest' in sys.argv:
        selftest(out)
    else:
        for s in out['sections']:
            print(len(s['items']), s['cn'], file=sys.stderr)
        json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
