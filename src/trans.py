# -*- coding: utf-8 -*-
"""例句的翻译思路标注（样板，尚未覆盖全部词条）。

键 = 词条。字段：
  pat   句型名
  ch    意群列表 [英文, 中文直译, 成分代号]
  order 中文的拼装顺序（ch 的下标）——英语中心词在前、修饰在后，
        中文相反，所以这里常常是倒着走
  tip   一句话点破这句的关键

成分代号 → 颜色：
  v 谓语(蓝) · s 主语(绿) · h 中心词(红) · d 定语(黄) · a 状语(紫) · c 从句(青)
"""
TRANS = {

"time": {
    "pat": "祈使句 + 后置定语",
    "ch": [
        ["Measure",                          "测量",         "v"],
        ["the time",                         "时间",         "h"],
        ["taken",                            "所需的",       "d"],
        ["for the solid to dissolve",        "固体溶解",     "d"],
    ],
    "order": [0, 3, 2, 1],
    "tip": "没有主语、动词原形开头 → 祈使句，中文直接用动词起头。"
           "the time 是中心词，taken… 整块都是它的后置定语；"
           "中文必须把定语搬到中心词前面，所以从最后一块往回装。",
},

"pressure": {
    "pat": "被动语态 + 介词短语",
    "ch": [
        ["Gas pressure",                     "气体压强",     "s"],
        ["is caused by",                     "由……产生",     "v"],
        ["particle collisions",              "粒子碰撞",     "h"],
        ["with the container walls",         "与容器壁",     "d"],
    ],
    "order": [0, 3, 2, 1],
    "tip": "be + 过去分词 = 被动。中文很少说「被产生」，"
           "用「由……产生／造成」更自然。with 短语修饰 collisions，同样要前移。",
},

"concentration": {
    "pat": "主谓宾 + 比较级",
    "ch": [
        ["A higher concentration",           "更高的浓度",   "s"],
        ["gives",                            "意味着",       "v"],
        ["more particles",                   "更多粒子",     "h"],
        ["per unit volume",                  "每单位体积",   "a"],
    ],
    "order": [0, 1, 3, 2],
    "tip": "give 在科学英语里常不是「给」，而是「得出、意味着」。"
           "per = 每，状语在中文里要提到宾语前面说。",
},

}
