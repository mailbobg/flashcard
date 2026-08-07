# -*- coding: utf-8 -*-
"""衔接课程的课前预习单。

每加一节课就往 LESSONS 里追加一条，界面不用改。

字段：
  id       课时序号
  book     这节课属于哪本词书："sci" 科学 / "phy" 物理
  title    小标题（这节讲什么）
  course   课程名
  mins     建议用时
  intro    预习要求，逐条列出
  goals    预习目标，可勾选
  vocab    重点词汇：[英文, 理解提示]。英文写成 "sci:diffusion" 可跨书引用，
           不带前缀就按本课的 book 解析。构建时会校验能否查到；
           点进去直接进闪卡流程
  reading  阅读材料：[小标题, [句子, ...]]
           每个句子是一个 dict：
             zh    中文原句（多句拼起来就是段落，界面按段落显示）
             en    对应的英文表达
             parts 中英对照的意群：[中文块, 英文块, 成分]
             note  这句中译英要注意什么
           中文里写成「中文（english）」的地方，界面会把括号中的
           英文变成可点朗读；点整块可展开英文表达与拆解
  check    上课前自查

思考题不收录 —— 那部分要动笔写，留在纸上做。
"""
LESSONS = [
{
    "id": 3,
    "book": "phy",
    "title": "扩散、布朗运动与气体规律",
    "course": "Cambridge IGCSE Physics 0625 衔接课程",
    "mins": 20,
    "intro": [
        "先阅读、朗读词汇，再回到阅读材料。",
        "不会的地方留空或圈出来，不要用翻译软件直接生成整段答案。",
    ],
    "goals": [
        "知道扩散与布朗运动不是同一个概念。",
        "理解粒子会持续进行无规则运动。",
        "尝试解释温度和分子质量为什么会影响扩散速度。",
    ],
    "vocab": [
        ["sci:diffusion",               "粒子总体由高浓度区域向低浓度区域移动"],
        ["sci:Brownian motion",         "悬浮微粒受到分子不规则碰撞产生的随机运动"],
        ["sci:random",                  "方向不断变化、没有固定路线"],
        ["sci:concentration",           "一定空间中粒子的多少"],
        ["sci:net movement",            "综合所有随机运动后呈现的总体方向"],
        ["sci:collision",               "粒子相互撞击"],
        ["sci:relative molecular mass", "一个分子中各原子相对质量的总和"],
        ["kinetic energy",              "物体或粒子由于运动具有的能量"],
        ["mass",                        "物体含有的物质数量"],
        ["pressure",                    "粒子碰撞容器壁产生的作用"],
        ["temperature",                 "粒子平均动能的度量"],
        ["volume",                      "物质或气体占据的空间"],
    ],
    "reading": [
        ["粒子一直在运动", [
            {"zh": "液体和气体中的粒子会持续进行快速、无规则的运动。",
             "en": "Particles in liquids and gases are constantly moving quickly and randomly.",
             "parts": [["液体和气体中的粒子", "Particles in liquids and gases", "s"],
                       ["会持续进行……运动", "are constantly moving", "v"],
                       ["快速、无规则的", "quickly and randomly", "a"]],
             "note": "中文说「进行……运动」是动宾结构，英文直接用动词 move 就够了。"
                     "而中文的形容词「快速、无规则的」到英文里要变成副词 quickly and randomly。"},
            {"zh": "温度越高，粒子的平均动能（kinetic energy）通常越大，运动也越快。",
             "en": "The higher the temperature, the greater the average kinetic energy of the particles, "
                   "and the faster they move.",
             "parts": [["温度越高", "The higher the temperature", "c"],
                       ["粒子的平均动能通常越大", "the greater the average kinetic energy of the particles", "c"],
                       ["运动也越快", "the faster they move", "c"]],
             "note": "「越……越……」对应英文的 the + 比较级, the + 比较级 句型，"
                     "每个分句前面都要有 the，漏掉就不成句。"},
        ]],
        ["什么是扩散？", [
            {"zh": "扩散（diffusion）是粒子由于随机运动而产生的总体净移动：从高浓度区域移向低浓度区域，"
                   "直到分布变得更加均匀。",
             "en": "Diffusion is the net movement of particles from a region of higher concentration "
                   "to a region of lower concentration, due to their random movement.",
             "parts": [["扩散是", "Diffusion is", "v"],
                       ["总体净移动", "the net movement of particles", "h"],
                       ["从高浓度区域移向低浓度区域", "from a region of higher concentration to a region of lower concentration", "a"],
                       ["由于随机运动而产生的", "due to their random movement", "d"]],
             "note": "关键差异：中文把「由于随机运动而产生的」放在中心词「净移动」前面，"
                     "英文必须挪到后面去（due to…）。中文修饰前置、英文后置，这是写英文答案时最容易出错的地方。"},
            {"zh": "扩散不需要搅拌，也不是所有粒子都只朝一个方向移动。",
             "en": "Diffusion does not need stirring, and not all particles move in only one direction.",
             "parts": [["扩散不需要搅拌", "Diffusion does not need stirring", "v"],
                       ["也不是所有粒子", "not all particles", "s"],
                       ["都只朝一个方向移动", "move in only one direction", "v"]],
             "note": "「不是所有……都」是部分否定，英文写 not all…；写成 all… not 意思就变成「全都不」了。"},
        ]],
        ["什么是布朗运动？", [
            {"zh": "布朗运动（Brownian motion）是悬浮在液体或气体中的微小可见颗粒，"
                   "由于受到周围分子的不断、不均匀碰撞而产生的随机运动。",
             "en": "Brownian motion is the random movement of small visible particles suspended in a liquid or gas, "
                   "caused by constant, uneven collisions with the surrounding molecules.",
             "parts": [["布朗运动是", "Brownian motion is", "v"],
                       ["随机运动", "the random movement", "h"],
                       ["悬浮在液体或气体中的微小可见颗粒", "of small visible particles suspended in a liquid or gas", "d"],
                       ["由于受到周围分子不断、不均匀碰撞而产生的", "caused by constant, uneven collisions with the surrounding molecules", "d"]],
             "note": "中文一口气把两串修饰全堆在「随机运动」前面，英文得拆成两段挂到后面：先 of… 再 caused by…。"
                     "suspended 也是后置定语，修饰 particles。"},
            {"zh": "它是粒子存在并不断运动的一项证据。",
             "en": "It is evidence that particles exist and are moving all the time.",
             "parts": [["它是一项证据", "It is evidence", "v"],
                       ["粒子存在并不断运动的", "that particles exist and are moving all the time", "c"]],
             "note": "「……的证据」英文用 evidence that + 从句（同位语从句），不能写成 evidence of that。"},
        ]],
        ["哪些因素会影响扩散速度？", [
            {"zh": "温度较高：粒子运动更快，扩散通常更快。",
             "en": "Higher temperature: the particles move faster, so diffusion is usually faster.",
             "parts": [["温度较高", "Higher temperature", "s"],
                       ["粒子运动更快", "the particles move faster", "c"],
                       ["扩散通常更快", "so diffusion is usually faster", "c"]],
             "note": "中文靠语序就能表达因果，英文最好补一个 so 把逻辑显式说出来——"
                     "中文重意合、英文重形合，写英文答案时连词不能省。"},
            {"zh": "浓度差较大：开始时净移动更明显。",
             "en": "A greater difference in concentration: the net movement is more obvious at the start.",
             "parts": [["浓度差较大", "A greater difference in concentration", "s"],
                       ["净移动更明显", "the net movement is more obvious", "c"],
                       ["开始时", "at the start", "a"]],
             "note": "「浓度差」是 difference in concentration，介词用 in 不用 of。"
                     "中文时间词「开始时」在前，英文习惯放句末。"},
            {"zh": "粒子质量较小：在相同条件下通常运动更快，扩散更快。",
             "en": "Smaller particle mass: under the same conditions the particles usually move faster and diffuse faster.",
             "parts": [["粒子质量较小", "Smaller particle mass", "s"],
                       ["在相同条件下", "under the same conditions", "a"],
                       ["通常运动更快，扩散更快", "usually move faster and diffuse faster", "c"]],
             "note": "「在……条件下」固定搭配是 under conditions，不是 in。"
                     "diffuse 是动词、diffusion 是名词，这里要用动词。"},
        ]],
        ["气体的压力与体积", [
            {"zh": "气体压力来自粒子不断碰撞容器壁。",
             "en": "Gas pressure comes from the constant collisions of particles with the container walls.",
             "parts": [["气体压力", "Gas pressure", "s"],
                       ["来自", "comes from", "v"],
                       ["粒子不断碰撞容器壁", "the constant collisions of particles with the container walls", "h"]],
             "note": "中文「粒子不断碰撞容器壁」是个主谓宾小句，英文更常写成名词化的"
                     "「the collisions of A with B」。科学英语偏爱名词化——正好是词卡里那条规律反过来用。"},
            {"zh": "提高温度会使粒子运动更快；压缩气体会让粒子在更小空间中更频繁地碰撞容器壁。",
             "en": "Raising the temperature makes the particles move faster; compressing the gas makes them "
                   "hit the walls more often in a smaller space.",
             "parts": [["提高温度", "Raising the temperature", "s"],
                       ["会使粒子运动更快", "makes the particles move faster", "v"],
                       ["压缩气体", "compressing the gas", "s"],
                       ["会让粒子更频繁地碰撞容器壁", "makes them hit the walls more often", "v"],
                       ["在更小空间中", "in a smaller space", "a"]],
             "note": "中文的「提高温度」「压缩气体」作主语时，英文要用动名词 Raising / compressing。"
                     "另外 make 后面跟动词原形，不带 to：makes them hit，不是 makes them to hit。"},
        ]],
    ],
    "check": ["已朗读全部词汇", "已读完阅读材料", "已圈出不懂的地方"],
},
]
