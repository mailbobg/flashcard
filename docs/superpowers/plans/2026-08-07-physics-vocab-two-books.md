# 物理词表接入与两本词书 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把《Cambridge IGCSE Physics 0625 核心词汇表》162 词接入闪卡，与现有 170 词并列为两本可切换的词书，并把「学习」页从 3 屏多的竖排卡片流改成 2.4 屏以内的紧凑网格。

**Architecture:** 数据层引入 `books` 一层，每个词条获得稳定 id `<bookId>:<word>`，`localStorage` 的进度改按 id 存放并一次性迁移旧数据。界面层由 `S.set.book` 驱动，学习/词表/句型三页共用同一当前科目，通过分段控件或左右滑动切换。音标字典 `PHON` 按裸词全局共用（51 个同名词天然复用），翻译思路 `TRANS` 按书各持一份。

**Tech Stack:** Python 3（PyMuPDF 解析 PDF、无框架的构建脚本）、原生 HTML/CSS/JS 单文件（无构建工具、无依赖、无 npm）。

## 本项目没有测试框架

这个仓库不用 pytest / jest，**不要引入**。它的测试harness 是两样东西，计划中的每个「测试」步骤都指其中之一：

1. **`python3 src/build.py`** —— 构建脚本内置校验，任一条不满足就 `raise SystemExit` 并打印原因。数据层的任务用「先加校验 → 跑构建看它失败 → 实现 → 跑构建看它通过」的顺序。
2. **浏览器验证** —— 通过 preview 工具打开 `http://localhost:8777/index.html`，用 `javascript_tool` 跑断言表达式、`computer{action:"screenshot"}` 出图。界面任务用这个。

启动预览服务器：`preview_start {name: "flashcard"}`（配置已在 `.claude/launch.json`）。**不要用 Bash 起服务器。**

## Global Constraints

- 单文件产物：`index.html` 必须零外部请求、断网可打开。不得引入 CDN、字体链接、fetch。
- 所有源改动都在 `src/` 下；`index.html` 是 `python3 src/build.py` 的产物，**永远不要手改**。
- 词条 id 格式固定为 `<bookId>:<word>`，bookId 只有 `sci` 和 `phy` 两个值。
- 两本书的中文标签固定为「科学」和「物理」。
- 现有 170 词的章节归属、释义、例句、音标、翻译思路一律不改。
- 界面文案用中文；代码注释沿用现有风格（中文、解释「为什么」而非「是什么」）。
- 提交信息用中文，格式 `<type>: <简述>`，结尾带 `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`。
- 设计依据：`docs/superpowers/specs/2026-08-07-physics-vocab-two-books-design.md`。
- 物理 PDF 路径（不入库，`.gitignore` 已排除 `*.pdf`）：
  `/Users/bobmax/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/bob743439_6d65/temp/drag/Cambridge_IGCSE_Physics_Core_Vocabulary_中英例句词汇表.pdf`

## 文件结构

| 文件 | 职责 |
| --- | --- |
| `src/parse_physics_pdf.py`（新） | 只负责把物理 PDF 变成 `src/parsed_phy.json`。四栏表格、跨页续行合并、章内重复词取舍 |
| `src/phon_phy.py`（新） | 物理独有的 111 词的音节切分与词根助记。纯数据 |
| `src/trans_phy.py`（新） | 物理 162 句的翻译思路。纯数据 |
| `src/frames_phy.py`（新） | 物理 10 组高频答题句型。纯数据 |
| `src/build.py`（改） | 合成两本书、补 id、跑五道校验、注入模板 |
| `src/lessons.py`（改） | 课时加 `book` 字段，`vocab` 支持跨书前缀 |
| `src/tpl.html`（改） | 界面。数据索引、存储迁移、三页的科目切换、章节网格 |
| `README.md`（改） | 词数、文件表、构建步骤 |

`phon_phy` / `trans_phy` / `frames_phy` 独立成文件而不并进现有的 `phon.py` / `trans.py`，
是为了让两份词表的来源保持可追溯，也避免 `trans.py` 从 1710 行涨到 3400 行。

---

## Task 1: 解析物理 PDF

**Files:**
- Create: `src/parse_physics_pdf.py`
- Create（产物，入库）: `src/parsed_phy.json`

**Interfaces:**
- Produces: `src/parsed_phy.json`，结构为
  ```
  {"sections": [{"cn": "题目指令词", "en": "Command words",
                 "items": [{"w": str, "zh": str, "ex": str, "exzh": str}, ...]}, ...]}
  ```
  共 11 章、162 条 items。后续 Task 2 读取它。

**背景：** 这份 PDF 与现有的 `src/parse_pdf.py` 处理的那份**结构不同**，不要试图复用。
新 PDF 是真表格（PyMuPDF `find_tables()` 能直接抽出四列：Key word / 中文 / English example / 例句中文），
章标题是页面上字号 ≥13、形如 `Motion / 运动` 的蓝色文本。三处坑：

1. **跨页续行**：`water displacement`、`atom`、`boiling` 三条的例句被页边界切成两行，
   第二行的首列为空。首列为空的行要并到上一条，`ex` 用空格拼、`exzh` 直接拼。
2. **章内重复**：`temperature` 和 `current` 各出现两次。保留定义性更强的一条 ——
   `temperature` 留「热学」章，`current` 留「电与磁」章，丢弃「测量与数据」章里的那条。
3. **最后一章不是词表**：`High-frequency answer patterns / 高频答题句型` 下面没有表格，
   解析结果为空章，要跳过（那 10 组句型在 Task 9 手录）。

- [ ] **Step 1: 写脚本骨架与自检**

创建 `src/parse_physics_pdf.py`：

```python
# -*- coding: utf-8 -*-
"""从《Cambridge IGCSE Physics 0625 核心词汇表》PDF 解析出结构化词表。

用法：python3 src/parse_physics_pdf.py <pdf 路径> > src/parsed_phy.json
     python3 src/parse_physics_pdf.py <pdf 路径> --selftest
依赖：PyMuPDF (pip install pymupdf)

与 parse_pdf.py 处理的那份 PDF 结构不同：这份是真表格，四栏
（Key word / 中文 / English example / 例句中文），章标题是字号 >=13 的
「English / 中文」蓝色文本。
"""
import fitz, json, sys

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
        for t in pg.find_tables().tables:
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
```

- [ ] **Step 2: 跑自检，确认它通过**

```bash
python3 src/parse_physics_pdf.py "/Users/bobmax/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/bob743439_6d65/temp/drag/Cambridge_IGCSE_Physics_Core_Vocabulary_中英例句词汇表.pdf" --selftest
```

Expected: `selftest OK — 11 章 162 词`

若报「应有 162 词」，先打印各章词数对照：题目指令词 12、测量与数据 17、运动 17、力 17、
能量功与功率 16、密度压强与流体 12、热学 10、波声音与光 15、电与磁 14、
原子核与空间物理 17、实验技能 15。

- [ ] **Step 3: 生成 parsed_phy.json**

```bash
python3 src/parse_physics_pdf.py "/Users/bobmax/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/bob743439_6d65/temp/drag/Cambridge_IGCSE_Physics_Core_Vocabulary_中英例句词汇表.pdf" > src/parsed_phy.json
```

- [ ] **Step 4: 验证跨页续行确实被合并**

```bash
python3 -c "
import json
d = json.load(open('src/parsed_phy.json'))
by = {it['w']: it for s in d['sections'] for it in s['items']}
for w in ['water displacement', 'atom', 'boiling']:
    print(w, '->', by[w]['ex'])
assert by['water displacement']['ex'].endswith('displacement.'), '续行没合上'
assert by['atom']['ex'].endswith('electrons.'), '续行没合上'
assert by['boiling']['ex'].endswith('liquid.'), '续行没合上'
print('OK')
"
```

Expected: 三条例句都是完整句、结尾有句点，最后打印 `OK`。

- [ ] **Step 5: 提交**

`src/parsed_phy.json` **要入库**（`.gitignore` 只排除了 `src/parsed.json`，不含 `parsed_phy.json`），
这样没有 PDF 也能重新构建。

```bash
git add src/parse_physics_pdf.py src/parsed_phy.json
git commit -m "$(cat <<'EOF'
feat: 解析物理 PDF 成结构化词表

四栏表格，处理跨页续行与 temperature/current 的章内重复。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: 构建链路改成两本书

**Files:**
- Modify: `src/build.py`（`build_data` / `enrich` / `check` / `attach_trans` / `__main__`）
- Create: `src/phon_phy.py`（本任务只建空壳，Task 8 填内容）
- Create: `src/frames_phy.py`（本任务只建空壳，Task 9 填内容）

**Interfaces:**
- Consumes: Task 1 的 `src/parsed_phy.json`
- Produces:
  - `src/data.json` 结构变为 `{"books": [...], "lessons": [...]}`，
    每本书 `{"id": "sci"|"phy", "cn": str, "credit": str, "sections": [...], "frames": [...]}`
  - 每个词条多出 `"id": "<bookId>:<w>"` 字段
  - `build.py` 暴露模块常量 `STRICT_PHON`（本任务为 `False`，Task 8 翻成 `True`）

**背景：两处必须先解决的坑**

1. **en dash**：`distance–time graph` 和 `speed–time graph` 里的 `–` 是 U+2013，
   不是 ASCII 连字符。现有 `check()` 的 `norm` 只剥 `-` 和空格，这两个词会被误判成
   「音节拼写与原词不符」。要把 `norm` 扩成同时剥 `–`（U+2013）和 `—`（U+2014）。
2. **占位音标**：Task 8 之前 `PHON` 缺 111 个物理词。让 `enrich` 在缺失时生成
   `拼写=?` 的占位音节（`check()` 仍会通过，因为拼写拼回原词是对的），并统计缺口。
   `STRICT_PHON = True` 时改为直接报错。

- [ ] **Step 1: 先建两个空壳数据文件**

`src/phon_phy.py`：

```python
# -*- coding: utf-8 -*-
"""物理词表独有词汇的音节切分与词根助记。

格式与 phon.py 完全一致：值是 (音节串, 助记) 二元组，
音节串写成「拼写=音标」，音节间用 |，短语中的词之间用 " / " 分隔。
与 phon.py 同名的词不在这里重复——音标一样，构建时直接复用。
"""
PHON_PHY = {}
```

`src/frames_phy.py`：

```python
# -*- coding: utf-8 -*-
"""物理的高频答题句型。字段与 data.json 里 frames 一致。"""
FRAMES_PHY = []
```

- [ ] **Step 2: 先加校验，让构建失败**

改 `src/build.py`。在 import 区加：

```python
from phon_phy import PHON_PHY               # noqa: E402
from trans import TRANS                     # 已有
from frames_phy import FRAMES_PHY           # noqa: E402
```

在 `from phon import PHON` 之后合并字典（物理独有词补进来，同名词沿用 phon.py 的）：

```python
PHON = {**PHON, **PHON_PHY}
```

新增两道校验函数：

```python
STRICT_PHON = False        # Task 8 填完 phon_phy.py 后翻成 True


def check_ids(data):
    """同一本书内 id 不能重复。这道会自动兜住 PDF 里同词出现两次那类问题。"""
    for bk in data['books']:
        seen = set()
        for s in bk['sections']:
            for w in s['words']:
                if w['id'] in seen:
                    raise SystemExit('%s 书内 id 重复: %s' % (bk['id'], w['id']))
                seen.add(w['id'])


def check_phon(data):
    """PHON 必须覆盖两本书的全部裸词。STRICT_PHON 之前只报缺口数。"""
    miss = sorted({w['w'] for bk in data['books']
                   for s in bk['sections'] for w in s['words']
                   if w['w'] not in PHON})
    if miss and STRICT_PHON:
        raise SystemExit('PHON 缺 %d 词: %s' % (len(miss), miss))
    if miss:
        print('  ⚠ 尚缺音标/助记 %d 词（占位中）: %s%s'
              % (len(miss), ', '.join(miss[:6]), ' …' if len(miss) > 6 else ''))
    return len(miss)
```

- [ ] **Step 3: 跑构建，确认它因为新结构而失败**

```bash
python3 src/build.py
```

Expected: FAIL —— `check_ids` 还没被调用、`data['books']` 还不存在，
应报 `KeyError: 'books'` 或 `NameError`。这一步只是确认改动确实生效、没有被旧缓存绕过。

- [ ] **Step 4: 改 enrich 与 check，支持 id、占位音标与 en dash**

替换 `src/build.py` 里的 `enrich` 和 `check`：

```python
def enrich(it, book):
    """给一个词条补上 id、音标、音节切分与助记。PHON 是唯一来源。

    PHON 尚未覆盖的词先给占位音节，让构建能跑通；check_phon 会报缺口，
    STRICT_PHON 打开后则直接失败。
    """
    if it['w'] in PHON:
        syl, tip = PHON[it['w']]
    else:
        syl, tip = ' / '.join('%s=?' % p for p in it['w'].split()), ''
    # "ob=ˌɒb|ser=zə" → [[{t:'ob',p:'ˌɒb'},…]]，词与词之间用 " / " 分隔
    sw = [[{'t': x.split('=')[0], 'p': x.split('=')[1]} for x in p.split('|')]
          for p in syl.split(' / ')]
    ipa = '/' + ' '.join(''.join(y['p'] for y in p) for p in sw) + '/'
    return {**it, 'id': '%s:%s' % (book, it['w']), 'ipa': ipa, 'syl': sw, 'tip': tip}


def check(data):
    """音节拼写拼回原词必须一致，否则说明 PHON 写错了"""
    # distance–time graph 用的是 en dash（U+2013），不是 ASCII 连字符，一并剥掉
    def norm(x):
        for c in ('-', '–', '—', ' '):
            x = x.replace(c, '')
        return x.lower()

    bad = []
    for bk in data['books']:
        for s in bk['sections']:
            for w in s['words']:
                rebuilt = ' '.join(''.join(y['t'] for y in p) for p in w['syl'])
                if norm(rebuilt) != norm(w['w']):
                    bad.append((w['id'], rebuilt))
    if bad:
        raise SystemExit('音节拼写与原词不符: %s' % bad)
    return sum(len(s['words']) for bk in data['books'] for s in bk['sections'])
```

- [ ] **Step 5: 改 build_data 产出两本书**

替换 `src/build.py` 的 `build_data`：

```python
SCI = {'id': 'sci', 'cn': '科学', 'credit': 'IGCSE 自然科学英语核心词汇表'}
PHY = {'id': 'phy', 'cn': '物理', 'credit': 'Cambridge IGCSE Physics 0625 核心词汇表'}


def build_sci():
    """现有词表：优先吃 parsed.json，没有就用 data.json 缓存里的 sci 书"""
    src = os.path.join(HERE, 'parsed.json')
    if not os.path.exists(src):
        cached = json.load(open(os.path.join(HERE, 'data.json'), encoding='utf-8'))
        bk = next(b for b in cached['books'] if b['id'] == 'sci')
        have = {w['w'] for s in bk['sections'] for w in s['words']}
        missing = [enrich(it, 'sci') for it in EXTRA['words'] if it['w'] not in have]
        if missing:
            bk['sections'].append({'id': len(bk['sections']) + 1,
                                   'cn': EXTRA['cn'], 'en': EXTRA['en'], 'words': missing})
        return bk

    d = json.load(open(src, encoding='utf-8'))
    secs, sid = [], 0
    for s in d['sections']:
        if not s['items']:
            continue
        body = re.match(r'^[一二三四五六七八九]、(.+)$', s['title']).group(1)
        m = re.search(r'(?<=[一-鿿])(?=[A-Za-z])', body)     # 中英文标题分界
        cn, en = (body[:m.start()].strip(), body[m.start():].strip()) if m else (body, '')
        sid += 1
        secs.append({'id': sid, 'cn': cn, 'en': en,
                     'words': [enrich(it, 'sci') for it in s['items']]})
    sid += 1                                   # 衔接课程带来的补充词汇单列一章
    secs.append({'id': sid, 'cn': EXTRA['cn'], 'en': EXTRA['en'],
                 'words': [enrich(it, 'sci') for it in EXTRA['words']]})
    return {**SCI, 'sections': secs, 'frames': d['frames']}


def build_phy():
    """物理词表：parsed_phy.json 是唯一来源，它已入库，不依赖 PDF"""
    d = json.load(open(os.path.join(HERE, 'parsed_phy.json'), encoding='utf-8'))
    secs = [{'id': i + 1, 'cn': s['cn'], 'en': s['en'],
             'words': [enrich(it, 'phy') for it in s['items']]}
            for i, s in enumerate(d['sections'])]
    return {**PHY, 'sections': secs, 'frames': FRAMES_PHY}


def build_data():
    # {**SCI, **book} 让缓存分支也一定带上最新的 cn / credit
    data = {'books': [{**SCI, **build_sci()}, build_phy()]}
    json.dump(data, open(os.path.join(HERE, 'data.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    return data
```

- [ ] **Step 6: 改 attach_trans 按书调用**

`attach_trans` 现在遍历 `data['sections']`，改成接收一本书：

```python
def attach_trans(book, TR):
    """把例句的翻译思路挂到指定的书上。独立于 build_data——直接吃缓存时也要生效。"""
    n, seen = 0, set()
    for s in book['sections']:
        for w in s['words']:
            if w['w'] in TR:
                w['tr'] = TR[w['w']]; n += 1; seen.add(w['w'])
            else:
                w.pop('tr', None)                  # 标注被删掉时同步清掉
    unknown = set(TR) - seen
    if unknown:
        raise SystemExit('%s 的 trans 里有词表中不存在的词条: %s'
                         % (book['id'], sorted(unknown)))
    missing = [w['w'] for s in book['sections'] for w in s['words'] if 'tr' not in w]
    if missing:
        print('  ⚠ %s 尚缺翻译思路 %d 条: %s%s'
              % (book['id'], len(missing), ', '.join(missing[:6]),
                 ' …' if len(missing) > 6 else ''))
    for w, t in TR.items():                        # 结构自检
        for k in ('pat', 'flow', 'core', 'final', 'tip'):
            if k not in t:
                raise SystemExit('%s 缺字段 %s' % (w, k))
        if any(len(x) != 3 for x in t['flow']):
            raise SystemExit('%s 的 flow 每项要写成 [英文, 中文, 成分]' % w)
    # final 各段拼起来必须与原书译文完全一致，防止标注时漏字或改写
    for s in book['sections']:
        for w in s['words']:
            if 'tr' not in w:
                continue
            joined = ''.join(seg[0] for seg in w['tr']['final'])
            if re.sub(r'\s+', '', joined) != re.sub(r'\s+', '', w['exzh']):
                raise SystemExit('%s 的 final 拼接与译文不符:\n  %s\n  %s'
                                 % (w['id'], joined, w['exzh']))
    return n
```

- [ ] **Step 7: 改 `__main__` 串起来**

```python
if __name__ == '__main__':
    data = build_data()
    n = check(data)
    check_ids(data)
    nmiss = check_phon(data)
    books = {b['id']: b for b in data['books']}
    ntr = attach_trans(books['sci'], TRANS)
    ntr += attach_trans(books['phy'], TRANS_PHY)
    nles = attach_lessons(data)
    tpl = open(os.path.join(HERE, 'tpl.html'), encoding='utf-8').read()
    assert '__DATA__' in tpl, 'tpl.html 缺少 __DATA__ 占位符'
    assert '__BASE__' in tpl, 'tpl.html 缺少 __BASE__ 占位符'
    assert BASE.endswith('/'), 'BASE 末尾要有斜杠'
    html = (tpl.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
               .replace('__LOGO_URI__', logo_data_uri())      # 顺序要紧：先换 URI，再换裸 SVG
               .replace('__LOGO__', logo_svg())
               .replace('__BASE__', BASE)
               .replace('__N__', str(n)))
    dst = os.path.join(ROOT, 'index.html')
    open(dst, 'w', encoding='utf-8').write(html)
    print('built %s — %d 词（%d 句带翻译思路，%d 词缺音标）, %d 节预习, %d KB'
          % (dst, n, ntr, nmiss, nles, round(os.path.getsize(dst) / 1024)))
```

本任务里 `TRANS_PHY` 还不存在，先在 import 区加一行空壳兜底：

```python
try:
    from trans_phy import TRANS_PHY          # noqa: E402  Task 10 才填
except ImportError:
    TRANS_PHY = {}
```

`attach_lessons` 暂时会因为 `data['sections']` 不存在而报错 —— 那是 Task 3 的事，
本任务先把它改成读 books 的最小版本：

```python
def attach_lessons(data):
    """课时里引用的词必须在词库中查得到，否则「开始学这些词」会点空"""
    have = {w['id'] for bk in data['books'] for s in bk['sections'] for w in s['words']}
    for les in LESSONS:
        miss = [v[0] for v in les['vocab'] if 'sci:' + v[0] not in have]
        if miss:
            raise SystemExit('第 %s 节引用了词库中不存在的词: %s' % (les['id'], miss))
    data['lessons'] = LESSONS
    return len(LESSONS)
```

- [ ] **Step 8: 跑构建，确认通过并报出缺口**

因为 `src/parsed.json` 不存在（`.gitignore` 排除了），`build_sci()` 会走缓存分支，
但缓存里还是旧结构。**先删掉旧缓存让它从 parsed 重建是不行的**（没有原 PDF），
所以要一次性把旧 `data.json` 迁成新结构：

```bash
python3 -c "
import json
p = 'src/data.json'
d = json.load(open(p, encoding='utf-8'))
if 'books' in d: raise SystemExit('已经是新结构，无需迁移')
for s in d['sections']:
    for w in s['words']:
        w['id'] = 'sci:' + w['w']
out = {'books': [{'id':'sci','cn':'科学','credit':'IGCSE 自然科学英语核心词汇表',
                  'sections': d['sections'], 'frames': d['frames']}]}
json.dump(out, open(p,'w',encoding='utf-8'), ensure_ascii=False, separators=(',',':'))
print('data.json 已迁到 books 结构')
"
python3 src/build.py
```

Expected: 构建成功，输出形如
`built …/index.html — 332 词（170 句带翻译思路，111 词缺音标）, 1 节预习, … KB`

关键数字：**332 词**、**111 词缺音标**。对不上就停下来查，不要往下做。

- [ ] **Step 9: 验证 id 与 books 结构**

```bash
python3 -c "
import json
d = json.load(open('src/data.json', encoding='utf-8'))
assert [b['id'] for b in d['books']] == ['sci','phy'], d['books'][0].keys()
n = {b['id']: sum(len(s['words']) for s in b['sections']) for b in d['books']}
assert n == {'sci':170,'phy':162}, n
ids = [w['id'] for b in d['books'] for s in b['sections'] for w in s['words']]
assert len(ids) == len(set(ids)) == 332, (len(ids), len(set(ids)))
assert 'sci:pressure' in ids and 'phy:pressure' in ids
by = {w['id']: w for b in d['books'] for s in b['sections'] for w in s['words']}
assert by['phy:distance–time graph']['syl'], 'en dash 词条没生成'
print('OK', n)
"
```

Expected: `OK {'sci': 170, 'phy': 162}`

- [ ] **Step 10: 提交**

```bash
git add src/build.py src/phon_phy.py src/frames_phy.py src/data.json
git commit -m "$(cat <<'EOF'
feat: 构建链路改成两本词书，词条补稳定 id

data.json 顶层变 books，每词 id 为 <book>:<word>。新增同书内 id 唯一、
PHON 覆盖两道校验；音节比对同时剥 en dash，物理缺的 111 词先走占位音标。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: 课时归属与跨书取词

**Files:**
- Modify: `src/lessons.py:27-55`（第 3 节的头部字段与 `vocab`）
- Modify: `src/lessons.py:1-26`（模块 docstring 里的字段说明）
- Modify: `src/build.py`（`attach_lessons`）

**Interfaces:**
- Consumes: Task 2 的 `data['books']` 与词条 `id`
- Produces: `LESSONS` 每条多出 `"book": "sci"|"phy"`；`vocab` 项的第一个元素
  可写成 `"sci:diffusion"`（带前缀跨书引用）或 `"pressure"`（不带前缀＝本课所属书）

**背景：** 衔接课程有两门（化学、物理）。第 3 节「扩散、布朗运动与气体规律」属于**物理**那门。
它的 12 个词横跨两本：`pressure` / `volume` / `kinetic energy` / `temperature` 在物理书里
（例句是物理语境，更对路），`diffusion` / `Brownian motion` / `concentration` / `collision` /
`random` / `net movement` / `relative molecular mass` 只在科学书里。

- [ ] **Step 1: 先加校验，让构建失败**

改 `src/build.py` 的 `attach_lessons`：

```python
def attach_lessons(data):
    """课时里引用的词必须在词库中查得到，否则「开始学这些词」会点空。

    vocab 的词可写成 "sci:diffusion" 跨书引用；不带前缀就按课时自己的 book 解析。
    """
    have = {w['id'] for bk in data['books'] for s in bk['sections'] for w in s['words']}
    ids = {b['id'] for b in data['books']}
    for les in LESSONS:
        if les.get('book') not in ids:
            raise SystemExit('第 %s 节的 book 字段应为 %s，实为 %r'
                             % (les['id'], sorted(ids), les.get('book')))
        miss = []
        for v in les['vocab']:
            wid = v[0] if ':' in v[0] else '%s:%s' % (les['book'], v[0])
            if wid not in have:
                miss.append(wid)
        if miss:
            raise SystemExit('第 %s 节引用了词库中不存在的词: %s' % (les['id'], miss))
    data['lessons'] = LESSONS
    return len(LESSONS)
```

- [ ] **Step 2: 跑构建，确认它失败**

```bash
python3 src/build.py
```

Expected: FAIL —— `第 3 节的 book 字段应为 ['phy', 'sci']，实为 None`

- [ ] **Step 3: 改 lessons.py 的第 3 节**

把 `src/lessons.py` 第 3 节开头的字段改成（`course` 从化学改为物理）：

```python
{
    "id": 3,
    "book": "phy",
    "title": "扩散、布朗运动与气体规律",
    "course": "Cambridge IGCSE Physics 0625 衔接课程",
    "mins": 20,
```

`vocab` 整块替换为（只在科学书里的 7 个词加 `sci:` 前缀）：

```python
    "vocab": [
        ["sci:diffusion",               "粒子总体由高浓度区域向低浓度区域移动"],
        ["sci:Brownian motion",         "悬浮微粒受到分子不规则碰撞产生的随机运动"],
        ["sci:random",                  "方向不断变化、没有固定路线"],
        ["sci:concentration",           "一定空间中粒子的多少"],
        ["sci:high concentration",      "单位空间内粒子较多"],
        ["sci:low concentration",       "单位空间内粒子较少"],
        ["sci:net movement",            "综合所有随机运动后呈现的总体方向"],
        ["sci:collision",               "粒子相互撞击"],
        ["kinetic energy",              "物体或粒子由于运动具有的能量"],
        ["sci:relative molecular mass", "一个分子中各原子相对质量的总和"],
        ["pressure",                    "粒子碰撞容器壁产生的作用"],
        ["volume",                      "物质或气体占据的空间"],
    ],
```

- [ ] **Step 4: 更新模块 docstring**

`src/lessons.py` 顶部字段说明里，`id` 那行下面加一行，`vocab` 那段改写：

```
  id       课时序号
  book     这节课属于哪本词书："sci" 科学 / "phy" 物理
  ...
  vocab    重点词汇：[英文, 理解提示]。英文写成 "sci:diffusion" 可跨书引用，
           不带前缀就按本课的 book 解析。构建时会校验能否查到；
           点进去直接进闪卡流程
```

- [ ] **Step 5: 跑构建，确认通过**

```bash
python3 src/build.py
```

Expected: 成功，`1 节预习`

- [ ] **Step 6: 验证跨书引用解析正确**

```bash
python3 -c "
import json
d = json.load(open('src/data.json', encoding='utf-8'))
have = {w['id'] for b in d['books'] for s in b['sections'] for w in s['words']}
import sys; sys.path.insert(0,'src')
from lessons import LESSONS
les = LESSONS[0]
assert les['book'] == 'phy', les['book']
ids = [v[0] if ':' in v[0] else les['book']+':'+v[0] for v in les['vocab']]
assert all(i in have for i in ids), [i for i in ids if i not in have]
assert sum(1 for i in ids if i.startswith('sci:')) == 7, ids
assert sum(1 for i in ids if i.startswith('phy:')) == 5, ids
print('OK 跨书 7 + 本书 5')
"
```

Expected: `OK 跨书 7 + 本书 5`

- [ ] **Step 7: 提交**

```bash
git add src/lessons.py src/build.py src/data.json
git commit -m "$(cat <<'EOF'
feat: 课时按书归属，vocab 支持跨书引用

第 3 节归到物理衔接课程；只在科学书里的 7 个词写成 sci: 前缀，
其余 5 个用物理书自己的词条，例句更贴物理语境。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: 前端数据索引与进度迁移

**Files:**
- Modify: `src/tpl.html:658-708`（数据索引、存储、间隔重复判定）
- Modify: `src/tpl.html:1277,1288,1382-1383`（卡片学习里的进度读写）
- Modify: `src/tpl.html:1422`（页头副标题）

**Interfaces:**
- Produces（后续任务都依赖这些全局量）：
  - `BOOKS`：`{sci: <book>, phy: <book>}`
  - `curBook()` → 当前 book 对象；`curWords()` → 当前书的词条数组
  - `BY_ID`：`{'<book>:<word>': <词条>}`，跨全部书
  - `S.set.book`：`'sci' | 'phy'`，默认 `'sci'`
  - `dueCount(bookId)` → number，指定书的到期词数
  - 词条上新增 `w.book`（所属书 id）、沿用 `w.sec` / `w.secName`

**背景：** `S.prog` 现在按裸词存。51 个同名词会互相覆盖，必须改按 `w.id`。
老用户的 localStorage 里全是裸词 key，`load()` 要一次性加 `sci:` 前缀。

- [ ] **Step 1: 换掉数据索引（`tpl.html:658-663`）**

原来：

```js
/* ===================== 数据索引 ===================== */
const ALL = [];
DATA.sections.forEach(s => s.words.forEach(w => {
  w.sec = s.id; w.secName = s.cn; ALL.push(w);
}));
const BY_W = Object.fromEntries(ALL.map(w => [w.w, w]));
```

替换为：

```js
/* ===================== 数据索引 ===================== */
const BOOKS = {};
DATA.books.forEach(bk => {
  bk.words = [];
  bk.sections.forEach(s => s.words.forEach(w => {
    w.book = bk.id; w.sec = s.id; w.secName = s.cn; bk.words.push(w);
  }));
  BOOKS[bk.id] = bk;
});
const BOOK_IDS = DATA.books.map(b => b.id);
const BY_ID = Object.fromEntries(
  DATA.books.flatMap(bk => bk.words.map(w => [w.id, w])));
const curBook = () => BOOKS[S.set.book] || BOOKS[BOOK_IDS[0]];
const curWords = () => curBook().words;
```

注意 `curBook` 用到 `S`，而 `S` 在下一段才定义 —— 因为它是箭头函数、调用时才求值，
没有时序问题；但**不要**改成在这里就求值的常量。

- [ ] **Step 2: 存储加 book 字段与迁移（`tpl.html:665-681`）**

`DEF.set` 加 `book: 'sci'`：

```js
  set: { rate: .95, voice: '', autoSpeak: true, sylMode: 'respell', maskZh: false, theme: 'light', book: 'sci' }
```

`load()` 换成：

```js
function load() {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) || '{}');
    const S = { prog: raw.prog || {}, les: raw.les || {},
                set: Object.assign({}, DEF.set, raw.set || {}) };
    // 旧版进度按裸词存，两本词书上线后改按 <book>:<word>。裸 key 一律归到科学书。
    let moved = 0;
    for (const k of Object.keys(S.prog)) {
      if (k.includes(':')) continue;
      S.prog['sci:' + k] = S.prog[k]; delete S.prog[k]; moved++;
    }
    if (moved) { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} }
    if (!BOOKS[S.set.book]) S.set.book = BOOK_IDS[0];
    return S;
  } catch (e) { return JSON.parse(JSON.stringify(DEF)); }
}
```

- [ ] **Step 3: 进度判定改用 id（`tpl.html:698-708`）**

```js
function grade(id, g) {
  const r = rec(id); r.seen++;
  if (g === 0) { r.box = 0; r.wrong++; }
  else if (g === 1) { r.box = Math.min(Math.max(r.box, 1), 3); }   // 模糊：至少 10 分钟后再来
  else { r.box = Math.min(5, r.box + 1); }
  r.due = Date.now() + STEP[r.box];
  save();
}
const isDue = w => { const r = S.prog[w.id]; return r && r.seen > 0 && r.due <= Date.now(); };
const isNew = w => !S.prog[w.id] || !S.prog[w.id].seen;
const isMastered = w => (S.prog[w.id]?.box || 0) >= 4;
const dueCount = b => BOOKS[b].words.filter(isDue).length;
```

- [ ] **Step 4: 卡片学习里的三处（`tpl.html:1277,1288,1382-1383`）**

```js
  const r = rec(Q[qi].id); r.star = r.star ? 0 : 1; save();
```

```js
  $('stStar').classList.toggle('star-on', !!S.prog[w.id]?.star);
```

```js
  const g = +b.dataset.g, w = Q[qi];
  grade(w.id, g);
  if (g === 0 && !requeued.has(w.id)) { requeued.add(w.id); Q.push(w); }   // 忘记的词本轮末尾再出现一次
```

- [ ] **Step 5: 页头副标题（`tpl.html:1422`）**

```js
$('hdS').textContent = `${Object.values(BOOKS).reduce((n, b) => n + b.words.length, 0)} 词 · 音标 · 拆音节 · 朗读`;
```

- [ ] **Step 6: 把剩余的 `ALL` / `BY_W` 引用机械替换掉**

**只换引用，不动任何布局或文案** —— 界面在本任务结束时必须和改动前长得一模一样。
先加两个解析课时词的辅助函数，放在 `/* ---------- 首页 ---------- */` 注释之前：

```js
/* vocab 的词可写成 "sci:diffusion" 跨书引用，不带前缀就按本课的 book 解析 */
const lessonWordId = (les, w) => w.includes(':') ? w : `${les.book}:${w}`;
const lessonWords = les => les.vocab.map(([w]) => BY_ID[lessonWordId(les, w)]).filter(Boolean);
```

然后逐处替换：

**`renderHome`（约 957-1015 行）**——在函数第一行加 `const W = curWords();`，
把函数体里所有 `ALL` 换成 `W`，并把三处进度读取换成 id：

```js
    const q = W.filter(isDue).sort((a, b) => S.prog[a.id].due - S.prog[b.id].due);
```

```js
    const q = W.filter(w => (S.prog[w.id]?.wrong || 0) > 0 || S.prog[w.id]?.star)
      .sort((a, b) => (S.prog[b.id].wrong || 0) - (S.prog[a.id].wrong || 0));
```

**`lessonSectionHTML`（约 1184 行）**：`les.vocab.map(([w]) => BY_W[w]).filter(Boolean)`
→ `lessonWords(les)`。**本任务不加按书过滤**——分段控件要到 Task 5 才有，
这里过滤会让物理那节课没有入口。

**预习详情页**：`const words = les.vocab.map(([w]) => BY_W[w]).filter(Boolean);`
→ `const words = lessonWords(les);`；`const it = BY_W[w];`
→ `const it = BY_ID[lessonWordId(les, w)];`；该页词条行的
`data-w="${esc(w.w)}"` → `data-w="${esc(w.id)}"`，对应的
`startStudy([BY_W[row.dataset.w]], …)` → `startStudy([BY_ID[row.dataset.w]], …)`。

**`renderList`（约 1044、1046、1066 行）**：`S.prog[w.w]` → `S.prog[w.id]`；
`data-w="${esc(w.w)}"` → `data-w="${esc(w.id)}"`；
`startStudy([BY_W[r.dataset.w]], '单词')` → `startStudy([BY_ID[r.dataset.w]], '单词')`。

**`renderMe`（约 1214、1248、1261 行）**：函数第一行加 `const W = curWords();`，
`ALL` 全换成 `W`，`S.prog[w.w]` → `S.prog[w.id]`，
`BY_W['photosynthesis']` → `BY_ID['sci:photosynthesis']`。

替换完用这条确认没有遗漏：

```bash
grep -n "BY_W\|\bALL\b" src/tpl.html
```

Expected: 无输出。

- [ ] **Step 7: 构建并在浏览器里验证迁移**

```bash
python3 src/build.py
```

然后 `preview_start {name: "flashcard"}`，导航到 `http://localhost:8777/index.html`。
**先注入一份旧格式进度**再刷新，验证迁移：

用 `javascript_tool` 执行：

```js
localStorage.setItem('igcse-flashcard-v1', JSON.stringify({
  prog: { 'pressure': {box:3,due:0,seen:5,wrong:1,star:1},
          'photosynthesis': {box:5,due:0,seen:9,wrong:0,star:0} },
  les: {}, set: { theme: 'light' }
}));
location.reload(); 'reloaded'
```

刷新后再执行：

```js
const p = JSON.parse(localStorage.getItem('igcse-flashcard-v1')).prog;
JSON.stringify({
  keys: Object.keys(p),
  migrated: !!p['sci:pressure'] && !!p['sci:photosynthesis'] && !p['pressure'],
  box: p['sci:pressure'].box,
  book: JSON.parse(localStorage.getItem('igcse-flashcard-v1')).set.book,
  total: Object.values(BOOKS).reduce((n,b)=>n+b.words.length,0),
  byId: !!BY_ID['phy:pressure'] && !!BY_ID['sci:pressure']
})
```

Expected: `migrated: true`、`box: 3`、`book: "sci"`、`total: 332`、`byId: true`，
且 `keys` 里没有裸词。

再执行一次 `location.reload()` 后重跑上面的断言，确认**幂等**（第二次不会再动数据）。

再确认界面没被这次重构改坏 —— 本任务不应有任何肉眼可见的变化：

```js
JSON.stringify({
  chap: document.querySelectorAll('.chap').length,        // 章节卡 + 预习卡
  err: (() => { try { renderList(); renderMe(); renderHome(); return null } catch (e) { return e.message } })(),
  study: (() => { document.querySelector('[data-sec]').click();
                  const on = document.getElementById('study').classList.contains('on');
                  document.getElementById('stClose').click(); return on })()
})
```

Expected: `chap: 10`（9 章 + 1 节预习）、`err: null`、`study: true`。
浏览器控制台（`read_console_messages`）应无报错。

- [ ] **Step 8: 提交**

```bash
git add src/tpl.html index.html
git commit -m "$(cat <<'EOF'
refactor: 进度改按 <book>:<word> 存，旧数据一次性迁移

BY_W 换成跨书的 BY_ID，ALL 换成 curWords()，课时词统一走 lessonWordId 解析。
裸词 key 全部归到科学书，迁移幂等。界面外观不变。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: 学习页 —— 科目切换与章节网格

**Files:**
- Modify: `src/tpl.html`（在 `.chap` 规则之后、`/* ---------- 学习卡 ---------- */` 之前插入新 CSS）
- Modify: `src/tpl.html:956-1023`（`renderHome`）
- Modify: `src/tpl.html:1178-1196`（`lessonSectionHTML`）

**Interfaces:**
- Consumes: Task 4 的 `BOOKS` / `curBook()` / `curWords()` / `dueCount()` / `S.set.book`
- Produces: `bookBarHTML()` → string（三页共用的分段控件）；
  `bindBookBar()` → void（绑定切换事件，供词表页与句型页复用）

- [ ] **Step 1: 加 CSS**

在 `src/tpl.html` 的 `.chap .n{…}` 那行之后插入：

```css
/* ---------- 科目切换 ---------- */
.bookbar{
  display:flex;gap:4px;padding:4px;margin-top:4px;
  background:var(--color-background-muted);border-radius:var(--radius-full);
}
.bookbar button{
  flex:1;border:0;background:none;font-family:inherit;color:var(--color-text-secondary);
  font-size:var(--font-size-base);font-weight:var(--font-weight-medium);
  padding:8px 0;border-radius:var(--radius-full);
  display:flex;align-items:center;justify-content:center;gap:6px;
  transition:background var(--duration-fast) var(--ease-standard);
}
.bookbar button.on{
  background:var(--color-background-card);color:var(--color-text-primary);
  font-weight:var(--font-weight-semibold);box-shadow:var(--shadow-low);
}
.bookbar .due{
  display:inline-flex;align-items:center;justify-content:center;min-width:17px;height:17px;
  padding:0 5px;border-radius:var(--radius-full);background:var(--color-error);
  color:#fff;font-size:var(--font-size-xs);font-weight:var(--font-weight-semibold);
  font-variant-numeric:tabular-nums;
}

/* ---------- 章节网格 ---------- */
.grid{display:grid;grid-template-columns:1fr 1fr;gap:var(--spacing-2)}
.gcard{
  padding:var(--spacing-3);text-align:left;color:inherit;font-family:inherit;
  display:flex;flex-direction:column;min-height:104px;overflow:hidden;
  transition:transform var(--duration-fast) var(--ease-standard);
}
.gcard:active{transform:scale(.97)}
.gcard .no{
  flex:0 0 auto;width:22px;height:22px;border-radius:var(--radius-inner);
  background:var(--color-accent);color:var(--color-on-accent);
  display:flex;align-items:center;justify-content:center;
  font-size:var(--font-size-sm);font-weight:var(--font-weight-semibold);
}
.gcard .t{
  font-weight:var(--font-weight-semibold);font-size:var(--font-size-base);
  line-height:1.25;margin-top:9px;
}
.gcard .e{
  font-size:var(--font-size-xs);color:var(--color-text-secondary);margin-top:2px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}
.gcard .n{
  margin-top:auto;padding-top:6px;font-size:var(--font-size-sm);
  color:var(--color-text-secondary);font-variant-numeric:tabular-nums;
}
/* 细条不做满宽——满宽会在卡片圆角处切出方角 */
.gcard .bar{height:3px;margin-top:7px}
```

- [ ] **Step 2: 加分段控件的公共函数**

在 `/* ---------- 首页 ---------- */` 注释之前插入：

```js
/* ---------- 科目切换（学习 / 词表 / 句型 三页共用） ---------- */
function bookBarHTML() {
  return `<div class="bookbar">` + DATA.books.map(bk => {
    const on = bk.id === S.set.book ? ' on' : '';
    const d = bk.id === S.set.book ? 0 : dueCount(bk.id);
    return `<button class="bk${on}" data-bk="${bk.id}">${esc(bk.cn)}${
      d ? `<span class="due">${d}</span>` : ''}</button>`;
  }).join('') + `</div>`;
}
function switchBook(id) {
  if (!BOOKS[id] || id === S.set.book) return;
  S.set.book = id; save(); view.scrollTop = 0; render();
}
function bindBookBar() {
  view.querySelectorAll('.bk').forEach(b => b.onclick = () => switchBook(b.dataset.bk));
}
```

- [ ] **Step 3: 重写 renderHome**

把 `src/tpl.html:957-1023` 的 `renderHome` 整个替换为：

```js
function renderHome() {
  const bk = curBook(), W = bk.words;
  const done = W.filter(isMastered).length;
  const due = W.filter(isDue).length;
  const started = W.filter(w => !isNew(w)).length;
  const pct = Math.round(done / W.length * 100);
  const C = 2 * Math.PI * 35;
  view.innerHTML = `
  ${bookBarHTML()}

  <div class="card panel dash" style="margin-top:12px">
    <div class="ring">
      <svg width="86" height="86">
        <circle class="track" cx="43" cy="43" r="35" fill="none" stroke-width="7"/>
        ${done ? `<circle cx="43" cy="43" r="35" fill="none" stroke="var(--color-accent)" stroke-width="7" stroke-linecap="round"
          stroke-dasharray="${C}" stroke-dashoffset="${C * (1 - done / W.length)}"/>` : ''}
      </svg>
      <div class="num"><b>${pct}%</b><span>已掌握</span></div>
    </div>
    <div class="stat">
      <div><i style="background:var(--color-success)"></i><b>${done}</b><span>已掌握</span></div>
      <div><i style="background:var(--color-warning)"></i><b>${started - done}</b><span>学习中</span></div>
      <div><i style="background:var(--color-track)"></i><b>${W.length - started}</b><span>未学习</span></div>
    </div>
  </div>

  <div class="sec-t">今日任务</div>
  <button class="btn pri blk" id="goDue">${due ? `开始复习 · ${due} 词到期` : '暂无到期复习，去学新词 →'}</button>
  <div class="chipbar" style="margin-top:8px">
    <button class="btn line" id="goNew" style="flex:1">学新词 20</button>
    <button class="btn line" id="goHard" style="flex:1">难词本</button>
    <button class="btn line" id="goAll" style="flex:1">全部乱序</button>
  </div>

  ${lessonSectionHTML()}

  <div class="sec-t">按主题学习 · ${bk.sections.length} 章 / ${W.length} 词</div>
  <div class="grid">${bk.sections.map(s => {
    const d = s.words.filter(isMastered).length;
    return `<button class="card gcard" data-sec="${s.id}">
      <div class="no">${s.id}</div>
      <div class="t">${esc(s.cn)}</div>
      <div class="e">${esc(s.en)}</div>
      <div class="n">${d}/${s.words.length}</div>
      <div class="bar"><i style="width:${d / s.words.length * 100}%"></i></div>
    </button>`;
  }).join('')}</div>
  <div class="credit">词表来源：${esc(bk.credit)}</div>`;

  bindBookBar();
  $('goDue').onclick = () => {
    const q = W.filter(isDue).sort((a, b) => S.prog[a.id].due - S.prog[b.id].due);
    startStudy(q.length ? q : shuffle(W.filter(isNew)).slice(0, 20), '今日复习');
  };
  $('goNew').onclick = () => startStudy(W.filter(isNew).slice(0, 20), '新词');
  $('goHard').onclick = () => {
    const q = W.filter(w => (S.prog[w.id]?.wrong || 0) > 0 || S.prog[w.id]?.star)
      .sort((a, b) => (S.prog[b.id].wrong || 0) - (S.prog[a.id].wrong || 0));
    q.length ? startStudy(q, '难词本') : toast('还没有标记的难词');
  };
  $('goAll').onclick = () => startStudy(shuffle(W.slice()), '全部乱序');
  view.querySelectorAll('[data-sec]').forEach(b => b.onclick = () => {
    const s = bk.sections.find(x => x.id == b.dataset.sec);
    startStudy(s.words.slice(), s.cn);
  });
  view.querySelectorAll('[data-les]').forEach(b => b.onclick = () => {
    lesId = +b.dataset.les; view.scrollTop = 0; render();
  });
}
```

- [ ] **Step 4: 预习段按书过滤，并支持跨书取词**

`lessonSectionHTML`（`tpl.html:1179`）替换为：

```js
/* 首页里的「课前预习」一段，只显示属于当前书的课时 */
function lessonSectionHTML() {
  const L = (DATA.lessons || []).filter(l => l.book === S.set.book);
  if (!L.length) return '';
  return `<div class="sec-t">课前预习 · ${L.length} 节</div>` +
    L.map(les => {
      const ws = lessonWords(les);
      const d = ws.filter(isMastered).length;
      return `<button class="card chap lcard" data-les="${les.id}">
        <div class="no">${les.id}</div>
        <div class="bd">
          <div class="t">${esc(les.title)}</div>
          <div class="e">${ws.length} 词 · ${les.reading.length} 段阅读 · 约 ${les.mins} 分钟</div>
          <div class="bar"><i style="width:${d / ws.length * 100}%"></i></div>
        </div>
        <div class="n">${d}/${ws.length}</div>
      </button>`;
    }).join('');
}
```

本任务对这个函数**只加第一行的 `.filter(l => l.book === S.set.book)`** ——
`lessonWords` / `lessonWordId` 已在 Task 4 建好，不要重复定义。

- [ ] **Step 5: 构建并验证**

```bash
python3 src/build.py
```

浏览器里（`http://localhost:8777/index.html`，先 `localStorage.clear()` 再刷新），
用 `javascript_tool` 断言：

```js
const v = document.getElementById('view');
JSON.stringify({
  bar: !!document.querySelector('.bookbar'),
  tabs: [...document.querySelectorAll('.bk')].map(b => b.textContent),
  cards: document.querySelectorAll('.gcard').length,
  cols: getComputedStyle(document.querySelector('.grid')).gridTemplateColumns.split(' ').length,
  bars: document.querySelectorAll('.gcard .bar').length,
  rings: document.querySelectorAll('.gcard svg').length,
  screens: +(v.scrollHeight / v.clientHeight).toFixed(2)
})
```

Expected: `bar: true`、`tabs: ["科学","物理"]`、`cards: 9`、`cols: 2`、
`bars: 9`、`rings: 0`、`screens ≤ 2.1`

再切到物理书并复核：

```js
document.querySelector('.bk[data-bk=phy]').click();
const v = document.getElementById('view');
JSON.stringify({
  cards: document.querySelectorAll('.gcard').length,
  lesson: !!document.querySelector('[data-les]'),
  credit: document.querySelector('.credit').textContent,
  screens: +(v.scrollHeight / v.clientHeight).toFixed(2)
})
```

Expected: `cards: 11`、`lesson: true`（预习归物理）、
`credit` 含「Cambridge IGCSE Physics 0625」、`screens ≤ 2.5`

- [ ] **Step 6: 出图存档**

`resize_window {preset: "mobile"}` 后 `computer {action: "screenshot"}`，
浅色/深色各一张，确认细条与红点角标对比度正常。

- [ ] **Step 7: 提交**

```bash
git add src/tpl.html index.html
git commit -m "$(cat <<'EOF'
feat: 学习页加科目切换，章节卡改 2 列网格

11 章从 11 屏高收到 6 行网格，进度用卡底内缩细条。预习段按书过滤，
vocab 跨书引用统一走 lessonWordId 解析。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: 左右滑动切换科目

**Files:**
- Modify: `src/tpl.html`（在 `/* ===================== 杂项 ===================== */` 之前插入）

**Interfaces:**
- Consumes: Task 5 的 `switchBook()`、`BOOK_IDS`、`S.set.book`

**背景：** 卡片学习页已有一套同款手势（`tpl.html:1397`，阈值 55px、`|dx| > |dy| × 1.6`），
照抄它的判定，保持两处手感一致。`#study` 是 `position:fixed` 的独立覆盖层，
手势挂在 `main#view` 上不会互相触发。预习**详情**页也在 `#view` 里，
在那儿滑动切科目会让人莫名其妙，所以 `lesId != null` 时不响应。

- [ ] **Step 1: 加手势**

```js
/* 学习 / 词表 / 句型 三页左右滑动切换科目。判定与卡片页保持一致 */
let vx = 0, vy = 0;
view.addEventListener('touchstart', e => {
  vx = e.touches[0].clientX; vy = e.touches[0].clientY;
}, { passive: true });
view.addEventListener('touchend', e => {
  if (curView === 'me' || lesId != null) return;      // 设置页与预习详情页不参与
  const dx = e.changedTouches[0].clientX - vx, dy = e.changedTouches[0].clientY - vy;
  if (Math.abs(dx) < 55 || Math.abs(dx) < Math.abs(dy) * 1.6) return;
  const i = BOOK_IDS.indexOf(S.set.book) + (dx < 0 ? 1 : -1);
  if (i >= 0 && i < BOOK_IDS.length) switchBook(BOOK_IDS[i]);   // 到头不循环
}, { passive: true });
```

- [ ] **Step 2: 构建并验证**

```bash
python3 src/build.py
```

浏览器里用 `javascript_tool` 合成触摸事件（`computer` 的 swipe 走的是鼠标，
触发不了 `touchstart`）：

```js
function swipe(dx, dy) {
  const v = document.getElementById('view');
  const mk = (t, x, y) => new TouchEvent(t, { bubbles: true,
    [t === 'touchend' ? 'changedTouches' : 'touches']:
      [new Touch({ identifier: 1, target: v, clientX: x, clientY: y })] });
  v.dispatchEvent(mk('touchstart', 200, 400));
  v.dispatchEvent(mk('touchend', 200 + dx, 400 + dy));
}
const before = S.set.book;
swipe(-120, 5);  const afterLeft = S.set.book;
swipe(120, 5);   const afterRight = S.set.book;
swipe(120, 5);   const atHead = S.set.book;      // 已在第一本，不应循环
swipe(-30, 5);   const tooShort = S.set.book;    // 位移不够，不应切
swipe(-120, 90); const tooSlanted = S.set.book;  // 太斜，不应切
JSON.stringify({ before, afterLeft, afterRight, atHead, tooShort, tooSlanted })
```

Expected: `{"before":"sci","afterLeft":"phy","afterRight":"sci","atHead":"sci","tooShort":"sci","tooSlanted":"sci"}`

再验证卡片学习页的滑动没被影响：点任一章节进入卡片流，左滑应切下一张卡而不是切科目。

```js
document.querySelector('.gcard').click();
const q0 = document.getElementById('stPg').textContent;
const cw = document.querySelector('.cardwrap');
const mk = (t, x) => new TouchEvent(t, { bubbles: true,
  [t === 'touchend' ? 'changedTouches' : 'touches']:
    [new Touch({ identifier: 1, target: cw, clientX: x, clientY: 400 })] });
cw.dispatchEvent(mk('touchstart', 200)); cw.dispatchEvent(mk('touchend', 60));
JSON.stringify({ before: q0, after: document.getElementById('stPg').textContent, book: S.set.book })
```

Expected: `after` 的序号比 `before` 大 1，`book` 不变。

- [ ] **Step 3: 提交**

```bash
git add src/tpl.html index.html
git commit -m "$(cat <<'EOF'
feat: 三页支持左右滑动切换科目

判定沿用卡片页的 55px / |dx|>|dy|x1.6，到头不循环。
设置页与预习详情页不参与，避免误触。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: 词表跨科搜索、句型页与设置页

**Files:**
- Modify: `src/tpl.html:1027-1068`（`renderList`）
- Modify: `src/tpl.html:1198-1210`（`renderFrames`）
- Modify: `src/tpl.html:1213-1265`（`renderMe`）

**Interfaces:**
- Consumes: Task 5 的 `bookBarHTML()` / `bindBookBar()`、Task 4 的 `BY_ID` / `curWords()`

**背景：** 词表页平时只列当前书；一旦输入关键词就自动把另一科的命中追加成独立分组，
组头标明科目，这样搜 `pressure` 能一次看到两科的例句。清空关键词回到单科视图。

- [ ] **Step 1: 重写 renderList**

```js
/* ---------- 词表 ---------- */
let q = '';
function renderList() {
  view.innerHTML = `
    ${bookBarHTML()}
    <div style="display:flex;gap:8px;margin-top:12px">
      <input class="search" id="q" placeholder="搜索单词或中文…" value="${esc(q)}">
      <button class="btn ${S.set.maskZh ? 'pri' : 'line'}" id="mask" style="flex:0 0 auto">${S.set.maskZh ? '显示' : '遮住'}中文</button>
    </div>
    <div id="rows"></div>`;
  bindBookBar();
  const rows = $('rows');
  const draw = () => {
    const kw = q.trim().toLowerCase();
    const hit = w => !kw || w.w.toLowerCase().includes(kw) || w.zh.includes(kw);
    // 平时只看当前书；一搜就把另一科的命中也带出来，方便对比同名词的两个例句
    const books = kw ? [curBook(), ...DATA.books.filter(b => b.id !== S.set.book)]
                     : [curBook()];
    let h = '';
    books.forEach((bk, bi) => {
      bk.sections.forEach(s => {
        const ws = s.words.filter(hit);
        if (!ws.length) return;
        const head = bi ? `${esc(bk.cn)} · ${esc(s.cn)}` : `${s.id}. ${esc(s.cn)}`;
        h += `<div class="grp">${head} · ${ws.length}</div><div class="card rowgrp">`;
        ws.forEach(w => {
          const b = S.prog[w.id]?.box || 0, sn = !isNew(w);
          const col = !sn ? 'var(--color-track)' : b >= 4 ? 'var(--color-success)' : b >= 2 ? 'var(--color-warning)' : 'var(--color-error)';
          h += `<div class="row" data-w="${esc(w.id)}">
            <span class="dot" style="background:${col}"></span>
            <div class="bd">
              <span class="w">${esc(w.w)}</span><span class="p">${esc(w.ipa)}</span>
              <div class="z${S.set.maskZh ? ' hide' : ''}">${esc(w.zh)}</div>
            </div>
            <span class="iconbtn" data-say="${esc(w.w)}">${IC.spk}</span>
          </div>`;
        });
        h += '</div>';
      });
    });
    rows.innerHTML = h || '<div class="empty">没有匹配的词</div>';
  };
  draw();
  $('q').oninput = e => { q = e.target.value; draw(); };
  $('mask').onclick = () => { S.set.maskZh = !S.set.maskZh; save(); renderList(); };
  rows.onclick = e => {
    const s = e.target.closest('[data-say]');
    if (s) { e.stopPropagation(); say(s.dataset.say); return; }
    const r = e.target.closest('.row');
    if (r) startStudy([BY_ID[r.dataset.w]], '单词');
  };
}
```

- [ ] **Step 2: 句型页跟随当前书**

```js
/* ---------- 句型 ---------- */
function renderFrames() {
  const bk = curBook();
  view.innerHTML = bookBarHTML() +
    `<div class="sec-t">常用科学英语句型 · ${bk.frames.length} 组</div>` +
    bk.frames.map((f, i) => `<div class="card fr">
      <div class="use">${esc(f.use)}</div>
      <div class="fm">${esc(f.frame)}</div>
      <div class="en">${esc(f.ex)}</div>
      <div class="cn">${esc(f.exzh)}</div>
      <div style="margin-top:12px"><button class="btn line tiny" data-f="${i}">${IC.spk} 朗读例句</button></div>
    </div>`).join('') +
    `<div class="credit">先模仿句型，再替换关键词造句</div>`;
  bindBookBar();
  view.onclick = e => { const b = e.target.closest('[data-f]'); if (b) say(bk.frames[b.dataset.f].ex); };
}
```

两个 `onclick` 不冲突：`bindBookBar()` 绑在按钮元素自身，`view.onclick` 绑在容器上。
点分段控件时事件会冒泡到 `view.onclick`，但那里 `closest('[data-f]')` 取不到东西，
不做任何事。顺序要紧：`bindBookBar()` 必须在 `innerHTML` 赋值之后调用。

- [ ] **Step 3: 设置页按当前书统计，清空文案改准**

`renderMe` 开头：

```js
function renderMe() {
  const W = curWords();
  const boxes = [0, 1, 2, 3, 4, 5].map(b => W.filter(w => (S.prog[w.id]?.box || 0) === b && !isNew(w)).length);
```

箱体条的分母（约 1248 行）：

```js
      <span class="bar" style="flex:1;margin:0"><i style="width:${n / W.length * 100}%"></i></span>
```

「试听」用的词（约 1261 行）改成带前缀：

```js
    const w = BY_ID['sci:photosynthesis'];
```

清空按钮文案与确认语（约 1252、1264 行）：

```js
  <button class="btn line blk" id="reset" style="margin-top:10px;color:var(--color-error)">清空全部学习进度（两科）</button>
```

```js
  $('reset').onclick = () => { if (confirm('确定清空两本词书的全部学习进度？')) { S.prog = {}; save(); render(); toast('已清空'); } };
```

- [ ] **Step 4: 构建并验证**

```bash
python3 src/build.py
```

浏览器里（先 `localStorage.clear(); location.reload()`）：

```js
document.querySelector('[data-t=list]').click();
const inp = document.getElementById('q');
inp.value = 'pressure'; inp.dispatchEvent(new Event('input'));
const heads = [...document.querySelectorAll('.grp')].map(g => g.textContent);
const ids = [...document.querySelectorAll('.row')].map(r => r.dataset.w);
JSON.stringify({ heads, ids })
```

Expected: `ids` 同时含 `sci:pressure` 和 `phy:pressure`；
`heads` 里有一条以「物理 · 」开头的跨科组头。

清空关键词应回到单科：

```js
const inp = document.getElementById('q');
inp.value = ''; inp.dispatchEvent(new Event('input'));
JSON.stringify({
  books: new Set([...document.querySelectorAll('.row')].map(r => r.dataset.w.split(':')[0])).size,
  crossHead: [...document.querySelectorAll('.grp')].some(g => g.textContent.startsWith('物理 · '))
})
```

Expected: `books: 1`、`crossHead: false`

句型页与设置页：

```js
document.querySelector('[data-t=frames]').click();
const sci = document.querySelectorAll('.fr').length;
document.querySelector('.bk[data-bk=phy]').click();
const phy = document.querySelectorAll('.fr').length;
document.querySelector('[data-t=me]').click();
JSON.stringify({ sci, phy, reset: document.getElementById('reset').textContent })
```

Expected: `sci: 10`；`phy: 0`（Task 9 之前物理还没有句型，属预期）；
`reset` 文案为「清空全部学习进度（两科）」。

- [ ] **Step 5: 提交**

```bash
git add src/tpl.html index.html
git commit -m "$(cat <<'EOF'
feat: 词表搜索自动跨科，句型与设置页跟随当前书

有关键词时把另一科的命中追加成独立分组，组头标科目，
同名词的两个例句可直接对比。清空进度文案改准为两科。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: 物理 111 词的音标、音节与助记

**Files:**
- Modify: `src/phon_phy.py`（填 111 条）
- Modify: `src/build.py`（`STRICT_PHON = False` → `True`）

**Interfaces:**
- Produces: `PHON_PHY: dict[str, tuple[str, str]]`，111 个键，键为裸词

**格式规则**（与 `src/phon.py` 完全一致，照它的写法）：

- 值是 `(音节串, 助记)` 二元组
- 音节串每块写 `拼写=音标`，块间用 `|`
- **短语里的词与词之间用 ` / `**（前后各一个空格），例如
  `"kinetic energy": ("ki=kɪ|net=ˈnet|ic=ɪk / en=ˈen|er=ə|gy=dʒi", "…")`
- 整词音标由各块音标顺序拼接得出，所以重音符 `ˈ` / `ˌ` 写在所属音节的音标里
- **各块拼写连起来必须等于原词**（构建时 `check()` 会验），空格与连字符不计
- 音标用英式 RP，不带斜杠
- 助记写一句话，讲构词或词源怎么通到词义；实在没有词源可讲就写用法提示

四个样例（覆盖普通词、短语、连字符词、en dash 词）：

```python
    "friction": ("fric=ˈfrɪk|tion=ʃn",
                 "拉丁 fricare「摩擦」→ friction 摩擦力；同源 fricative 摩擦音。"),
    "specific heat capacity": ("spe=spəˈ|ci=sɪ|fic=fɪk / heat=hiːt / ca=kəˈ|pa=pæ|ci=sɪ|ty=ti",
                               "specific「每单位的」+ heat capacity「储热本领」→ 每千克升高 1℃ 所需的热量。"),
    "half-life": ("half=ˈhɑːf|-=|life=laɪf",
                  "「一半的寿命」：活度减到一半所需的时间。"),
    "distance–time graph": ("dis=ˈdɪs|tance=təns|–= / time=taɪm / graph=ɡrɑːf",
                            "纵轴距离、横轴时间；斜率就是速度。"),
```

连字符与 en dash 单独占一块、音标留空，这样各块拼写连起来能一字不差地拼回原词。

**要覆盖的 111 个词**（`src/phon.py` 里已有的同名词不要重复写）：

```
sketch, show, physical quantity, SI unit, resolution, uncertainty, error, parallax,
reliable, accurate, rest, reference point, displacement, average speed, constant speed,
deceleration, initial velocity, final velocity, distance–time graph, speed–time graph,
gradient, stationary, newton, push, pull, friction, air resistance, drag, weight,
gravitational field strength, normal contact force, tension, resultant force,
balanced forces, unbalanced forces, free fall, terminal velocity, energy, energy store,
gravitational potential energy, elastic potential energy, chemical energy, thermal energy,
transfer, conservation of energy, work done, joule, power, watt, useful energy,
wasted energy, efficiency, regular object, irregular object, water displacement, float,
sink, area, pascal, atmospheric pressure, liquid pressure, upthrust,
thermal energy transfer, conduction, convection, radiation, specific heat capacity,
transverse wave, longitudinal wave, amplitude, wavelength, period, wave speed,
reflection, refraction, normal, angle of incidence, sound, vacuum, echo, electric charge,
current, ampere, potential difference, circuit, series circuit, parallel circuit,
magnetic field, electromagnet, transformer, nucleus, proton, neutron, electron, isotope,
radioactive decay, alpha particle, beta particle, gamma radiation, half-life, planet,
orbit, gravitational field, star, galaxy, light-year, risk, safety precaution, valid,
range, interval
```

- [ ] **Step 1: 先把校验打开，让构建失败**

改 `src/build.py`：

```python
STRICT_PHON = True         # phon_phy.py 已填满，缺词一律视为错误
```

- [ ] **Step 2: 跑构建，确认它失败并列出缺词**

```bash
python3 src/build.py
```

Expected: FAIL —— `PHON 缺 111 词: ['SI unit', 'accurate', …]`

- [ ] **Step 3: 分批填写 phon_phy.py**

按上面的章节顺序分 6 批写，每批约 20 词。**每批写完立刻跑一次构建**，
这样音节拼写写错时能马上定位，不用在 111 条里翻：

```bash
python3 src/build.py 2>&1 | tail -3
```

写到一半时它会继续报「PHON 缺 N 词」，N 应逐批下降。
若报「音节拼写与原词不符」，看它打印的 `(id, 拼回来的串)` 修那一条。

- [ ] **Step 4: 全部写完后跑构建，确认通过**

```bash
python3 src/build.py
```

Expected: 成功，输出里 `0 词缺音标`，词数仍是 `332 词`

- [ ] **Step 5: 逐条核对音标拼接**

```bash
python3 -c "
import json
d = json.load(open('src/data.json', encoding='utf-8'))
phy = next(b for b in d['books'] if b['id']=='phy')
bad = [w['id'] for s in phy['sections'] for w in s['words']
       if '?' in w['ipa'] or not w['tip']]
assert not bad, bad
print('OK 162 词音标与助记齐备')
"
```

Expected: `OK 162 词音标与助记齐备`

- [ ] **Step 6: 浏览器抽查发音**

打开物理书，进「波、声音与光」章，检查 `wavelength`、`refraction`、
`angle of incidence` 三张卡：音标显示正常、点音节能单独朗读、「逐音节跟读」不卡。

- [ ] **Step 7: 提交**

```bash
git add src/phon_phy.py src/build.py src/data.json index.html
git commit -m "$(cat <<'EOF'
feat: 补齐物理 111 词的音标、音节切分与词根助记

与 phon.py 同名的 51 词直接复用，不重复维护。
STRICT_PHON 打开，此后缺音标一律构建失败。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: 物理的 10 组答题句型

**Files:**
- Modify: `src/frames_phy.py`

**Interfaces:**
- Produces: `FRAMES_PHY: list[dict]`，每项 `{use, frame, ex, exzh}` 四个字段，
  与科学书 `frames` 结构一致（句型页直接复用同一套渲染）

**内容**（取自 PDF 最后一节「High-frequency answer patterns / 高频答题句型」，
`use` 是我们补的用途说明，PDF 里没有）：

- [ ] **Step 1: 写 frames_phy.py**

```python
# -*- coding: utf-8 -*-
"""物理的高频答题句型。字段与 data.json 里 frames 一致。

来源：Cambridge IGCSE Physics 0625 核心词汇表最后一节。
use 是我们补的用途说明，原书没有。
"""
FRAMES_PHY = [
    {"use": "描述两个量的变化关系",
     "frame": "As ___ increases, ___ increases/decreases.",
     "ex": "As the force increases, the acceleration increases.",
     "exzh": "随着力增大，加速度增大。"},
    {"use": "判断物体静止并给理由",
     "frame": "The object is stationary because ___.",
     "ex": "The object is stationary because the resultant force is zero.",
     "exzh": "物体静止，因为合力为零。"},
    {"use": "比较两次结果并给理由",
     "frame": "The result is greater because ___.",
     "ex": "The result is greater because the temperature is higher.",
     "exzh": "结果更大，因为温度更高。"},
    {"use": "论证实验是公平实验",
     "frame": "This is a fair test because only the independent variable is changed.",
     "ex": "This is a fair test because only the independent variable is changed.",
     "exzh": "这是公平实验，因为只有自变量被改变。"},
    {"use": "写提高可靠性的做法",
     "frame": "Repeat the measurements, identify anomalies and calculate a mean.",
     "ex": "Repeat the measurements, identify anomalies and calculate a mean.",
     "exzh": "重复测量、识别异常值并计算平均值。"},
    {"use": "解释压强变化",
     "frame": "The same force acts over a smaller area, so the pressure is greater.",
     "ex": "The same force acts over a smaller area, so the pressure is greater.",
     "exzh": "相同的力作用在更小面积上，因此压强更大。"},
    {"use": "由受力平衡推合力",
     "frame": "The forces are balanced, so the resultant force is zero.",
     "ex": "The forces are balanced, so the resultant force is zero.",
     "exzh": "力平衡，因此合力为零。"},
    {"use": "描述能量转移",
     "frame": "Energy is transferred from ___ to ___.",
     "ex": "Energy is transferred from the chemical store to the thermal store.",
     "exzh": "能量从化学能储存转移到内能储存。"},
    {"use": "指出答案缺单位",
     "frame": "The answer is incomplete because the unit is missing.",
     "ex": "The answer is incomplete because the unit is missing.",
     "exzh": "答案不完整，因为缺少单位。"},
    {"use": "读图线斜率",
     "frame": "The graph is steeper, so the speed is greater.",
     "ex": "The graph is steeper, so the speed is greater.",
     "exzh": "图线更陡，因此速度更大。"},
]
```

- [ ] **Step 2: 构建并验证**

```bash
python3 src/build.py
python3 -c "
import json
d = json.load(open('src/data.json', encoding='utf-8'))
phy = next(b for b in d['books'] if b['id']=='phy')
assert len(phy['frames']) == 10, len(phy['frames'])
for f in phy['frames']:
    for k in ('use','frame','ex','exzh'):
        assert f.get(k), (f, k)
print('OK 10 组句型')
"
```

Expected: `OK 10 组句型`

- [ ] **Step 3: 浏览器验证**

切到物理书 → 句型 Tab，应有 10 张卡，「朗读例句」可点、能出声。

```js
document.querySelector('[data-t=frames]').click();
document.querySelector('.bk[data-bk=phy]').click();
JSON.stringify({ n: document.querySelectorAll('.fr').length,
                 first: document.querySelector('.fr .fm').textContent })
```

Expected: `n: 10`，`first` 为 `As ___ increases, ___ increases/decreases.`

- [ ] **Step 4: 提交**

```bash
git add src/frames_phy.py src/data.json index.html
git commit -m "$(cat <<'EOF'
feat: 补物理 10 组高频答题句型

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: 物理 162 句的翻译思路

**Files:**
- Create: `src/trans_phy.py`

**Interfaces:**
- Produces: `TRANS_PHY: dict[str, dict]`，键为裸词，值含 `pat` / `flow` / `core` / `final` / `tip` 五个字段

**格式**（照 `src/trans.py` 写，它有 170 条现成样例可参考）：

- `pat` —— 这句的句型概括，一行
- `flow` —— 顺句理解，每项 `[英文块, 中文块, 成分]`，**每项必须是 3 个元素**
- `core` —— 主干先行，一行
- `final` —— 完整译文按意群切段，每项 `[中文块, 颜色组号]`；
  **各段拼起来（去掉空白后）必须与词条的 `exzh` 完全一致**，构建时会逐字比对
- `tip` —— 中译英时要注意什么，一行

**这是全计划里最大的一块（162 条），分章推进**，每章写完跑一次构建。
构建对缺失的翻译思路只打印提醒、不失败，所以中途随时可以提交、可以停。

- [ ] **Step 1: 建文件并写第一章（题目指令词 12 条）**

```python
# -*- coding: utf-8 -*-
"""物理例句的翻译思路。字段与 trans.py 一致，按裸词索引。

与 trans.py 分开是因为同名词（pressure、density…）在两本书里的例句不是同一句，
构建时各自挂到所属的书上。
"""
TRANS_PHY = {
    "calculate": {
        "pat": "祈使句：动词 + 宾语",
        "flow": [["Calculate", "计算", "谓语"],
                 ["the average speed", "平均速度", "宾语"]],
        "core": "主干就是「计算 + 什么」，没有主语。",
        "final": [["计算", 1], ["平均速度", 2], ["。", 0]],
        "tip": "指令词开头的祈使句，中文同样不加主语，直接「计算…」。",
    },
}
```

- [ ] **Step 2: 跑构建，确认它接上了**

```bash
python3 src/build.py 2>&1 | tail -3
```

Expected: 输出里带翻译思路的句数从 170 涨到 171，且提醒 `phy 尚缺翻译思路 161 条`。

若报 `phy 的 final 拼接与译文不符`，说明 `final` 各段拼起来不等于 `exzh`，
按它打印的两行对照修。

- [ ] **Step 3: 按章补完剩下 150 条**

顺序：测量与数据 17 → 运动 17 → 力 17 → 能量功与功率 16 → 密度压强与流体 12 →
热学 10 → 波声音与光 15 → 电与磁 14 → 原子核与空间物理 17 → 实验技能 15。

每章写完跑：

```bash
python3 src/build.py 2>&1 | tail -3
```

缺口数应逐章下降。每章末尾提交一次：

```bash
git add src/trans_phy.py src/data.json index.html
git commit -m "feat: 物理翻译思路补至 <章名>

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

- [ ] **Step 4: 全部补完后验证**

```bash
python3 src/build.py
python3 -c "
import json
d = json.load(open('src/data.json', encoding='utf-8'))
miss = [w['id'] for b in d['books'] for s in b['sections'] for w in s['words'] if 'tr' not in w]
assert not miss, ('缺翻译思路', len(miss), miss[:5])
print('OK 332 句全带翻译思路')
"
```

Expected: `OK 332 句全带翻译思路`，且构建输出为 `332 词（332 句带翻译思路，0 词缺音标）`

- [ ] **Step 5: 浏览器抽查**

物理书任一词翻面 → 翻译思路卡片应展开，意群上色与上方英文分组对应，
完整译文读起来通顺。

---

## Task 11: 更新 README 与收尾

**Files:**
- Modify: `README.md`
- Delete: `mockup-study.html`（设计稿，临时文件）

- [ ] **Step 1: 改 README**

需要改的地方：

- 首行：`覆盖 IGCSE 自然科学核心词汇 **164 词 + 10 组句型**` →
  `两本词书：IGCSE 自然科学 **170 词**、Cambridge IGCSE Physics 0625 **162 词**，各带 10 组句型`
- 「记忆」一节加一条：
  `- 两本词书顶部切换，也可左右滑动；进度、复习队列、难词本各自独立`
- 「记忆」一节里 `首页有今日到期复习、按主题进度、难词本` →
  `学习页有今日到期复习、按主题网格、难词本；另一科有到期复习时在标签上挂红点`
- 「记忆」一节里 `词表支持搜索与「遮住中文」自测` →
  `词表支持搜索与「遮住中文」自测；搜索时自动跨科，同名词两科例句可直接对比`
- 「从源码构建」的命令块加一行物理解析：

```bash
pip install pymupdf
python3 src/parse_pdf.py <自然科学词汇表.pdf> > src/parsed.json      # 可选，已附 data.json
python3 src/parse_physics_pdf.py <物理词汇表.pdf> > src/parsed_phy.json  # 可选，已入库
python3 src/build.py                                                 # 生成 index.html
```

- 文件表加四行：

| 文件 | 说明 |
| --- | --- |
| `src/parse_physics_pdf.py` | 从物理 PDF 的四栏表格解析词条，处理跨页续行与章内重复 |
| `src/phon_phy.py` | 物理独有 111 词的音标、音节切分与词根助记 |
| `src/trans_phy.py` | 物理 162 句的翻译思路 |
| `src/frames_phy.py` | 物理的 10 组高频答题句型 |

- `src/phon.py` 那行说明后补一句：
  `两本词书共用同一份音标字典——51 个同名词音标一致，不重复维护。`

- [ ] **Step 2: 删掉设计稿**

```bash
rm -f mockup-study.html
```

- [ ] **Step 3: 全量验收**

```bash
python3 src/build.py
```

Expected: `built …/index.html — 332 词（332 句带翻译思路，0 词缺音标）, 1 节预习, … KB`

浏览器里逐条过验收清单（先 `localStorage.clear(); location.reload()`）：

```js
const v = document.getElementById('view');
const r = {};
['sci','phy'].forEach(b => {
  document.querySelector(`.bk[data-bk=${b}]`).click();
  r[b] = { cards: document.querySelectorAll('.gcard').length,
           screens: +(v.scrollHeight / v.clientHeight).toFixed(2) };
});
JSON.stringify(r)
```

Expected: `sci` 9 章、`phy` 11 章，两者 `screens` 都 ≤ 2.5

断网验证：在浏览器里停掉预览服务器后，直接 `open index.html`（`file://` 协议），
确认词表、朗读、翻面、翻译思路都正常。

- [ ] **Step 4: 提交**

```bash
git add README.md
git rm --cached mockup-study.html 2>/dev/null || true
git commit -m "$(cat <<'EOF'
docs: README 补两本词书与物理构建链路

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## 自查

对照 spec 逐节核对：

| spec 章节 | 落在哪个任务 |
| --- | --- |
| 数据模型 · books 顶层结构 | Task 2 Step 5 |
| 数据模型 · 词条 id | Task 2 Step 4 |
| 数据模型 · 两处去重 | Task 1 Step 1（`KEEP_DUP`）+ Task 2 `check_ids` 兜底 |
| 数据模型 · 音标复用 / TRANS 分书 | Task 2 Step 1、Step 6；Task 8；Task 10 |
| 源文件改动表（8 个文件） | Task 1/2/3/8/9/10/11 逐一覆盖 |
| 构建期五道校验 | Task 2（check、check_ids、check_phon）、Task 2 Step 6（final 比对）、Task 3（课时引用） |
| 界面 · 学习页网格 | Task 5 |
| 界面 · 三种切换入口 | Task 5（分段控件）+ Task 6（滑动） |
| 界面 · 词表跨科搜索 | Task 7 Step 1 |
| 界面 · 句型页 | Task 7 Step 2、Task 9 |
| 界面 · 设置页 | Task 7 Step 3 |
| 状态与迁移 | Task 4 Step 2、Step 6 |
| 课前预习跨书取词 | Task 3、Task 5 Step 4/5 |
| 体积 | Task 11 Step 3 观察构建输出 |
| 验收清单 6 条 | Task 11 Step 3 + 各任务的浏览器验证步骤 |

**未覆盖项：** spec「待确认」里的课程名，本计划按
`Cambridge IGCSE Physics 0625 衔接课程` 落地（Task 3 Step 3）。用户若给出别的名字，
改 `src/lessons.py` 一行后重跑构建即可。

**命名一致性核对：** `curBook` / `curWords` / `BY_ID` / `BOOK_IDS` / `dueCount` /
`switchBook` / `bookBarHTML` / `bindBookBar` / `lessonWordId` / `lessonWords` /
`STRICT_PHON` / `PHON_PHY` / `TRANS_PHY` / `FRAMES_PHY` —— 定义处与引用处已逐一比对一致。
