# IGCSE 科学词汇闪卡

手机端 H5 背单词应用，三本词书：IGCSE 自然科学 **181 词**、Cambridge IGCSE Physics 0625 **175 词**（各带 10 组句型）、日常手写笔记 **40 词**。
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
- 三本词书顶部切换，也可左右滑动；进度、复习队列、难词本各自独立
- 日常词表按录入批次分章，会持续增长；加词只需往 `src/daily.py` 最后一批贴几行
- 学习页有今日到期复习、按主题网格、难词本；另一科有到期复习时在标签上挂红点
- 词表支持搜索与「遮住中文」自测；搜索时自动跨科，同名词两科例句可直接对比
- 进度存 `localStorage`，离线保留
- 词表页可以直接测试当前筛选出的这批词：辨义（英译中四选一）、拼写（中译英手输）、
  听写（只听发音手输）三种题型，跟着记忆盒子自动升级，也可以手动锁定
- 测试结果直接计入间隔重复；用了首字母提示即使答对也只按「模糊」记

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
python3 src/parse_pdf.py <自然科学词汇表.pdf> > src/parsed.json      # 可选，已附 data.json
python3 src/parse_physics_pdf.py <物理词汇表.pdf> > src/parsed_phy.json  # 可选，已入库
python3 src/build.py                                                 # 生成 index.html
```

| 文件 | 说明 |
| --- | --- |
| `src/parse_pdf.py` | 从 PDF 三栏表格解析出词条与句型 |
| `src/parse_physics_pdf.py` | 从物理 PDF 的四栏表格解析词条，处理跨页续行与章内重复 |
| `src/phon.py` | 手工编写的音标、音节切分与词根助记（164 条） |
| `src/phon_phy.py` | 物理独有 111 词的音标、音节切分与词根助记 |
| `src/trans_phy.py` | 物理 162 句的翻译思路 |
| `src/frames_phy.py` | 物理的 10 组高频答题句型 |
| `src/daily.py` | 日常词表。按录入批次分章，加词就是往最后一批贴几行 |
| `src/phon_daily.py` | 日常词的音标、音节切分与词根助记 |
| `src/tpl.html` | 应用模板，含样式、逻辑与内嵌字体，`__DATA__` 为词条占位符。测试功能（覆盖层 #quiz、判分、音效）也在这个文件里，音效用 Web Audio 现场合成，不引入音频文件。 |
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
两本词书共用同一份音标字典——51 个同名词音标一致，不重复维护。

## 说明

- 音标、音节切分和词根助记为人工编写，欢迎指正
- 界面配色、圆角、字阶与动效曲线取自 [Astryx](https://astryx.atmeta.com/) design tokens
- 字体 [Figtree](https://fonts.google.com/specimen/Figtree) 以 SIL Open Font License 1.1 授权
