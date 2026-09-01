# 词表页「测试」功能 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在词表页加一个测试入口，用辨义／拼写／听写三种题型测「当前正在看的这批词」，结果喂回现有的间隔重复。

**Architecture:** 一个与现有卡片学习页同级的全屏覆盖层 `#quiz`。题型由词条当前的记忆盒子决定并可手动锁定；拼写与听写走文本输入 + 归一化判分 + 字符级 diff，辨义走四选一。所有动作按钮放在可滚动正文里，不做固定底栏，以避开 iOS 键盘遮挡。音效用 Web Audio 现场合成，不引入音频文件。

**Tech Stack:** 原生 HTML/CSS/JS 单文件（无框架、无构建工具、无 npm、无依赖）；Python 构建脚本把数据注入模板。

**Spec:** `docs/superpowers/specs/2026-09-02-vocab-quiz-design.md`

## 本项目没有测试框架

这个仓库不用 pytest / jest，**不要引入**。每个任务的「测试」指下面两样：

1. **`python3 src/build.py`** —— 构建脚本内置校验，任一条不满足就 `raise SystemExit`。
2. **浏览器断言** —— `preview_start {name: "flashcard"}` 起预览（配置已在 `.claude/launch.json`，
   端口 8777，服务项目根目录），`navigate` 到 `http://localhost:8777/index.html`，
   用 `javascript_tool` 跑断言表达式，`read_console_messages` 查报错。
   **不要用 Bash 起服务器。**

浏览器验证前先 `resize_window {preset:"mobile"}`（375×812），并
`javascript_tool` 跑 `localStorage.clear(); location.reload()` 拿到干净状态。

**`getComputedStyle(...).opacity` 在这个浏览器面板里读数不可靠**（内联设 `opacity:0` 仍报 1）。
要验证显隐，用截图，或者检查 `document.body.className` 这类可靠信号。

## Global Constraints

- 所有源改动都在 `src/` 下；`index.html` 是 `python3 src/build.py` 的产物，
  **永远不要手改**，但每次提交都要带上它。
- 单文件、零外部请求、断网可打开。**不得引入 CDN、字体链接、fetch、音频文件、任何依赖。**
- CSS 惯例：令牌（`--color-*` / `--radius-*` / `--font-size-*` / `--font-weight-*` /
  `--shadow-*` / `--duration-*` / `--ease-standard`）管颜色、圆角、字号、字重、阴影、过渡；
  细粒度间距写裸 px。这是代码库既有惯例（`.tabbar{gap:2px}`、`.btn{padding:9px 15px}`、
  `.bar{margin-top:8px}`），**沿用即可，裸 px 间距不是问题**。
- 深浅色靠 `light-dark()` 令牌自动切换，**不得另写 `.dark` 深色规则**。
- 所有动效必须包在 `@media (prefers-reduced-motion: reduce)` 的兜底里。
- 词条 id 格式 `<bookId>:<word>`，bookId 只有 `sci` 和 `phy`。
- 现有 356 词的数据、学习页、卡片学习页、句型页**一律不改**（Task 8 的一行 CSS 除外）。
- 注释用中文，解释「为什么」而非「是什么」。
- 提交信息用中文，格式 `<type>: <简述>`，正文结尾必须带
  `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`。
- 当前分支：先建 `feat/vocab-quiz`，**不要在 main 上直接改**。
- 项目根的 `mockup-quiz.html` 是未入库的设计稿参考实现，**不要提交、不要删除**，
  实现时可以对照它。

## 文件结构

整个功能都落在 `src/tpl.html` 一个文件里 —— 这是项目既有形态（单文件产物），
不为这个功能拆分文件。改动集中在四处：

| 位置 | 职责 |
| --- | --- |
| `<style>` 块尾部（`.credit` 规则之后，约 655 行） | 测试覆盖层的全部样式 |
| `#study` 覆盖层之后（约 700 行） | `#quiz` 覆盖层的 HTML 骨架 |
| `<script>` 里 `/* ---------- 词表 ---------- */` 之前（约 1120 行） | 音效引擎、纯函数、测试流程 |
| `renderList()`（约 1122 行）与 `renderMe()`（约 1345 行） | 入口按钮、设置开关 |

---

## Task 1: 音效引擎与设置开关

**Files:**
- Modify: `src/tpl.html`（`<script>` 里 `const shuffle = …`（约 1118 行）之后插入音效段）
- Modify: `src/tpl.html:729-730`（`DEF.set` 加 `sfx`）
- Modify: `src/tpl.html:1345-1346`（设置页「翻卡自动朗读」之后加一项）

**Interfaces:**
- Produces:
  - `sfxOK(streak: number): void` —— 答对音，连对数越大音越高
  - `sfxNo(): void` —— 答错音
  - `sfxFinish(perfect: boolean): void` —— 一轮结束音
  - `S.set.sfx: boolean`，默认 `true`

- [ ] **Step 1: 先建分支**

```bash
git checkout -b feat/vocab-quiz
```

- [ ] **Step 2: 写断言，确认它失败**

`python3 src/build.py` 后在浏览器里跑：

```js
JSON.stringify({
  设置项: typeof S.set.sfx,
  函数: [typeof sfxOK, typeof sfxNo, typeof sfxFinish]
})
```

Expected: FAIL —— `{"设置项":"undefined","函数":["undefined","undefined","undefined"]}`

- [ ] **Step 3: `DEF.set` 加 `sfx`**

`src/tpl.html` 约 730 行，把：

```js
  set: { rate: .95, voice: '', autoSpeak: true, sylMode: 'respell', maskZh: false, theme: 'light', book: 'sci' }
```

改成：

```js
  set: { rate: .95, voice: '', autoSpeak: true, sylMode: 'respell', maskZh: false, theme: 'light', book: 'sci', sfx: true, quizLock: '' }
```

（`quizLock` 是 Task 7 的题型锁定，一并加进来免得再动这一行。）

- [ ] **Step 4: 插入音效引擎**

在 `const shuffle = …`（约 1118 行）**之后**、`/* ---------- 词表 ---------- */` 之前插入：

```js
/* ===================== 测试音效 =====================
   用 Web Audio 现场合成，不引入任何音频文件——单文件离线是硬约束。 */
let AC = null;
function ac() {
  try {
    AC = AC || new (window.AudioContext || window.webkitAudioContext)();
    if (AC.state === 'suspended') AC.resume();
    return AC;
  } catch (e) { return null; }
}
document.addEventListener('pointerdown', ac, { once: true, capture: true });   // iOS 要用户手势才解锁

function tone(freq, at, dur, gain, type) {
  if (!S.set.sfx) return;
  const a = ac(); if (!a) return;
  const o = a.createOscillator(), g = a.createGain(), t = a.currentTime + at;
  o.type = type || 'sine'; o.frequency.value = freq;
  g.gain.setValueAtTime(0.0001, t);
  g.gain.linearRampToValueAtTime(gain, t + .014);
  g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  o.connect(g); g.connect(a.destination);
  o.start(t); o.stop(t + dur + .03);
}
const NOTE = n => 523.25 * Math.pow(2, n / 12);          // C5 起算
/* 连对越多起始音越高、音符越多——每题都一样的奖励等于没有奖励 */
function sfxOK(streak) {
  const base = [0, 0, 2, 4, 5, 7][Math.min(streak, 5)];
  tone(NOTE(base),      0,    .17, .16);
  tone(NOTE(base + 4), .065,  .19, .14);
  tone(NOTE(base + 7), .13,   .24, .12);
  if (streak >= 5) tone(NOTE(base + 12), .195, .30, .10);
}
function sfxNo() { tone(196, 0, .15, .09, 'triangle'); tone(155, .085, .20, .08, 'triangle'); }
function sfxFinish(perfect) {
  (perfect ? [0, 4, 7, 12, 16] : [0, 4, 7]).forEach((n, i) => tone(NOTE(n), i * .1, .36, .13));
}
```

- [ ] **Step 5: 设置页加开关**

`src/tpl.html` 约 1345 行，在「翻卡自动朗读」那一项**之后**、`</div>` 之前插入：

```js
    <div class="set"><div class="lb">答题音效<small>测试答对答错的提示音</small></div>
      <button class="sw${S.set.sfx ? ' on' : ''}" id="sfx"><i></i></button></div>
```

并在 `renderMe()` 的事件绑定里（`$('auto').onclick = …` 那行之后）加：

```js
  $('sfx').onclick = e => {
    S.set.sfx = !S.set.sfx; e.currentTarget.classList.toggle('on', S.set.sfx); save();
    if (S.set.sfx) sfxOK(1);                       // 打开时响一声，让用户听见效果
  };
```

- [ ] **Step 6: 构建并验证**

```bash
python3 src/build.py
```

浏览器里（先 `localStorage.clear(); location.reload()`）：

```js
const r = { 默认值: S.set.sfx, 函数: [typeof sfxOK, typeof sfxNo, typeof sfxFinish] };
r.可调用 = (() => { try { sfxOK(3); sfxNo(); sfxFinish(true); return true } catch (e) { return 'ERR:' + e.message } })();
document.querySelector('[data-t=me]').click();
r.开关存在 = !!document.getElementById('sfx');
r.开关初始 = document.getElementById('sfx').classList.contains('on');
document.getElementById('sfx').click();
r.点击后设置 = S.set.sfx;
r.点击后样式 = document.getElementById('sfx').classList.contains('on');
r.已持久化 = JSON.parse(localStorage.getItem('igcse-flashcard-v1')).set.sfx;
document.getElementById('sfx').click();
JSON.stringify(r)
```

Expected: `默认值:true`、三个函数都是 `function`、`可调用:true`、`开关存在:true`、
`开关初始:true`、`点击后设置:false`、`点击后样式:false`、`已持久化:false`

再验证关掉后**真的不发声** —— 拦截 `createOscillator` 数调用次数，而不是只看代码路径：

```js
const a = ac();
const orig = a.createOscillator.bind(a);
let n = 0; a.createOscillator = () => { n++; return orig(); };

S.set.sfx = true;  n = 0; sfxOK(3); const 开 = n;
S.set.sfx = false; n = 0; sfxOK(3); sfxNo(); sfxFinish(true); const 关 = n;
S.set.sfx = true;
a.createOscillator = orig;
JSON.stringify({ 开着时建了几个振荡器: 开, 关掉后: 关 })
```

Expected: `开着时建了几个振荡器:3`（连对 3 是三个音）、`关掉后:0`

`read_console_messages {onlyErrors:true}` 应无输出。

- [ ] **Step 7: 提交**

```bash
git add src/tpl.html index.html
git commit -m "$(cat <<'EOF'
feat: 测试音效引擎与设置页开关

用 Web Audio 现场合成，不引入音频文件。AudioContext 在首次 pointerdown
解锁——iOS 要用户手势。连对越多起始音越高。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: 判分与出题的纯函数

**Files:**
- Modify: `src/tpl.html`（Task 1 插入的音效段**之后**继续插入）

**Interfaces:**
- Consumes: `DATA.books`、`BY_ID`、`S.prog`、`esc()`（均已存在）
- Produces:
  - `normAns(s: string): string` —— 判分用的归一化
  - `diffHTML(user: string, ans: string): {you: string, cor: string}` —— 字符级 diff，返回两段 HTML
  - `distractors(w: 词条): string[]` —— 3 个与答案语义不重叠的中文释义
  - `quizType(w: 词条): 'mc' | 'spell' | 'dict'` —— 按记忆盒子定题型，受 `S.set.quizLock` 覆盖

- [ ] **Step 1: 写断言，确认它失败**

```js
JSON.stringify([typeof normAns, typeof diffHTML, typeof distractors, typeof quizType])
```

Expected: FAIL —— 四个都是 `"undefined"`

- [ ] **Step 2: 实现**

在 Task 1 的音效段之后插入：

```js
/* ===================== 测试：判分与出题 ===================== */

/* 判分前抹平大小写、空格、连字符。词库里 distance–time graph 用的是 U+2013，
   不是 ASCII 连字符；half-life、light-year、gravitational field strength 同理。 */
const normAns = s => s.toLowerCase().replace(/[-–—\s]/g, '');

/* 字符级 LCS diff：答案里用户漏掉的标绿，用户多写/写错的标红 */
function diffHTML(user, ans) {
  const a = [...user], b = [...ans], n = a.length, m = b.length;
  const L = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
  for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--)
    L[i][j] = a[i].toLowerCase() === b[j].toLowerCase() ? L[i + 1][j + 1] + 1
                                                        : Math.max(L[i + 1][j], L[i][j + 1]);
  let i = 0, j = 0, you = '', cor = '';
  while (i < n && j < m) {
    if (a[i].toLowerCase() === b[j].toLowerCase()) { you += esc(a[i]); cor += esc(b[j]); i++; j++; }
    else if (L[i + 1][j] >= L[i][j + 1]) { you += '<b class="bad">' + esc(a[i]) + '</b>'; i++; }
    else { cor += '<b class="miss">' + esc(b[j]) + '</b>'; j++; }
  }
  while (i < n) { you += '<b class="bad">' + esc(a[i]) + '</b>'; i++; }
  while (j < m) { cor += '<b class="miss">' + esc(b[j]) + '</b>'; j++; }
  return { you, cor };
}

/* 干扰项不能与答案有任何语义块重叠：voltage「电压」不能拿来干扰
   potential difference「电势差/电压」，否则两个选项都对。 */
const zhToks = z => new Set(z.replace(/[（(][^）)]*[）)]/g, '')
                             .split(/[；;、\/／,，]/).map(x => x.trim()).filter(Boolean));
function distractors(w) {
  const ansT = zhToks(w.zh);
  const clash = z => [...zhToks(z)].some(x => ansT.has(x));
  const bk = BOOKS[w.book];
  const same = bk.words.filter(x => x.sec === w.sec && x.id !== w.id && !clash(x.zh));
  const all  = bk.words.filter(x => x.id !== w.id && !clash(x.zh));
  return shuffle((same.length >= 3 ? same : all).slice()).slice(0, 3).map(x => x.zh);
}

/* 题型跟着记忆盒子升级：先认得出，再写得出，最后听得出。
   S.set.quizLock 非空时锁死题型。 */
function quizType(w) {
  if (S.set.quizLock) return S.set.quizLock;
  const box = S.prog[w.id]?.box || 0;
  return box <= 1 ? 'mc' : box <= 3 ? 'spell' : 'dict';
}
```

- [ ] **Step 3: 构建并跑断言**

```bash
python3 src/build.py
```

浏览器里：

```js
const cases = [
  ['distance–time graph', 'distance time graph', true],
  ['distance–time graph', 'distance-time graph', true],
  ['half-life',           'halflife',            true],
  ['light-year',          'light year',          true],
  ['gravitational field strength', 'Gravitational Field Strength', true],
  ['specific heat capacity',       'specific heat capacty',        false]
];
const r = { 归一化: cases.map(([a, u, want]) => ({ 答案: a, 输入: u,
  对: (normAns(u) === normAns(a)) === want })) };

const d = diffHTML('potential diference', 'potential difference');
r.diff = { 缺字标绿: d.cor.includes('<b class="miss">f</b>'), 你写的无红: !d.you.includes('bad') };
const d2 = diffHTML('speeed', 'speed');
r.diff多字标红 = d2.you.includes('<b class="bad">e</b>');

const all = DATA.books.flatMap(b => b.words);
r.干扰项 = { 总词数: all.length,
  不足3个的: all.filter(w => distractors(w).length < 3).map(w => w.id),
  与答案重叠的: all.filter(w => { const t = zhToks(w.zh);
    return distractors(w).some(z => [...zhToks(z)].some(x => t.has(x))) }).map(w => w.id) };

const pd = BY_ID['phy:potential difference'];
r.电势差的干扰项 = distractors(pd);

S.set.quizLock = '';
r.题型 = { box0: quizType({ id: 'x', book: 'phy', sec: 1, zh: '' }),
  box3: (() => { S.prog['tmp'] = { box: 3 }; return quizType({ id: 'tmp', book: 'phy', sec: 1, zh: '' }) })(),
  box5: (() => { S.prog['tmp'] = { box: 5 }; return quizType({ id: 'tmp', book: 'phy', sec: 1, zh: '' }) })() };
S.set.quizLock = 'dict';
r.题型.锁定后 = quizType({ id: 'tmp', book: 'phy', sec: 1, zh: '' });
S.set.quizLock = ''; delete S.prog['tmp'];
JSON.stringify(r)
```

Expected：
- `归一化` 六条的 `对` 全为 `true`
- `diff.缺字标绿:true`、`你写的无红:true`、`diff多字标红:true`
- `干扰项.不足3个的` 与 `与答案重叠的` **都是空数组**
- `电势差的干扰项` 里**不含「电压」**
- `题型`：`box0:"mc"`、`box3:"spell"`、`box5:"dict"`、`锁定后:"dict"`

- [ ] **Step 4: 提交**

```bash
git add src/tpl.html index.html
git commit -m "$(cat <<'EOF'
feat: 测试的判分与出题纯函数

归一化抹平 U+2013 连字符与空格；干扰项排除与答案语义重叠的释义，
否则 potential difference 的选项里会混进 voltage，两个都对。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: 覆盖层样式、骨架与三种题型出题

**Files:**
- Modify: `src/tpl.html`（`<style>` 块里 `.credit` 规则之后，约 655 行）
- Modify: `src/tpl.html`（`#study` 覆盖层的 `</div>` 之后，约 700 行）
- Modify: `src/tpl.html`（Task 2 的纯函数之后继续插入）
- Modify: `src/tpl.html:1122-1129`（`renderList` 加入口按钮）

**Interfaces:**
- Consumes: Task 1 的 `sfxOK/sfxNo/sfxFinish`、Task 2 的四个纯函数
- Produces:
  - `startQuiz(pool: 词条[]): void` —— 开始测试
  - `drawQ(): void` —— 渲染当前题
  - 模块级状态 `POOL / POOLI / ROUND / Q / qi / wrong / t0 / answered / hinted / streak / best`

- [ ] **Step 1: 写断言，确认它失败**

```js
document.querySelector('[data-t=list]').click();
JSON.stringify({ 入口: !!document.getElementById('goQuiz'), 覆盖层: !!document.getElementById('quiz') })
```

Expected: FAIL —— `{"入口":false,"覆盖层":false}`

- [ ] **Step 2: 加 CSS**

在 `<style>` 块里 `.credit{…}` 那行（约 655 行）**之后**插入：

```css
/* ---------- 测试 ---------- */
.quiz{position:fixed;inset:0;background:var(--color-background-body);z-index:60;display:none;flex-direction:column}
.quiz.on{display:flex}
.qbar{display:flex;align-items:center;gap:var(--spacing-3);padding:calc(var(--safe-t) + 14px) var(--spacing-5) var(--spacing-2)}
.qbar .track{flex:1;height:4px;border-radius:var(--radius-full);background:var(--color-track);overflow:hidden}
.qbar .track i{display:block;height:100%;background:var(--color-accent);border-radius:var(--radius-full);transition:width var(--duration-medium) var(--ease-standard)}
.qbar .pg{font-size:var(--font-size-sm);color:var(--color-text-secondary);font-variant-numeric:tabular-nums}
/* 按钮放在可滚动正文里，不做固定底栏——iOS 键盘弹起时只缩视觉视口不缩布局视口，
   固定底栏会躲到键盘后面点不到 */
.qbody{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch;display:flex;flex-direction:column;
  padding:var(--spacing-4) var(--spacing-5) calc(var(--safe-b) + var(--spacing-6))}
.qact{margin-top:var(--spacing-4)}

.qtype{display:inline-flex;align-items:center;gap:5px;align-self:flex-start;
  padding:4px 10px;border-radius:var(--radius-full);background:var(--color-accent-muted);
  font-size:var(--font-size-xs);font-weight:var(--font-weight-semibold);color:var(--color-text-secondary)}
.qsec{font-size:var(--font-size-xs);color:var(--color-text-disabled);margin-top:6px}
.qprompt{margin-top:var(--spacing-4)}
.qprompt .zh{font-size:var(--font-size-3xl);font-weight:var(--font-weight-semibold);line-height:1.25;letter-spacing:-.01em}
.qprompt .en{font-size:var(--font-size-3xl);font-weight:var(--font-weight-semibold);letter-spacing:-.01em}
.qprompt .ipa{font-size:var(--font-size-base);color:var(--color-text-secondary);margin-top:4px}
.qzh{text-align:center;font-size:var(--font-size-base);color:var(--color-text-disabled);margin-top:10px}

.bigspk{width:96px;height:96px;border-radius:var(--radius-full);border:0;margin:var(--spacing-5) auto var(--spacing-2);
  background:var(--color-accent);color:var(--color-on-accent);display:flex;align-items:center;justify-content:center;
  transition:transform var(--duration-fast) var(--ease-standard)}
.bigspk:active{transform:scale(.94)}
.bigspk svg{width:40px;height:40px;stroke:currentColor;fill:none;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.bigspk-t{text-align:center;font-size:var(--font-size-sm);color:var(--color-text-secondary)}

.qin{width:100%;margin-top:var(--spacing-5);padding:15px var(--spacing-4);border-radius:var(--radius-element);
  border:var(--border-width) solid var(--color-border-emphasized);background:var(--color-background-card);
  font-family:inherit;font-size:var(--font-size-xl);color:var(--color-text-primary);text-align:center}
.qin:focus{outline:none;border-color:var(--color-accent)}
.qin.ok{border-color:var(--color-success)}
.qin.no{border-color:var(--color-error)}
.qhint{margin-top:10px;text-align:center;font-size:var(--font-size-xl);letter-spacing:.22em;
  color:var(--color-text-disabled);font-variant-numeric:tabular-nums;min-height:26px}
.qrow{display:flex;gap:8px;margin-top:var(--spacing-3)}
.qrow .btn{flex:1}

.opt{width:100%;margin-top:var(--spacing-2);padding:15px var(--spacing-4);text-align:left;
  font-family:inherit;font-size:var(--font-size-lg);color:inherit;
  transition:transform var(--duration-fast) var(--ease-standard)}
.opt:active{transform:scale(.985)}
.opt.ok{border-color:var(--color-success);background:var(--color-success-muted)}
.opt.no{border-color:var(--color-error);background:var(--color-error-muted)}
.opt .k{display:inline-block;width:22px;color:var(--color-text-disabled);font-weight:var(--font-weight-semibold)}
```

- [ ] **Step 3: 加覆盖层骨架**

在 `#study` 覆盖层的收尾 `</div>` **之后**（约 700 行，`<div class="toast" id="toast"></div>` 之前）插入：

```html
<div class="quiz" id="quiz">
  <div class="qbar">
    <button class="iconbtn" id="qClose"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
    <div class="track"><i id="qProg" style="width:0%"></i></div>
    <div class="pg" id="qPg">0/0</div>
  </div>
  <div class="qbody" id="qBody"></div>
</div>
```

- [ ] **Step 4: 加测试流程（出题部分）**

在 Task 2 的纯函数之后插入：

```js
/* ===================== 测试流程 ===================== */
const ROUND_N = 10;                       // 拼写要手打，10 题约 2-3 分钟，适合碎片时间
let POOL = [], POOLI = 0, ROUND = 0;
let Q = [], qi = 0, wrong = [], t0 = 0, answered = false, hinted = false;
let streak = 0, best = 0;

const TYPE_CN = { mc: '辨义 · 英译中', spell: '拼写 · 中译英', dict: '听写 · 听音拼写' };

function startQuiz(pool) {
  if (!pool || !pool.length) { toast('没有可测的词'); return; }
  POOL = shuffle(pool.slice()); POOLI = 0; ROUND = 0;
  $('quiz').classList.add('on');
  loadRound();
}
function loadRound() {
  ROUND++;
  Q = POOL.slice(POOLI, POOLI + ROUND_N);
  if (!Q.length) { POOL = shuffle(POOL); POOLI = 0; ROUND = 1; Q = POOL.slice(0, ROUND_N); }
  qi = 0; wrong = []; streak = 0; best = 0; t0 = Date.now();
  drawQ();
}
$('qClose').onclick = () => {
  stopSpeak();
  $('quiz').classList.remove('on');
  document.body.classList.remove('typing');
  render();                               // 测试改了进度，回去要刷新词表/学习页
};

/* 顶栏的连对徽章。答题前后都要重画，否则会慢一拍 */
function paintPg() {
  $('qPg').innerHTML = (streak >= 2
      ? `<span class="streak${streak >= 5 ? ' hot' : ''}">连对 ${streak}</span> ` : '')
    + `${qi + 1}/${Q.length}`;
}

function drawQ() {
  answered = false; hinted = false;
  const w = Q[qi], t = quizType(w);
  paintPg();
  $('qProg').style.width = (qi / Q.length * 100) + '%';
  let h = `<span class="qtype">${TYPE_CN[t]}</span><div class="qsec">${esc(w.secName)}</div>`;

  if (t === 'mc') {
    const opts = shuffle([w.zh, ...distractors(w)]);
    h += `<div class="qprompt"><div class="en">${esc(w.w)}</div><div class="ipa">${esc(w.ipa)}</div></div>
      <div style="margin-top:18px">`
      + opts.map((o, i) => `<button class="card opt" data-opt="${esc(o)}">
          <span class="k">${'ABCD'[i]}</span>${esc(o)}</button>`).join('')
      + `</div>`;
    $('qBody').innerHTML = h;
    document.body.classList.remove('typing');      // 辨义题没有输入框
    say(w.w);
    $('qBody').querySelectorAll('.opt').forEach(b => b.onclick = () => pickMC(b, w));
  } else {
    const isDict = t === 'dict';
    h += isDict
      ? `<button class="bigspk" id="bigSpk">${IC.spk}</button>
         <div class="bigspk-t">点喇叭重听</div>
         <div class="qzh">${esc(w.zh)}</div>`
      : `<div class="qprompt"><div class="zh">${esc(w.zh)}</div></div>`;
    h += `<input class="qin" id="qIn" placeholder="${isDict ? '输入你听到的词' : '输入英文'}"
            autocapitalize="off" autocorrect="off" spellcheck="false" autocomplete="off"
            enterkeyhint="done">
          <div class="qhint" id="qHint"></div>
          <div class="qrow">
            <button class="btn line" id="bHint">首字母提示</button>
            <button class="btn line" id="bSay">${IC.spk} 听发音</button>
          </div>
          <div class="qact"><button class="btn pri blk" id="bSubmit">提交</button></div>`;
    $('qBody').innerHTML = h;
    if (isDict) { say(w.w); $('bigSpk').onclick = () => say(w.w); }
    const inp = $('qIn'); inp.focus();
    document.body.classList.add('typing');
    inp.onfocus = () => document.body.classList.add('typing');
    inp.onblur  = () => document.body.classList.remove('typing');
    inp.onkeydown = e => { if (e.key === 'Enter') { e.preventDefault(); submit(w); } };
    $('bSubmit').onclick = () => submit(w);
    $('bSay').onclick = () => say(w.w);
    $('bHint').onclick = () => {
      hinted = true;
      $('qHint').textContent = w.w.split(' ')
        .map(p => p[0] + '_'.repeat(Math.max(0, p.length - 1))).join('  ');
    };
  }
}
```

本任务里 `pickMC` 与 `submit` 还不存在 —— Task 4 补。先加两个空壳放在
`drawQ` 之后，让出题能跑通：

```js
function pickMC(btn, w) { }
function submit(w) { }
```

- [ ] **Step 5: 词表页加入口**

`renderList()`（约 1122 行）的 `view.innerHTML` 改成（**测试按钮在搜索框上方**）：

```js
  const pool = quizPool();
  view.innerHTML = `
    ${bookBarHTML()}
    <button class="btn pri blk" id="goQuiz" style="margin-top:12px">测试这 ${pool.length} 个词 →</button>
    <div style="display:flex;gap:8px;margin-top:8px">
      <input class="search" id="q" placeholder="搜索单词或中文…" value="${esc(q)}">
      <button class="btn ${S.set.maskZh ? 'pri' : 'line'}" id="mask" style="flex:0 0 auto">${S.set.maskZh ? '显示' : '遮住'}中文</button>
    </div>
    <div id="rows"></div>`;
```

在 `bindBookBar();` 之后加：

```js
  $('goQuiz').onclick = () => startQuiz(quizPool());
```

并在 `renderList` **之前**加一个取范围的函数（与 `draw()` 里的筛选口径完全一致）：

```js
/* 测试范围＝词表页当前筛选出的这批词。有关键词时跨科，与列表显示的口径一致 */
function quizPool() {
  const kw = q.trim().toLowerCase();
  const hit = w => !kw || w.w.toLowerCase().includes(kw) || w.zh.includes(kw);
  const books = kw ? [curBook(), ...DATA.books.filter(b => b.id !== S.set.book)] : [curBook()];
  return books.flatMap(bk => bk.words.filter(hit));
}
```

`$('q').oninput` 改成同时刷新按钮文案：

```js
  $('q').oninput = e => { q = e.target.value; renderList(); $('q').focus(); };
```

- [ ] **Step 6: 构建并验证**

```bash
python3 src/build.py
```

浏览器里（`localStorage.clear(); location.reload()` 后）：

```js
const r = {};
document.querySelector('[data-t=list]').click();
r.入口文案 = document.getElementById('goQuiz').textContent.trim();
r.范围 = quizPool().length;

S.set.quizLock = 'mc';
document.getElementById('goQuiz').click();
r.覆盖层打开 = document.getElementById('quiz').classList.contains('on');
r.本轮题数 = Q.length;
r.辨义 = { 题型标签: document.querySelector('.qtype').textContent,
  选项数: document.querySelectorAll('.opt').length,
  选项含答案: [...document.querySelectorAll('.opt')].some(b => b.dataset.opt === Q[0].zh) };

S.set.quizLock = 'spell'; drawQ();
r.拼写 = { 有输入框: !!document.getElementById('qIn'), 有提交: !!document.getElementById('bSubmit'),
  题面是中文: document.querySelector('.qprompt .zh').textContent === Q[0].zh };

S.set.quizLock = 'dict'; drawQ();
r.听写 = { 有喇叭: !!document.getElementById('bigSpk'),
  有中文兜底: document.querySelector('.qzh').textContent === Q[0].zh,
  无题面: !document.querySelector('.qprompt') };

document.getElementById('bHint').click();
r.提示 = document.getElementById('qHint').textContent;

S.set.quizLock = '';
document.getElementById('qClose').click();
r.关闭后 = document.getElementById('quiz').classList.contains('on');
JSON.stringify(r)
```

Expected：`入口文案` 形如 `测试这 186 个词 →`（数字与 `范围` 一致）、
`覆盖层打开:true`、`本轮题数:10`、辨义 4 个选项且含答案、
拼写有输入框与提交且题面是中文、听写有喇叭与中文兜底且无 `.qprompt`、
`提示` 是形如 `h________` 的下划线串、`关闭后:false`。

`read_console_messages {onlyErrors:true}` 应无输出。

- [ ] **Step 7: 提交**

```bash
git add src/tpl.html index.html
git commit -m "$(cat <<'EOF'
feat: 测试覆盖层与三种题型出题

动作按钮放在可滚动正文里不做固定底栏，避开 iOS 键盘遮挡。
入口在词表页搜索框上方，范围＝当前筛选结果。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: 作答、判分反馈与喂回间隔重复

**Files:**
- Modify: `src/tpl.html`（Task 3 的 `pickMC` / `submit` 空壳替换，并新增 `feedback` / `next`）
- Modify: `src/tpl.html`（`<style>` 里 Task 3 的 CSS 之后加反馈卡样式）

**Interfaces:**
- Consumes: Task 2 的 `normAns` / `diffHTML`、现有的 `grade(id, g)` / `rec(id)` / `say()`
- Produces: `pickMC(btn, w)`、`submit(w)`、`feedback(w, ok, d)`、`next()`

- [ ] **Step 1: 写断言，确认它失败**

```js
S.set.quizLock = 'spell';
document.querySelector('[data-t=list]').click();
document.getElementById('goQuiz').click();
const w = Q[0];
document.getElementById('qIn').value = w.w;
document.getElementById('bSubmit').click();
JSON.stringify({ 有反馈卡: !!document.querySelector('.fb'),
  进度已记: !!S.prog[w.id], 有下一题: !!document.getElementById('bNext') })
```

Expected: FAIL —— 三项都是 `false`

- [ ] **Step 2: 加反馈卡 CSS**

在 Task 3 的 CSS 之后插入：

```css
.fb{margin-top:var(--spacing-5);padding:var(--spacing-4)}
.fb .tag{font-size:var(--font-size-base);font-weight:var(--font-weight-semibold)}
.fb .tag.ok{color:var(--color-success)}
.fb .tag.no{color:var(--color-error)}
.fb .ans{font-size:var(--font-size-xl);font-weight:var(--font-weight-semibold);margin-top:8px;word-break:break-word}
.fb .yours{font-size:var(--font-size-base);color:var(--color-text-secondary);margin-top:6px;word-break:break-word}
.fb .zh{font-size:var(--font-size-base);color:var(--color-text-secondary);margin-top:6px}
.fb b.bad{color:var(--color-error);background:var(--color-error-muted);border-radius:3px}
.fb b.miss{color:var(--color-success);background:var(--color-success-muted);border-radius:3px}
```

- [ ] **Step 3: 实现作答与反馈**

把 Task 3 的两个空壳替换成：

```js
/* 测试结果就是复习结果，直接喂现有的间隔重复，不分裂成两套记录。
   用了提示即使答对也只按「模糊」记，不给满级晋升。 */
function score(w, ok) {
  if (ok) { streak++; best = Math.max(best, streak); sfxOK(streak); }
  else    { streak = 0; sfxNo(); }
  grade(w.id, ok ? (hinted ? 1 : 2) : 0);
  paintPg();
}

function pickMC(btn, w) {
  if (answered) return; answered = true;
  const ok = btn.dataset.opt === w.zh;
  $('qBody').querySelectorAll('.opt').forEach(b => {
    if (b.dataset.opt === w.zh) b.classList.add('ok');
    else if (b === btn) b.classList.add('no');
    b.onclick = null;
  });
  if (!ok) wrong.push({ w, your: btn.dataset.opt });
  score(w, ok);
  feedback(w, ok, null);
}

function submit(w) {
  if (answered) return;
  const v = $('qIn').value.trim();
  if (!v) return;
  answered = true;
  const ok = normAns(v) === normAns(w.w);
  $('qIn').classList.add(ok ? 'ok' : 'no');
  $('qIn').disabled = true;
  if (!ok) wrong.push({ w, your: v });
  score(w, ok);
  feedback(w, ok, ok ? null : diffHTML(v, w.w));
  setTimeout(() => say(w.w), 340);            // 让音效先响完，别和朗读糊在一起
}

function feedback(w, ok, d) {
  document.body.classList.remove('typing');
  const sb = $('bSubmit'); if (sb) sb.parentElement.remove();   // 用过的提交按钮收走
  const grade = !ok ? '记为「忘记」' : hinted ? '用了提示，记为「模糊」' : '记为「记得」';
  let h = `<div class="card fb">
    <div class="tag ${ok ? 'ok' : 'no'}">${ok ? IC.tick + '正确' : '✗ 不对'}
      <span style="color:var(--color-text-disabled);font-weight:400">· ${grade}</span></div>
    <div class="ans">${d ? d.cor : esc(w.w)}</div>`;
  if (d) h += `<div class="yours">你写的：${d.you}</div>`;
  h += `<div class="zh">${esc(w.zh)} · ${esc(w.ipa)}</div>
    <div style="margin-top:12px"><button class="btn line tiny" id="fbSay">${IC.spk} 再听一次</button></div>
  </div>
  <div class="qact"><button class="btn pri blk" id="bNext">${qi < Q.length - 1 ? '下一题' : '看结果'}</button></div>`;
  $('qBody').insertAdjacentHTML('beforeend', h);
  $('fbSay').onclick = () => say(w.w);
  $('bNext').onclick = next;
  // 键盘可能还开着，把「下一题」滚进可见区
  $('bNext').scrollIntoView({ block: 'nearest' });
}

function next() {
  if (qi < Q.length - 1) { qi++; drawQ(); } else result();
}
function result() { }        // Task 6 补
```

`IC.tick` 的 SVG 需要一个类名才能上色，把 `feedback` 里的 `IC.tick` 换成：

```js
    <div class="tag ${ok ? 'ok' : 'no'}">${ok ? '<svg class="tick" viewBox="0 0 24 24"><path d="M5 12.6l4.6 4.6L19 7.6"/></svg>正确' : '✗ 不对'}
```

并在 CSS 里加（动效在 Task 5 补，这里先给静态样式）：

```css
.tick{width:22px;height:22px;vertical-align:-4px;margin-right:2px}
.tick path{stroke:var(--color-success);stroke-width:2.8;fill:none;stroke-linecap:round;stroke-linejoin:round}
```

- [ ] **Step 4: 构建并验证**

```bash
python3 src/build.py
```

浏览器里（`localStorage.clear(); location.reload()` 后）：

```js
const r = {};
S.set.quizLock = 'spell';
document.querySelector('[data-t=list]').click();
document.getElementById('goQuiz').click();

// 答对、没用提示 → box 应升到 1
let w = Q[0];
document.getElementById('qIn').value = w.w;
document.getElementById('bSubmit').click();
r.答对 = { 标签: document.querySelector('.fb .tag').textContent.replace(/\s+/g,' ').trim(),
  box: S.prog[w.id].box, seen: S.prog[w.id].seen, 有下一题: !!document.getElementById('bNext'),
  提交已移除: !document.getElementById('bSubmit') };

document.getElementById('bNext').click();
// 用提示后答对 → 只按「模糊」
w = Q[qi];
document.getElementById('bHint').click();
document.getElementById('qIn').value = w.w;
document.getElementById('bSubmit').click();
r.提示后答对 = { 标签: document.querySelector('.fb .tag').textContent.replace(/\s+/g,' ').trim(),
  box: S.prog[w.id].box };

document.getElementById('bNext').click();
// 答错 → box 归零、wrong 记录、diff 有标注
w = Q[qi];
document.getElementById('qIn').value = 'zzzwrong';
document.getElementById('bSubmit').click();
r.答错 = { box: S.prog[w.id].box, wrong数: wrong.length,
  有你写的: !!document.querySelector('.fb .yours'),
  有红标: !!document.querySelector('.fb b.bad') };

S.set.quizLock = '';
JSON.stringify(r)
```

Expected：
- `答对`：标签含「正确 · 记为「记得」」、`box:1`、`seen:1`、`有下一题:true`、`提交已移除:true`
- `提示后答对`：标签含「用了提示，记为「模糊」」、`box:1`
- `答错`：`box:0`、`wrong数:1`、`有你写的:true`、`有红标:true`

再验证辨义题的作答：

```js
S.set.quizLock = 'mc'; drawQ();
const w = Q[qi];
const wrongBtn = [...document.querySelectorAll('.opt')].find(b => b.dataset.opt !== w.zh);
wrongBtn.click();
const r = { 选错标红: wrongBtn.classList.contains('no'),
  正确项标绿: [...document.querySelectorAll('.opt')].some(b => b.dataset.opt === w.zh && b.classList.contains('ok')),
  box: S.prog[w.id].box };
S.set.quizLock = '';
JSON.stringify(r)
```

Expected: `选错标红:true`、`正确项标绿:true`、`box:0`

`read_console_messages {onlyErrors:true}` 应无输出。

- [ ] **Step 5: 提交**

```bash
git add src/tpl.html index.html
git commit -m "$(cat <<'EOF'
feat: 测试的作答、判分反馈与间隔重复接入

答对无提示记「记得」、用了提示记「模糊」、答错记「忘记」，
直接喂现有的 grade()，不另起一套进度。错的用字符级 diff 标出来。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: 连对徽章与奖励动效

**Files:**
- Modify: `src/tpl.html`（`<style>` 里 Task 4 的 CSS 之后）
- Modify: `src/tpl.html`（`feedback()` 里加连对徽章）

**Interfaces:**
- Consumes: Task 4 的 `score()` / `feedback()`、Task 3 的 `paintPg()`
- Produces: `.streak` / `.tick` 动画、`.qin.no` 抖动、`.confetti` 彩纸；`confettiHTML(): string`

- [ ] **Step 1: 写断言，确认它失败**

```js
JSON.stringify({ 彩纸函数: typeof confettiHTML,
  有streak样式: [...document.styleSheets].some(ss => { try { return [...ss.cssRules].some(r => r.selectorText === '.streak') } catch(e) { return false } }) })
```

Expected: FAIL —— `{"彩纸函数":"undefined","有streak样式":false}`

- [ ] **Step 2: 加动效 CSS**

在 Task 4 的 CSS 之后插入（`.tick` 那两条规则替换成带动画的版本）：

```css
/* 奖励动效。全部受下面的 prefers-reduced-motion 兜底约束 */
@keyframes pop{0%{transform:scale(.9);opacity:0}60%{transform:scale(1.02)}100%{transform:scale(1);opacity:1}}
.fb{animation:pop .3s var(--ease-standard) both}
@keyframes draw{to{stroke-dashoffset:0}}
.tick{width:22px;height:22px;vertical-align:-4px;margin-right:2px}
.tick path{stroke:var(--color-success);stroke-width:2.8;fill:none;stroke-linecap:round;stroke-linejoin:round;
  stroke-dasharray:26;stroke-dashoffset:26;animation:draw .32s .05s var(--ease-standard) forwards}
@keyframes shake{15%{transform:translateX(-5px)}30%{transform:translateX(5px)}45%{transform:translateX(-4px)}
  60%{transform:translateX(4px)}80%{transform:translateX(-2px)}100%{transform:translateX(0)}}
.qin.no{animation:shake .38s var(--ease-standard)}

@keyframes streakPop{0%{transform:scale(.6);opacity:0}55%{transform:scale(1.18)}100%{transform:scale(1);opacity:1}}
.streak{display:inline-flex;align-items:center;gap:4px;padding:3px 9px;border-radius:var(--radius-full);
  background:var(--color-warning-muted);color:var(--color-text-yellow);
  font-size:var(--font-size-xs);font-weight:var(--font-weight-semibold);
  font-variant-numeric:tabular-nums;animation:streakPop .28s var(--ease-standard) both}
.streak.hot{background:var(--color-success-muted);color:var(--color-text-green)}

/* 满分彩纸：14 个小方块，纯 CSS，900ms 后自己消失 */
.confetti{position:absolute;inset:0;overflow:hidden;pointer-events:none}
.confetti i{position:absolute;left:50%;top:34%;width:8px;height:8px;border-radius:2px;opacity:0;
  animation:burst .9s var(--ease-standard) forwards}
@keyframes burst{0%{opacity:1;transform:translate(0,0) rotate(0)}
  100%{opacity:0;transform:translate(var(--dx),var(--dy)) rotate(var(--rot))}}

@media (prefers-reduced-motion: reduce){
  .fb,.streak,.qin.no,.confetti i{animation:none}
  .tick path{animation:none;stroke-dashoffset:0}
  .confetti{display:none}
}
```

- [ ] **Step 3: 反馈卡加连对徽章，并加彩纸生成函数**

`feedback()` 里，把 `· ${grade}</span></div>` 那一段改成：

```js
      <span style="color:var(--color-text-disabled);font-weight:400">· ${grade}</span>`
    + (ok && streak >= 3 ? ` <span class="streak${streak >= 5 ? ' hot' : ''}">连对 ${streak}</span>` : '')
    + `</div>
```

在 `next()` 之后加：

```js
function confettiHTML() {
  const cols = ['var(--color-success)', 'var(--color-warning)', 'var(--color-brand)', 'var(--color-error)'];
  let h = '<div class="confetti">';
  for (let i = 0; i < 14; i++) {
    const ang = (i / 14) * Math.PI * 2 + Math.random() * .4, dist = 90 + Math.random() * 110;
    h += `<i style="background:${cols[i % 4]};--dx:${(Math.cos(ang) * dist).toFixed(0)}px;`
       + `--dy:${(Math.sin(ang) * dist + 40).toFixed(0)}px;--rot:${(Math.random() * 540 - 270).toFixed(0)}deg;`
       + `animation-delay:${i * 14}ms"></i>`;
  }
  return h + '</div>';
}
```

- [ ] **Step 4: 构建并验证**

```bash
python3 src/build.py
```

浏览器里（`localStorage.clear(); location.reload()` 后）：

```js
const r = {};
S.set.quizLock = 'spell';
document.querySelector('[data-t=list]').click();
document.getElementById('goQuiz').click();
const ans = () => { document.getElementById('qIn').value = Q[qi].w; document.getElementById('bSubmit').click(); };
const nxt = () => document.getElementById('bNext').click();
ans(); nxt(); ans(); nxt();
r.连对2时顶栏 = document.getElementById('qPg').innerHTML;
ans();
r.连对3时反馈卡有徽章 = !!document.querySelector('.fb .streak');
r.顶栏与反馈卡一致 = document.getElementById('qPg').innerHTML.includes('连对 3');
nxt();
// 答错 → 抖动类 + 连对清零
document.getElementById('qIn').value = 'zzz';
document.getElementById('bSubmit').click();
r.答错 = { 抖动类: document.getElementById('qIn').classList.contains('no'), 连对: streak };
r.彩纸 = (() => { const d = document.createElement('div'); d.innerHTML = confettiHTML();
  return { 片数: d.querySelectorAll('i').length,
           带变量: d.querySelector('i').getAttribute('style').includes('--dx') } })();
S.set.quizLock = '';
JSON.stringify(r)
```

Expected：`连对2时顶栏` 含 `<span class="streak">连对 2</span>`、
`连对3时反馈卡有徽章:true`、`顶栏与反馈卡一致:true`、
`答错.抖动类:true`、`答错.连对:0`、`彩纸.片数:14`、`带变量:true`

再截图确认打勾是绿色、徽章在深浅色下都看得清：
`resize_window {preset:"mobile"}` → 答对一题 → `computer {action:"screenshot"}`；
`document.documentElement.classList.add('dark')` 后再截一张，截完移除该 class。

- [ ] **Step 5: 提交**

```bash
git add src/tpl.html index.html
git commit -m "$(cat <<'EOF'
feat: 测试的连对徽章与奖励动效

打勾自己画出来、答错抖动、连对 2 起顶栏挂徽章、5 起变绿。
全部包在 prefers-reduced-motion 兜底里。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: 轮次与结果页

**Files:**
- Modify: `src/tpl.html`（`result()` 空壳替换）
- Modify: `src/tpl.html`（`<style>` 里 Task 5 的 CSS 之后加结果页样式）

**Interfaces:**
- Consumes: Task 5 的 `confettiHTML()`、Task 1 的 `sfxFinish()`、Task 3 的 `POOL/POOLI/ROUND/loadRound`
- Produces: `result()`、`nextRound()`、`redoRound()`、`restLeft()`

- [ ] **Step 1: 写断言，确认它失败**

```js
JSON.stringify([typeof nextRound, typeof redoRound, typeof restLeft])
```

Expected: FAIL —— 三个都是 `"undefined"`

- [ ] **Step 2: 加结果页 CSS**

```css
.res{padding:var(--spacing-5) 0;position:relative}
.res .big{text-align:center;font-size:var(--font-size-5xl);font-weight:var(--font-weight-bold);letter-spacing:-.03em}
.res .sub{text-align:center;font-size:var(--font-size-base);color:var(--color-text-secondary);margin-top:4px}
.wrongrow{display:flex;align-items:flex-start;gap:10px;padding:11px var(--spacing-4);border-bottom:var(--border-width) solid var(--color-border)}
.wrongrow:last-child{border-bottom:0}
.wrongrow .bd{flex:1;min-width:0}
.wrongrow .w{font-weight:var(--font-weight-semibold)}
.wrongrow .z{font-size:var(--font-size-sm);color:var(--color-text-secondary);margin-top:2px}
.wrongrow .u{font-size:var(--font-size-sm);color:var(--color-error);margin-top:2px}
```

- [ ] **Step 3: 实现轮次与结果页**

把 `function result() { }` 替换成：

```js
const nextRound = () => { POOLI += Q.length; loadRound(); };
const redoRound = () => { ROUND--; loadRound(); };      // POOLI 不动，重取同一批
const restLeft  = () => Math.max(0, POOL.length - POOLI - Q.length);

function result() {
  const right = Q.length - wrong.length, perfect = !wrong.length;
  const sec = Math.round((Date.now() - t0) / 1000);
  const mm = String(Math.floor(sec / 60)), ss = String(sec % 60).padStart(2, '0');
  $('qPg').textContent = `${Q.length}/${Q.length}`;
  $('qProg').style.width = '100%';
  document.body.classList.remove('typing');
  sfxFinish(perfect);
  const left = restLeft();
  let h = `<div class="res">
      ${perfect ? confettiHTML() : ''}
      <div class="big">${right}/${Q.length}</div>
      <div class="sub">第 ${ROUND} 轮 · 用时 ${mm}:${ss} · 最长连对 ${best}</div>
    </div>`;
  if (wrong.length) {
    h += `<div class="sec-t">错题 ${wrong.length}</div><div class="card">`
      + wrong.map(x => `<div class="wrongrow">
          <span class="iconbtn" data-say="${esc(x.w.w)}">${IC.spk}</span>
          <div class="bd"><div class="w">${esc(x.w.w)}</div>
            <div class="z">${esc(x.w.zh)}</div>
            <div class="u">你的答案：${esc(x.your)}</div></div>
        </div>`).join('') + `</div>`;
  } else {
    h += `<div class="credit" style="margin-top:20px">全对，这批词可以往下一档题型走了</div>`;
  }
  h += `<div class="credit">${left ? '这批还剩 ' + left + ' 词没测' : '这批词已经测完一遍'}</div>`;
  h += `<div class="qact">`
    + (wrong.length
      ? `<div class="qrow"><button class="btn pri" id="bWrong">只练错题</button>
         <button class="btn line" id="bNextR">${left ? '下一轮' : '再来一轮'}</button></div>`
      : `<button class="btn pri blk" id="bNextR">${left ? '下一轮 10 题' : '再来一轮'}</button>`)
    + `<button class="btn line blk" id="bRedo" style="margin-top:8px">重做本轮</button></div>`;
  $('qBody').innerHTML = h;
  $('qBody').onclick = e => { const s = e.target.closest('[data-say]'); if (s) say(s.dataset.say); };
  $('bNextR').onclick = nextRound;
  $('bRedo').onclick  = redoRound;
  if (wrong.length) $('bWrong').onclick = () => startQuiz(wrong.map(x => x.w));
}
```

注意 `result()` 给 `$('qBody')` 挂了 `onclick`，`drawQ()` 每次重设 `innerHTML`
但不清 `onclick` —— 在 `drawQ()` 开头加一行清掉，免得在答题页误触发朗读：

```js
function drawQ() {
  $('qBody').onclick = null;
  answered = false; hinted = false;
```

- [ ] **Step 4: 构建并验证**

```bash
python3 src/build.py
```

浏览器里（`localStorage.clear(); location.reload()` 后）：

```js
const r = {};
S.set.quizLock = 'spell';
document.querySelector('[data-t=list]').click();
document.getElementById('goQuiz').click();
const r1 = Q.map(w => w.w);
const run = (bad) => { for (let k = 0; k < 10; k++) {
  document.getElementById('qIn').value = (bad && k === 2) ? 'zzz' : Q[qi].w;
  document.getElementById('bSubmit').click(); document.getElementById('bNext').click(); } };
run(true);
r.有错题时按钮 = [...document.querySelectorAll('.qact button')].map(b => b.textContent.trim());
r.错题行 = document.querySelectorAll('.wrongrow').length;
r.剩余文案 = [...document.querySelectorAll('.credit')].map(e => e.textContent.trim());

document.getElementById('bRedo').click();
r.重做取到同一批 = JSON.stringify(Q.map(w => w.w)) === JSON.stringify(r1);
run(false);
r.全对时彩纸 = document.querySelectorAll('.confetti i').length;
r.全对时按钮 = [...document.querySelectorAll('.qact button')].map(b => b.textContent.trim());

document.getElementById('bNextR').click();
const r2 = Q.map(w => w.w);
r.下一轮零重叠 = r2.every(w => !r1.includes(w));
r.轮次 = ROUND; r.游标 = POOLI; r.剩余 = restLeft();
S.set.quizLock = '';
JSON.stringify(r)
```

Expected：
- `有错题时按钮:["只练错题","下一轮","重做本轮"]`、`错题行:1`
- `剩余文案` 含形如 `这批还剩 176 词没测`
- `重做取到同一批:true`
- `全对时彩纸:14`、`全对时按钮:["下一轮 10 题","重做本轮"]`
- `下一轮零重叠:true`、`轮次:2`、`游标:10`

再验证「只练错题」：

```js
S.set.quizLock = 'spell';
document.querySelector('[data-t=list]').click();
document.getElementById('goQuiz').click();
for (let k = 0; k < 10; k++) { document.getElementById('qIn').value = k < 3 ? 'zzz' : Q[qi].w;
  document.getElementById('bSubmit').click(); document.getElementById('bNext').click(); }
const before = wrong.map(x => x.w.id);
document.getElementById('bWrong').click();
const r = { 错题数: before.length, 新池: POOL.length, 新轮题数: Q.length,
  只含错题: Q.every(w => before.includes(w.id)) };
S.set.quizLock = '';
JSON.stringify(r)
```

Expected: `错题数:3`、`新池:3`、`新轮题数:3`、`只含错题:true`

`read_console_messages {onlyErrors:true}` 应无输出。

- [ ] **Step 5: 提交**

```bash
git add src/tpl.html index.html
git commit -m "$(cat <<'EOF'
feat: 测试的轮次与结果页

一轮 10 题；下一轮从同一批词里接着取、与上一轮零重叠；重做本轮原样再来。
全对放彩纸。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: 题型选择器

**Files:**
- Modify: `src/tpl.html`（`#quiz` 骨架加底栏）
- Modify: `src/tpl.html`（`<style>` 里 Task 6 的 CSS 之后）
- Modify: `src/tpl.html`（`startQuiz` 里绑定事件）

**Interfaces:**
- Consumes: `S.set.quizLock`（Task 1 已加进 `DEF.set`）、Task 3 的 `drawQ()`
- Produces: `bindQuizLock(): void`

- [ ] **Step 1: 写断言，确认它失败**

```js
document.querySelector('[data-t=list]').click();
document.getElementById('goQuiz').click();
JSON.stringify({ 选择器: !!document.querySelector('.qlock'),
  按钮: [...document.querySelectorAll('.qlock button')].map(b => b.textContent.trim()) })
```

Expected: FAIL —— `{"选择器":false,"按钮":[]}`

- [ ] **Step 2: 加 CSS**

```css
/* 题型选择器。打字时整条收起——用不到，且 iOS 键盘弹起时固定底栏会飘到
   键盘上方，正好压住「提交」 */
.qlock{flex:0 0 auto;display:flex;gap:6px;justify-content:center;
  padding:9px var(--spacing-4) calc(var(--safe-b) + 9px);
  border-top:var(--border-width) solid var(--color-border);
  background:var(--color-background-card);
  transition:opacity var(--duration-fast) var(--ease-standard),
             transform var(--duration-fast) var(--ease-standard)}
.qlock button{flex:0 0 auto;background:var(--color-background-muted);border:0;color:var(--color-text-secondary);
  font-family:inherit;font-size:var(--font-size-sm);font-weight:var(--font-weight-medium);
  padding:7px 13px;border-radius:var(--radius-full);white-space:nowrap}
.qlock button.on{background:var(--color-accent);color:var(--color-on-accent);font-weight:var(--font-weight-semibold)}
body.typing .qlock{opacity:0;pointer-events:none;transform:translateY(100%)}
@media (prefers-reduced-motion: reduce){ .qlock{transition:none} }
```

- [ ] **Step 3: 骨架加底栏**

`#quiz` 里 `<div class="qbody" id="qBody"></div>` **之后**加：

```html
  <div class="qlock" id="qLock">
    <button data-lk="spell">拼写</button>
    <button data-lk="mc">辨义</button>
    <button data-lk="dict">听写</button>
    <button data-lk="">智能</button>
  </div>
```

- [ ] **Step 4: 绑定**

在 `loadRound()` 之后加：

```js
/* 顺序是 拼写/辨义/听写/智能，默认「智能」跟记忆盒子自动升级 */
function bindQuizLock() {
  $('qLock').querySelectorAll('button').forEach(b => {
    b.classList.toggle('on', b.dataset.lk === S.set.quizLock);
    b.onclick = () => {
      S.set.quizLock = b.dataset.lk; save();
      $('qLock').querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
      if (!answered) drawQ();              // 换题型立即重绘当前题；已作答的不动，免得丢反馈
    };
  });
}
```

`startQuiz()` 里 `$('quiz').classList.add('on');` 之后加一行：

```js
  bindQuizLock();
```

- [ ] **Step 5: 构建并验证**

```bash
python3 src/build.py
```

浏览器里（`localStorage.clear(); location.reload()` 后）：

```js
const r = {};
document.querySelector('[data-t=list]').click();
document.getElementById('goQuiz').click();
r.顺序 = [...document.querySelectorAll('.qlock button')].map(b => b.textContent.trim());
r.默认选中 = document.querySelector('.qlock button.on').textContent.trim();

document.querySelector('.qlock [data-lk=spell]').click();
r.锁拼写 = { 有输入框: !!document.getElementById('qIn'), 设置: S.set.quizLock,
  已持久化: JSON.parse(localStorage.getItem('igcse-flashcard-v1')).set.quizLock };
r.打字时body = document.body.className;

document.querySelector('.qlock [data-lk=mc]').click();
r.锁辨义 = { 有选项: document.querySelectorAll('.opt').length, body: document.body.className };

document.querySelector('.qlock [data-lk=dict]').click();
r.锁听写 = { 有喇叭: !!document.getElementById('bigSpk') };

// 已作答后切题型不应重绘（否则会把反馈冲掉）
document.getElementById('qIn').value = Q[qi].w;
document.getElementById('bSubmit').click();
document.querySelector('.qlock [data-lk=spell]').click();
r.答完后切题型保留反馈 = !!document.querySelector('.fb');

document.querySelector('.qlock [data-lk=""]').click();
r.回到智能 = S.set.quizLock;
JSON.stringify(r)
```

Expected：`顺序:["拼写","辨义","听写","智能"]`、`默认选中:"智能"`、
`锁拼写.有输入框:true` 且 `设置:"spell"` 且 `已持久化:"spell"`、
`打字时body` 含 `typing`、`锁辨义.有选项:4` 且 body **不含** `typing`、
`锁听写.有喇叭:true`、`答完后切题型保留反馈:true`、`回到智能:""`

**用截图验证收起行为**（`getComputedStyle` 读 opacity 不可靠）：
锁到「拼写」让输入框自动聚焦后截一张（底栏应不可见），
再 `document.getElementById('qIn').blur()` 截一张（底栏应回来）。

- [ ] **Step 6: 提交**

```bash
git add src/tpl.html index.html
git commit -m "$(cat <<'EOF'
feat: 测试的题型选择器

顺序 拼写/辨义/听写/智能，默认智能。输入框聚焦时整条收起——
iOS 键盘弹起时固定底栏会飘上来压住「提交」。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: 修 `100vh` 顺序与 viewport meta

**Files:**
- Modify: `src/tpl.html:5`（viewport meta）
- Modify: `src/tpl.html:146`（`#app` 高度）

**Interfaces:** 无

**背景：** 这是既有 bug，不属于测试功能，但同一个「底部被遮住」的问题域，一并修。
`#app{height:100dvh;height:100vh}` 两条顺序写反了 —— 后写的 `100vh` 生效，
而 iOS Safari 的 `100vh` 是**不含底部地址栏**的大视口，所以在 Safari 里正常浏览时
底部 Tab 栏会被 Safari 自己的地址栏压住。加到主屏幕当 PWA 用没有地址栏，所以一直没暴露。

- [ ] **Step 1: 写断言，确认它失败**

```bash
grep -n "height:100dvh;height:100vh" src/tpl.html
grep -n "interactive-widget" src/tpl.html
```

Expected: 第一条**有输出**（说明顺序还是错的），第二条**无输出**。

- [ ] **Step 2: 改两行**

`src/tpl.html:146`：

```css
/* 100vh 兜底，支持 dvh 的浏览器用 dvh —— iOS Safari 的 100vh 不含底部地址栏，
   直接用会让底部 Tab 栏被地址栏压住 */
#app{height:100vh;height:100dvh;display:flex;flex-direction:column}
```

`src/tpl.html:5`：

```html
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,maximum-scale=1,user-scalable=no,interactive-widget=resizes-content">
```

（`interactive-widget=resizes-content` 让 Android Chrome 把键盘算进视口；iOS 忽略该值，无副作用。）

- [ ] **Step 3: 构建并验证**

```bash
python3 src/build.py
grep -c "height:100vh;height:100dvh" src/tpl.html
grep -c "interactive-widget=resizes-content" index.html
```

Expected: 两条 `grep -c` 都输出 `1`。

浏览器里确认没改坏布局：

```js
const r = {};
['home','list','frames','me'].forEach(t => { try { document.querySelector(`[data-t=${t}]`).click(); r[t]='ok' } catch(e){ r[t]='ERR:'+e.message } });
r.app高度 = getComputedStyle(document.getElementById('app')).height;
r.视口 = innerHeight + 'px';
JSON.stringify(r)
```

Expected: 四个 Tab 全 `ok`，`app高度` 与 `视口` 相等。

- [ ] **Step 4: 提交**

```bash
git add src/tpl.html index.html
git commit -m "$(cat <<'EOF'
fix: #app 高度改用 dvh，viewport 加 interactive-widget

两条 height 顺序写反，实际生效的是 100vh。iOS Safari 的 100vh 不含底部
地址栏，正常浏览时底部 Tab 栏会被地址栏压住；PWA 模式没地址栏所以一直没暴露。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: README 与全量验收

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 改 README**

在「记忆」一节里加两条：

```
- 词表页可以直接测试当前筛选出的这批词：辨义（英译中四选一）、拼写（中译英手输）、
  听写（只听发音手输）三种题型，跟着记忆盒子自动升级，也可以手动锁定
- 测试结果直接计入间隔重复；用了首字母提示即使答对也只按「模糊」记
```

在文件表里加一行说明测试功能的位置（`src/tpl.html` 那一行的说明后面补一句）：

```
测试功能（覆盖层 #quiz、判分、音效）也在这个文件里，音效用 Web Audio 现场合成，不引入音频文件。
```

- [ ] **Step 2: 全量验收**

```bash
python3 src/build.py
```

Expected: `built …/index.html — 356 词（356 句带翻译思路，0 词缺音标）, 1 节预习, … KB`

浏览器里（`resize_window {preset:"mobile"}`、`localStorage.clear(); location.reload()` 后）
逐条过 spec 的验收清单：

```js
const r = {};
document.querySelector('[data-t=list]').click();
r.入口 = document.getElementById('goQuiz').textContent.trim();
r.范围一致 = r.入口.includes(String(quizPool().length));

// 搜索会改变范围
const inp = document.getElementById('q');
inp.value = 'pressure'; inp.dispatchEvent(new Event('input'));
r.搜索后入口 = document.getElementById('goQuiz').textContent.trim();
inp.value = ''; inp.dispatchEvent(new Event('input'));

// 三种题型
document.getElementById('goQuiz').click();
const seen = new Set();
['spell','mc','dict'].forEach(t => { S.set.quizLock = t; drawQ(); seen.add(document.querySelector('.qtype').textContent); });
r.三种题型 = [...seen];

// 归一化
r.归一化 = normAns('distance time graph') === normAns('distance–time graph')
        && normAns('specific heat capacty') !== normAns('specific heat capacity');

// 干扰项无重叠
const all = DATA.books.flatMap(b => b.words);
r.干扰项无重叠 = all.every(w => { const t = zhToks(w.zh);
  return !distractors(w).some(z => [...zhToks(z)].some(x => t.has(x))) });

// 进度联动
S.set.quizLock = 'spell'; drawQ();
const w = Q[qi];
document.getElementById('qIn').value = w.w;
document.getElementById('bSubmit').click();
r.进度联动 = S.prog[w.id].box === 1;
S.set.quizLock = '';
document.getElementById('qClose').click();
r.关闭后回词表 = !document.getElementById('quiz').classList.contains('on') && !!document.getElementById('goQuiz');
JSON.stringify(r)
```

Expected：`范围一致:true`、`搜索后入口` 的数字明显小于全量、
`三种题型` 三个都在、`归一化:true`、`干扰项无重叠:true`、
`进度联动:true`、`关闭后回词表:true`

**键盘遮挡验收**：`resize_window {width:375, height:430}`（模拟键盘弹起），
锁到「拼写」，截图确认「首字母提示」「听发音」「提交」三个按钮都完整可见可点。
验完 `resize_window {preset:"mobile"}` 复位。

**减弱动效验收**：无法在此环境模拟系统设置，改为静态核对
`@media (prefers-reduced-motion: reduce)` 块里确实覆盖了
`.fb`、`.streak`、`.qin.no`、`.confetti i`、`.tick path`、`.qlock`。

**断网验收**：`preview_stop` 停掉服务器后，直接 `open index.html`（`file://` 协议），
确认词表、测试、朗读、翻卡都正常。

- [ ] **Step 3: 提交**

```bash
git add README.md index.html
git commit -m "$(cat <<'EOF'
docs: README 补测试功能

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## 自查

对照 spec 逐节核对：

| spec 章节 | 落在哪个任务 |
| --- | --- |
| 题型（三种、按盒子升级） | Task 2（`quizType`）+ Task 3（渲染） |
| 听写的中文兜底 | Task 3 Step 4（`.qzh`） |
| 干扰项排除语义重叠 | Task 2（`distractors` + `zhToks`） |
| 归一化（U+2013 等） | Task 2（`normAns`） |
| 错误展示（diff） | Task 2（`diffHTML`）+ Task 4（渲染） |
| 提示与降级 | Task 3（`bHint`）+ Task 4（`score` 里 `hinted ? 1 : 2`） |
| 喂回间隔重复 | Task 4（`score` 调 `grade`） |
| 轮次（10 题 / 下一轮 / 重做 / 只练错题） | Task 6 |
| 奖励（音效 + 动效 + 连对 + 彩纸） | Task 1（音效）+ Task 5（动效） |
| 入口（测试在上、搜索在下、范围随筛选） | Task 3 Step 5 |
| 答题页不做固定底栏 | Task 3 Step 2（`.qbody` / `.qact`） |
| 题型选择器（顺序、打字收起） | Task 7 |
| 设置页音效开关 | Task 1 Step 5 |
| `100dvh` 顺序与 viewport meta | Task 8 |
| 验收清单 | Task 9 Step 2 + 各任务的浏览器验证 |

**命名一致性核对：** `normAns` / `diffHTML` / `zhToks` / `distractors` / `quizType` /
`quizPool` / `startQuiz` / `loadRound` / `nextRound` / `redoRound` / `restLeft` /
`drawQ` / `paintPg` / `score` / `pickMC` / `submit` / `feedback` / `next` / `result` /
`confettiHTML` / `bindQuizLock` / `sfxOK` / `sfxNo` / `sfxFinish` / `tone` / `ac` /
`S.set.sfx` / `S.set.quizLock` / `ROUND_N` —— 定义处与引用处已逐一比对一致。

**空壳追踪：** Task 3 建了 `pickMC` / `submit` 空壳（Task 4 替换）、
Task 4 建了 `result` 空壳（Task 6 替换）。到 Task 6 结束时全部落实，无遗留。
