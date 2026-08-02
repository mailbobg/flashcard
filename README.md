# IGCSE 科学词汇闪卡

手机端 H5 背单词应用，覆盖 IGCSE 自然科学核心词汇 **164 词 + 10 组句型**。
单个 `index.html`，**零外部请求、可离线使用**，浏览器打开即可。

线上地址：**<https://flash.imyway.cn/>**

## 功能

**发音**

- 每词标注英式音标（RP），如 `photosynthesis /ˌfəʊtəʊˈsɪnθəsɪs/`
- **发音音节拆分**：`pho·to·syn·the·sis`，每块单独标注音标，并按音标结尾自动判定开音节 / 闭音节
- **倒切法**：从词尾往前按「一元一辅」切字母，圆圈数字标出下刀顺序。与发音音节不一致时会显式标注（164 词中 141 词一致）
- 点单个音节可单独慢速朗读；「逐音节跟读」按音节逐个高亮播放 → 整词慢速 → 整词正常
- 音节朗读默认按音标拟音（`ʃn` → `shun`、`kjʊ` → `kyoo`），比直接读拼写准确；可在设置里切回按拼写
- 朗读走系统 TTS（Web Speech API），默认优先选择 en-GB 语音，语速可调

**记忆**

- 卡片正面单词 / 音标 / 音节，轻点翻面看中文释义、词根词缀助记、例句与翻译
- 三档自评 + 间隔重复：即时 / 10 分钟 / 1 天 / 3 天 / 7 天 / 21 天；「忘记」的词本轮末尾再出现一次
- 首页有今日到期复习、按主题进度、难词本
- 词表支持搜索与「遮住中文」自测
- 进度存 `localStorage`，离线保留

**其他**

- 浅色 / 深色主题（基于 `light-dark()` + `color-scheme`）
- 内嵌 Figtree 可变字体（OFL），latin-ext 子集覆盖 IPA 扩展区，音标与正文字形统一

## 使用

直接用浏览器打开 `index.html` 即可。手机上可用局部静态服务：

```bash
python3 -m http.server 8777
```

然后手机访问 `http://<电脑 IP>:8777`。在 Safari 里「添加到主屏幕」后是全屏 App 形态。

## 从源码构建

```bash
pip install pymupdf
python3 src/parse_pdf.py <词汇表.pdf> > src/parsed.json   # 解析 PDF（可选，已附 data.json）
python3 src/build.py                                      # 生成 index.html
```

| 文件 | 说明 |
| --- | --- |
| `src/parse_pdf.py` | 从 PDF 三栏表格解析出词条与句型 |
| `src/phon.py` | 手工编写的音标、音节切分与词根助记（164 条） |
| `src/tpl.html` | 应用模板，含样式、逻辑与内嵌字体，`__DATA__` 为词条占位符 |
| `src/data.json` | 合成后的词条数据 |
| `src/build.py` | 合成数据并注入模板，产出根目录 `index.html`（含音节拼写校验） |
| `src/share.html` | 分享卡片设计稿，复用应用内嵌的 Figtree |
| `src/make_share.py` | Chrome headless 出图：`share.jpg` / `share-square.jpg` / 图标 |

换域名时改 `src/build.py` 顶部的 `BASE` 一行再重新构建即可——`og:image`
必须是绝对地址，模板里统一用 `__BASE__` 占位。分享图改动后需重跑
`python3 src/make_share.py`。

`src/phon.py` 的音节格式为 `拼写=音标`，音节间用 `|`，短语中的词间用 ` / ` 分隔：

```python
"observation": ("ob=ˌɒb|ser=zə|va=ˈveɪ|tion=ʃn", "ob-（朝向）+ serve（看守）→ 盯着看 = 观察；-ation 变名词。"),
```

整词音标由各音节音标拼接得出，因此只需维护一处。

## 说明

- 音标、音节切分和词根助记为人工编写，欢迎指正
- 界面配色、圆角、字阶与动效曲线取自 [Astryx](https://astryx.atmeta.com/) design tokens
- 字体 [Figtree](https://fonts.google.com/specimen/Figtree) 以 SIL Open Font License 1.1 授权
