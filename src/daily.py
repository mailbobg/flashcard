# -*- coding: utf-8 -*-
"""日常词表 —— 会一直增长的手写笔记。

和另外两本词书的根本差别：那两本是一次性导入的定稿词表，这本是流水账。
所以这里的结构只为一件事服务：**加词的摩擦要足够低**。

## 怎么加词

往最后一批的 words 里贴几行就行：

    {"w": "单词", "zh": "中文", "ex": "英文例句", "exzh": "例句中译"},

攒够一批（或换了个来源）就在 BATCHES 末尾新起一条，`cn` 写清是哪天、哪来的。

## 为什么按批次分章，而不按主题或字母

日常词没有主题可分。按字母的话每加一批章节都会重排，「按主题学习」那一屏的
进度条就失去意义了 —— 你昨天学完的第 3 章，今天可能变成第 5 章的一部分。
按批次分则章节永远稳定，还天然记录了这批词是哪天、从哪抄来的。

## 加词之后还要做什么

`src/phon_daily.py` 里要有对应的音节切分与词根助记，否则构建会报错
（`build.py` 的 STRICT_PHON 对三本书一视同仁）。这是刻意的：宁可加词时被拦下，
也不要让一半词条没有音节、卡片上留一块空白。
"""

BATCHES = [
    {
        "cn": "9/2 手写笔记",
        "en": "Sept 2 notes",
        "words": [
            # 原稿把 deposit 写成了 deposite，这里按正确拼写收
            {"w": "deposit", "zh": "押金；定金",
             "ex": "We paid a deposit for the flat.",
             "exzh": "我们为这套公寓付了押金。"},
            {"w": "paused", "zh": "暂停；停顿",
             "ex": "She paused before answering.",
             "exzh": "她回答前停顿了一下。"},
            {"w": "insist", "zh": "坚持",
             "ex": "He insisted on paying the bill.",
             "exzh": "他坚持要买单。"},
            # 原稿字迹像 returetable，按 returnable 理解（对应「押金退还」）
            {"w": "returnable", "zh": "可退还的",
             "ex": "The deposit is returnable when you move out.",
             "exzh": "押金在你搬走时可以退还。"},
            {"w": "suppose", "zh": "以为；假设",
             "ex": "I suppose he forgot the time.",
             "exzh": "我以为他忘了时间。"},
            {"w": "complain", "zh": "抱怨；投诉",
             "ex": "She complained about the noise upstairs.",
             "exzh": "她投诉楼上的噪音。"},
            {"w": "grumble", "zh": "嘟囔着抱怨",
             "ex": "He grumbled about the cold weather all day.",
             "exzh": "他一整天都在嘟囔天气冷。"},
            {"w": "tempt", "zh": "诱惑；勾引",
             "ex": "The smell of bread tempted me to buy some.",
             "exzh": "面包的香味诱惑我买了一些。"},
            {"w": "whine", "zh": "哼哼唧唧地抱怨",
             "ex": "Stop whining and finish your homework.",
             "exzh": "别哼唧了，把作业做完。"},
            {"w": "lure", "zh": "引诱",
             "ex": "The shop used low prices to lure customers.",
             "exzh": "那家店用低价引诱顾客。"},
            {"w": "temporary", "zh": "暂时的",
             "ex": "This is only a temporary job.",
             "exzh": "这只是一份临时工作。"},
            {"w": "permanent", "zh": "永久的",
             "ex": "She found a permanent job in the city.",
             "exzh": "她在城里找到一份长期工作。"},
            {"w": "lodge", "zh": "小屋",
             "ex": "We stayed in a small lodge near the lake.",
             "exzh": "我们住在湖边一间小木屋里。"},
            {"w": "halt", "zh": "停止",
             "ex": "The bus came to a halt at the corner.",
             "exzh": "公交车在拐角处停了下来。"},
            {"w": "tent", "zh": "帐篷",
             "ex": "We put up the tent before dark.",
             "exzh": "我们在天黑前搭好了帐篷。"},
            {"w": "camp", "zh": "营地；阵营",
             "ex": "They set up camp beside the river.",
             "exzh": "他们在河边扎营。"},
            {"w": "landlord", "zh": "房东",
             "ex": "The landlord raised the rent last month.",
             "exzh": "房东上个月涨了租金。"},
            {"w": "settle", "zh": "定居",
             "ex": "They settled in this town ten years ago.",
             "exzh": "他们十年前在这个镇定居。"},
            {"w": "sterile", "zh": "无菌的",
             "ex": "The nurse used a sterile needle.",
             "exzh": "护士用了一根无菌针头。"},
            {"w": "polluted", "zh": "受污染的",
             "ex": "The river is badly polluted.",
             "exzh": "这条河污染严重。"},
            {"w": "drenched", "zh": "淋透的",
             "ex": "We got drenched walking home in the rain.",
             "exzh": "我们冒雨走回家，淋透了。"},
            {"w": "parched", "zh": "干渴的；干旱的",
             "ex": "After the run I was parched.",
             "exzh": "跑完步我渴极了。"},
            {"w": "gravel", "zh": "石砾；碎石",
             "ex": "The path is covered with gravel.",
             "exzh": "小路上铺着碎石。"},
            {"w": "moist", "zh": "潮湿的",
             "ex": "Keep the soil moist but not wet.",
             "exzh": "保持土壤湿润，但不要太湿。"},
            {"w": "soggy", "zh": "湿软的",
             "ex": "The bread went soggy in the rain.",
             "exzh": "面包淋雨后变得湿软。"},
            {"w": "damp", "zh": "潮湿的",
             "ex": "The walls feel damp in winter.",
             "exzh": "冬天墙壁摸上去很潮。"},
            {"w": "seldom", "zh": "很少",
             "ex": "He seldom eats out.",
             "exzh": "他很少在外面吃饭。"},
            {"w": "a lot", "zh": "很多",
             "ex": "She travels a lot for work.",
             "exzh": "她因为工作经常出差。"},
            {"w": "lists", "zh": "列表；清单",
             "ex": "She makes lists before she goes shopping.",
             "exzh": "她购物前会列清单。"},
            {"w": "recordings", "zh": "录音",
             "ex": "The recordings help me practise listening.",
             "exzh": "这些录音帮我练听力。"},
            {"w": "absent", "zh": "缺席的",
             "ex": "Two students were absent today.",
             "exzh": "今天有两名学生缺席。"},
            {"w": "contract", "zh": "合同",
             "ex": "Read the contract before you sign it.",
             "exzh": "签之前先把合同看一遍。"},
            {"w": "propensity", "zh": "习性；倾向",
             "ex": "He has a propensity to arrive late.",
             "exzh": "他有迟到的习性。"},
            {"w": "communicate", "zh": "沟通",
             "ex": "We communicate by text every day.",
             "exzh": "我们每天用短信沟通。"},
            {"w": "peer", "zh": "同龄人",
             "ex": "Teenagers care about what their peers think.",
             "exzh": "青少年在意同龄人怎么想。"},
            {"w": "freedom", "zh": "自由",
             "ex": "She values her freedom to choose.",
             "exzh": "她珍视自己选择的自由。"},
            {"w": "peace", "zh": "和平；平静",
             "ex": "The village is full of peace in the morning.",
             "exzh": "早晨的村子一片宁静。"},
            {"w": "period", "zh": "时期",
             "ex": "This was a difficult period for the family.",
             "exzh": "这对这家人是段艰难的时期。"},
            {"w": "reported", "zh": "报道",
             "ex": "The news reported heavy rain in the south.",
             "exzh": "新闻报道南方有大雨。"},
            {"w": "situation", "zh": "情况",
             "ex": "The situation improved after the meeting.",
             "exzh": "会议之后情况有所好转。"},
        ],
    },
]
