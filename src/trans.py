# -*- coding: utf-8 -*-
"""例句的翻译思路标注。

设计取向：IGCSE 考生要读懂英文、用英文作答，不是产出漂亮中文。
所以主轨是「顺着英语语序一次读懂」，重排成中文只作核对。

键 = 词条。字段：
  pat   句型名
  flow  顺句理解：[英文块, 读到这里脑子里的中文, 成分]。按英语原序，不回头
  core  主干：[英文, 中文]。剥掉全部修饰后剩下的主谓宾
  tree  修饰层级：[缩进层级, 英文, 中文]（可选，只在有嵌套修饰时给）
  asm   中文装配顺序：[中文片段, 成分]（可选，只在语序需要重排时给）
  final 完整译文的分段：[中文片段, 成分]。与 flow/tree 同色，
        让读者看出译文每一段来自哪个英文意群；标点用空字符串
  shift 词性转换（可选）：[英文, 中文, 说明]。科学英语大量名词化，
        中文要还原成动词，例如 formation of bubbles → 产生气泡
  tip   一句话点破

成分代号：v 谓语 · s 主语 · h 中心词 · d 定语 · a 状语 · c 从句
"""
TRANS = {

# ========== 一、IGCSE 题目指令词 ==========

"state": {
    "pat": "祈使句 + of 后置定语",
    "flow": [["State", "写出……", "v"], ["the colour", "什么颜色", "h"], ["of the solution", "该溶液的", "d"]],
    "core": ["State the colour", "写出颜色"],
    "tree": [[0, "the colour", "颜色"], [1, "of the solution", "该溶液的"]],
    "asm": [["该溶液的", "d"], ["颜色", "h"]],
    "final": [["写出", "v"], ["该溶液的", "d"], ["颜色", "h"], ["。", ""]],
    "tip": "state 要的是结论本身，不要解释。of 短语是后置定语，中文提到「颜色」前面。",
},

"name": {
    "pat": "祈使句 + 分词后置定语",
    "flow": [["Name", "写出名称", "v"], ["the gas", "哪种气体", "h"],
             ["produced", "被生成的", "d"], ["in the reaction", "在该反应里", "d"]],
    "core": ["Name the gas", "写出气体的名称"],
    "tree": [[0, "the gas", "气体"], [1, "produced", "产生的"], [2, "in the reaction", "该反应"]],
    "asm": [["该反应产生的", "d"], ["气体名称", "h"]],
    "final": [["写出", "v"], ["该反应产生的", "d"], ["气体名称", "h"], ["。", ""]],
    "tip": "produced 是过去分词作后置定语，等于 which is produced。中文把整块「该反应产生的」搬到「气体」前面。",
},

"identify": {
    "pat": "祈使句（语序与中文一致）",
    "flow": [["Identify", "指出", "v"], ["the independent variable", "自变量", "h"]],
    "core": ["Identify the variable", "指出变量"],
    "final": [["指出", "v"], ["自变量", "h"], ["。", ""]],
    "tip": "动宾结构，英汉语序相同，顺着直译即可，不用重排。",
},

"define": {
    "pat": "祈使句 + 同位语",
    "flow": [["Define", "给……下定义", "v"], ["the term", "这个术语", "h"], ["diffusion", "就是「扩散」", "h"]],
    "core": ["Define the term", "给术语下定义"],
    "final": [["给", "v"], ["“扩散”", "h"], ["下定义", "v"], ["。", ""]],
    "tip": "the term 和 diffusion 是同位语，指同一个东西，别译成「术语的扩散」，要译成「『扩散』这个术语」。",
},

"describe": {
    "pat": "祈使句 + how 宾语从句",
    "flow": [["Describe", "描述", "v"], ["how the temperature changes", "温度是怎么变的", "c"]],
    "core": ["Describe how…", "描述……如何"],
    "final": [["描述", "v"], ["温度如何变化", "c"], ["。", ""]],
    "tip": "how 引导的整个从句作 Describe 的宾语。从句内部是「主语 + 谓语」的正常语序，顺译即可。",
},

"explain": {
    "pat": "祈使句 + why 宾语从句（含被动）",
    "flow": [["Explain", "解释", "v"], ["why the gas can be compressed", "气体为什么能被压缩", "c"]],
    "core": ["Explain why…", "解释为什么……"],
    "final": [["解释", "v"], ["气体为什么可以被压缩", "c"], ["。", ""]],
    "tip": "explain 要答原因。从句里 can be compressed 是被动，这里中文保留「被」读着自然。",
},

"compare": {
    "pat": "祈使句 + 两层后置定语",
    "flow": [["Compare", "比较", "v"], ["the arrangement", "排列方式", "h"],
             ["of particles", "粒子的", "d"], ["in solids and liquids", "在固体和液体里", "d"]],
    "core": ["Compare the arrangement", "比较排列"],
    "tree": [[0, "the arrangement", "排列"], [1, "of particles", "粒子的"], [2, "in solids and liquids", "固体和液体中"]],
    "asm": [["固体和液体中", "d"], ["粒子的", "d"], ["排列", "h"]],
    "final": [["比较", "v"], ["固体和液体中", "d"], ["粒子的", "d"], ["排列", "h"], ["。", ""]],
    "tip": "两层定语套在一起：in… 修饰 particles，of particles 又修饰 arrangement。中文从最里层往外依次前置。",
},

"calculate": {
    "pat": "祈使句 + of 后置定语",
    "flow": [["Calculate", "计算", "v"], ["the mass", "什么的质量", "h"], ["of the product", "生成物的", "d"]],
    "core": ["Calculate the mass", "计算质量"],
    "tree": [[0, "the mass", "质量"], [1, "of the product", "生成物的"]],
    "asm": [["生成物的", "d"], ["质量", "h"]],
    "final": [["计算", "v"], ["生成物的", "d"], ["质量", "h"], ["。", ""]],
    "tip": "calculate 必须写出计算过程和单位。of 短语后置，中文前移。",
},

"determine": {
    "pat": "祈使句 + 方式状语后置",
    "flow": [["Determine", "确定", "v"], ["the boiling point", "沸点", "h"], ["from the graph", "依据是那张图", "a"]],
    "core": ["Determine the boiling point", "确定沸点"],
    "asm": [["根据图像", "a"], ["确定", "v"], ["沸点", "h"]],
    "final": [["根据图像", "a"], ["确定", "v"], ["沸点", "h"], ["。", ""]],
    "tip": "from 短语是方式状语，英语习惯放句末，中文习惯放句首——这类状语要整块提到最前面。",
},

"predict": {
    "pat": "祈使句 + what 从句（内含时间状语从句）",
    "flow": [["Predict", "预测", "v"], ["what happens", "会发生什么", "c"],
             ["when the temperature increases", "在温度升高的时候", "c"]],
    "core": ["Predict what happens", "预测会发生什么"],
    "asm": [["温度升高时", "c"], ["会发生什么", "c"]],
    "final": [["预测", "v"], ["温度升高时", "c"], ["会发生什么", "c"], ["。", ""]],
    "tip": "when 引导的时间状语从句在英语里放后面，中文习惯先说时间条件再说结果，所以要调到前面。",
},

"suggest": {
    "pat": "祈使句 + for 后置定语",
    "flow": [["Suggest", "提出", "v"], ["one reason", "一个原因", "h"],
             ["for the unusual result", "针对那个异常结果的", "d"]],
    "core": ["Suggest one reason", "提出一个原因"],
    "tree": [[0, "one reason", "一个原因"], [1, "for the unusual result", "针对异常结果的"]],
    "asm": [["对这一异常结果", "d"], ["提出", "v"], ["一个合理原因", "h"]],
    "final": [["对这一异常结果", "d"], ["提出", "v"], ["一个合理原因", "h"], ["。", ""]],
    "tip": "suggest 不要求唯一正确答案，合理即可。for 短语说明原因是针对什么的，中文提到动词前面说。",
},

"evaluate": {
    "pat": "祈使句 + of 后置定语",
    "flow": [["Evaluate", "评价", "v"], ["the reliability", "可靠性", "h"], ["of the experiment", "该实验的", "d"]],
    "core": ["Evaluate the reliability", "评价可靠性"],
    "tree": [[0, "the reliability", "可靠性"], [1, "of the experiment", "该实验的"]],
    "asm": [["该实验的", "d"], ["可靠性", "h"]],
    "final": [["评价", "v"], ["该实验的", "d"], ["可靠性", "h"], ["。", ""]],
    "tip": "evaluate 要给出优点和缺点两面，再下判断。of 短语照例前移。",
},

# ========== 二、科学探究与数据 ==========

"observation": {
    "pat": "名词化主语 + 判断句",
    "flow": [["The formation", "「形成」这件事", "s"], ["of bubbles", "气泡的", "s"],
             ["is", "是", "v"], ["an observation", "一项观察到的现象", "h"]],
    "core": ["The formation is an observation", "形成是一项观察"],
    "shift": ["the formation of bubbles", "产生气泡", "英语名词 formation → 中文动词「产生」"],
    "asm": [["产生气泡", "s"], ["是", "v"], ["一项观察到的现象", "h"]],
    "final": [["产生气泡", "s"], ["是", "v"], ["一项观察到的现象", "h"], ["。", ""]],
    "tip": "科学英语爱把动作写成名词。「the formation of bubbles」直译成「气泡的形成」很生硬，"
           "还原成动宾「产生气泡」才是地道中文——这是科学英语译中文最高频的一步。",
},

"evidence": {
    "pat": "主谓宾 + for 后置定语",
    "flow": [["The data", "这些数据", "s"], ["provide", "提供了", "v"],
             ["evidence", "证据", "h"], ["for the conclusion", "支持结论的", "d"]],
    "core": ["The data provide evidence", "数据提供证据"],
    "asm": [["为结论", "d"], ["提供了", "v"], ["证据", "h"]],
    "final": [["这些数据", "s"], ["为结论", "d"], ["提供了", "v"], ["证据", "h"], ["。", ""]],
    "tip": "data 是复数（单数 datum），所以谓语用 provide 不用 provides。for 短语中文提到动词前。",
},

"hypothesis": {
    "pat": "主谓宾 + that 同位语从句",
    "flow": [["The student", "学生", "s"], ["tests", "检验", "v"], ["the hypothesis", "某个假设", "h"],
             ["that heat increases the reaction rate", "内容是：加热会提高反应速率", "c"]],
    "core": ["The student tests the hypothesis", "学生检验假设"],
    "tree": [[0, "the hypothesis", "假设"], [1, "that heat increases…", "加热会提高速率（假设的内容）"]],
    "asm": [["“加热会提高反应速率”", "c"], ["这一假设", "h"]],
    "final": [["学生", "s"], ["检验", "v"], ["“加热会提高反应速率”", "c"], ["这一假设", "h"], ["。", ""]],
    "tip": "这里的 that 不是定语从句，是同位语从句——它交代 hypothesis 的具体内容。"
           "中文常用引号把内容引出来，再补一句「这一假设」。",
},

"variable": {
    "pat": "被动语态 + 频率状语",
    "flow": [["Only one variable", "只有一个变量", "s"], ["should be changed", "该被改变", "v"],
             ["at a time", "每次", "a"]],
    "core": ["One variable should be changed", "一个变量应被改变"],
    "asm": [["每次", "a"], ["只应改变", "v"], ["一个变量", "s"]],
    "final": [["每次", "a"], ["只应", ""], ["改变", "v"], ["一个变量", "s"], ["。", ""]],
    "tip": "英语被动「should be changed」，中文说成主动「只应改变」更自然。"
           "at a time 是频率状语，中文提到句首。",
},

"independent variable": {
    "pat": "判断句 + 地点状语",
    "flow": [["Temperature", "温度", "s"], ["is", "是", "v"],
             ["the independent variable", "自变量", "h"], ["in this experiment", "在这个实验里", "a"]],
    "core": ["Temperature is the variable", "温度是变量"],
    "asm": [["这个实验中的", "a"], ["自变量", "h"]],
    "final": [["温度", "s"], ["是", "v"], ["这个实验中的", "a"], ["自变量", "h"], ["。", ""]],
    "tip": "A is B 判断句，语序与中文一致。句末的 in… 状语中文要提到表语前面。",
},

"dependent variable": {
    "pat": "分词作定语 + 判断句",
    "flow": [["The time", "时间", "s"], ["taken", "花掉的", "d"],
             ["is", "是", "v"], ["the dependent variable", "因变量", "h"]],
    "core": ["The time is the variable", "时间是变量"],
    "tree": [[0, "The time", "时间"], [1, "taken", "所需的"]],
    "asm": [["所需", "d"], ["时间", "s"]],
    "final": [["所需时间", "s"], ["是", "v"], ["因变量", "h"], ["。", ""]],
    "tip": "taken 是过去分词作后置定语，只有一个词也照样后置。中文前移成「所需时间」。",
},

"control variable": {
    "pat": "of 后置定语 + 判断句",
    "flow": [["The volume", "体积", "s"], ["of water", "水的", "d"],
             ["is", "是", "v"], ["a control variable", "一个控制变量", "h"]],
    "core": ["The volume is a variable", "体积是变量"],
    "asm": [["水的", "d"], ["体积", "s"]],
    "final": [["水的", "d"], ["体积", "s"], ["是", "v"], ["一个控制变量", "h"], ["。", ""]],
    "tip": "of 短语前移。主语部分带定语时，整块「水的体积」一起充当主语。",
},

"fair test": {
    "pat": "并列谓语",
    "flow": [["A fair test", "公平实验", "s"], ["changes one factor", "改变一个因素", "v"],
             ["and keeps the others constant", "同时让其余的保持不变", "v"]],
    "core": ["A test changes… and keeps…", "实验改变……并保持……"],
    "final": [["公平实验", "s"], ["只改变一个因素", "v"], ["，并", ""],
              ["保持其他因素不变", "v"], ["。", ""]],
    "tip": "and 连接两个并列谓语，主语共用。keep A constant 是「使 A 保持不变」，"
           "constant 是宾语补足语，不是状语。",
},

"method": {
    "pat": "祈使句 + for 后置定语（含动名词）",
    "flow": [["Write", "写出", "v"], ["a method", "一份方法", "h"],
             ["for separating sand from water", "用来把沙子和水分开的", "d"]],
    "core": ["Write a method", "写出方法"],
    "tree": [[0, "a method", "方法"], [1, "for separating sand from water", "将沙子与水分离的"]],
    "asm": [["将沙子与水分离的", "d"], ["实验方法", "h"]],
    "final": [["写出", "v"], ["将沙子与水分离的", "d"], ["实验方法", "h"], ["。", ""]],
    "tip": "for 后面跟动名词 separating，整块是 method 的后置定语。separate A from B = 把 A 从 B 中分离。",
},

"procedure": {
    "pat": "祈使句 + 方式状语",
    "flow": [["Follow", "按照……操作", "v"], ["the procedure", "实验步骤", "h"], ["carefully", "要仔细", "a"]],
    "core": ["Follow the procedure", "按照步骤操作"],
    "asm": [["认真", "a"], ["按照", "v"], ["实验步骤操作", "h"]],
    "final": [["认真", "a"], ["按照", "v"], ["实验步骤", "h"], ["操作", "v"], ["。", ""]],
    "tip": "副词 carefully 在英语里放句末，中文习惯放动词前面。",
},

"result": {
    "pat": "祈使句 + 地点状语",
    "flow": [["Record", "记录", "v"], ["each result", "每一个结果", "h"], ["in the table", "记到表格里", "a"]],
    "core": ["Record each result", "记录每个结果"],
    "asm": [["把每个结果", "h"], ["记录", "v"], ["在表格中", "a"]],
    "final": [["把每个结果", "h"], ["记录", "v"], ["在表格中", "a"], ["。", ""]],
    "tip": "中文常用「把」字句把宾语提前：把 A 记录在 B 中。这比直译「记录每个结果在表格中」自然得多。",
},

"conclusion": {
    "pat": "被动语态 + by 施动者",
    "flow": [["The conclusion", "结论", "s"], ["must be supported", "必须得到支持", "v"],
             ["by the results", "支持它的是实验结果", "a"]],
    "core": ["The conclusion must be supported", "结论必须得到支持"],
    "asm": [["得到实验结果的", "a"], ["支持", "v"]],
    "final": [["结论", "s"], ["必须", ""], ["得到实验结果的", "a"], ["支持", "v"], ["。", ""]],
    "tip": "be + 过去分词 + by = 被动。by 后面是动作的发出者。"
           "中文不说「被结果支持」，说「得到结果的支持」。",
},

"accuracy": {
    "pat": "动名词作主语 + of 后置定语",
    "flow": [["Using a more precise balance", "使用更精密的天平（这件事）", "s"],
             ["may improve", "可能提高", "v"], ["the accuracy", "准确度", "h"],
             ["of the measurement", "测量的", "d"]],
    "core": ["Using… may improve the accuracy", "使用……可能提高准确度"],
    "tree": [[0, "the accuracy", "准确度"], [1, "of the measurement", "测量的"]],
    "asm": [["测量的", "d"], ["准确度", "h"]],
    "final": [["使用更精密的天平", "s"], ["可能提高", "v"], ["测量的", "d"], ["准确度", "h"], ["。", ""]],
    "tip": "动名词短语 Using… 整块作主语，中文直接译成动词短语放句首即可。",
},

"precision": {
    "pat": "主谓宾（have 结构）",
    "flow": [["The repeated readings", "这些重复读数", "s"], ["have", "具有", "v"],
             ["high precision", "很高的精密度", "h"]],
    "core": ["The readings have precision", "读数具有精密度"],
    "final": [["这些重复读数", "s"], ["具有", "v"], ["较高精密度", "h"], ["。", ""]],
    "tip": "repeated 是过去分词作前置定语（在名词前，不用移位）。语序与中文一致，顺译即可。",
},

"reliability": {
    "pat": "动名词作主语 + of 后置定语",
    "flow": [["Repeating the experiment", "重复实验（这件事）", "s"], ["improves", "能提高", "v"],
             ["the reliability", "可靠性", "h"], ["of the results", "结果的", "d"]],
    "core": ["Repeating… improves the reliability", "重复……提高可靠性"],
    "tree": [[0, "the reliability", "可靠性"], [1, "of the results", "结果的"]],
    "asm": [["结果的", "d"], ["可靠性", "h"]],
    "final": [["重复实验", "s"], ["可以提高", "v"], ["结果的", "d"], ["可靠性", "h"], ["。", ""]],
    "tip": "动名词作主语时，中文用动词短语开头就行，不必加「……这件事」。",
},

"repeat": {
    "pat": "祈使句 + 次数状语",
    "flow": [["Repeat", "重复", "v"], ["the test", "这项测试", "h"], ["three times", "做三次", "a"]],
    "core": ["Repeat the test", "重复测试"],
    "asm": [["将该测试", "h"], ["重复", "v"], ["三次", "a"]],
    "final": [["将该测试", "h"], ["重复", "v"], ["三次", "a"], ["。", ""]],
    "tip": "次数状语 three times 放句末，中文也放动词后面，这点一致。用「将」字句提宾更顺。",
},

"mean": {
    "pat": "祈使句 + of 后置定语",
    "flow": [["Calculate", "计算", "v"], ["the mean", "平均值", "h"], ["of the three readings", "这三个读数的", "d"]],
    "core": ["Calculate the mean", "计算平均值"],
    "tree": [[0, "the mean", "平均值"], [1, "of the three readings", "三次读数的"]],
    "asm": [["三次读数的", "d"], ["平均值", "h"]],
    "final": [["计算", "v"], ["三次读数的", "d"], ["平均值", "h"], ["。", ""]],
    "tip": "mean 在这里不是「意思」，是「平均值」= 总和 ÷ 个数。of 短语照例前移。",
},

"anomalous result": {
    "pat": "of 同位语 + 判断句",
    "flow": [["The value", "那个数值", "s"], ["of 35 seconds", "也就是 35 秒", "s"],
             ["is", "是", "v"], ["an anomalous result", "一个异常结果", "h"]],
    "core": ["The value is an anomalous result", "数值是异常结果"],
    "final": [["35 秒这个数据", "s"], ["是", "v"], ["一个异常结果", "h"], ["。", ""]],
    "tip": "「the value of 35 seconds」里 of 表同位，不是所属——value 就等于 35 秒，"
           "所以译成「35 秒这个数据」，不是「35 秒的数值」。",
},

# ========== 三、测量、数量与变化 ==========

"mass": {
    "pat": "of 后置定语 + 判断句",
    "flow": [["The mass", "质量", "s"], ["of the sample", "样品的", "d"], ["is 5.0 g", "是 5.0 克", "v"]],
    "core": ["The mass is 5.0 g", "质量是 5.0 克"],
    "asm": [["样品的", "d"], ["质量", "s"]],
    "final": [["样品的", "d"], ["质量", "s"], ["为", "v"], ["5.0 克", "h"], ["。", ""]],
    "tip": "数值题里 of 短语几乎必出现，一律前移。注意单位 g 要照抄，不能漏。",
},

"volume": {
    "pat": "祈使句 + of 定语 + 单位状语",
    "flow": [["Measure", "测量", "v"], ["the volume", "体积", "h"],
             ["of the liquid", "液体的", "d"], ["in cm³", "用立方厘米作单位", "a"]],
    "core": ["Measure the volume", "测量体积"],
    "tree": [[0, "the volume", "体积"], [1, "of the liquid", "液体的"]],
    "asm": [["用立方厘米", "a"], ["测量", "v"], ["液体", "d"], ["体积", "h"]],
    "final": [["用立方厘米", "a"], ["测量", "v"], ["液体", "d"], ["体积", "h"], ["。", ""]],
    "tip": "in + 单位 表示「以……为单位」，是状语不是定语。中文提到句首说。",
},

"temperature": {
    "pat": "主谓 + during 时间状语",
    "flow": [["The temperature", "温度", "s"], ["rises", "上升", "v"], ["during the reaction", "在反应过程中", "a"]],
    "core": ["The temperature rises", "温度上升"],
    "asm": [["反应过程中", "a"], ["温度", "s"], ["升高", "v"]],
    "final": [["反应过程中", "a"], ["温度", "s"], ["升高", "v"], ["。", ""]],
    "tip": "during 引导的时间状语英语放句末，中文一律提到句首——「什么时候」先说，这是中文习惯。",
},

"time": {
    "pat": "祈使句 + 后置定语",
    "flow": [["Measure", "要测量……", "v"], ["the time", "某个时间", "h"],
             ["taken", "花掉的", "d"], ["for the solid to dissolve", "用来让固体溶解", "d"]],
    "core": ["Measure the time", "测量……时间"],
    "tree": [[0, "the time", "时间"], [1, "taken", "所需的"], [2, "for the solid to dissolve", "固体溶解"]],
    "asm": [["固体溶解", "d"], ["所需的", "d"], ["时间", "h"]],
    "final": [["测量", "v"], ["固体完全溶解", "d"], ["所需的", "d"], ["时间", "h"], ["。", ""]],
    "tip": "没有主语、动词原形开头 → 祈使句。先抓主干「Measure the time = 测量……时间」，"
           "剩下的全挂在 time 上，一层套一层。中文从最里层往外依次前置，中心词「时间」最后说。",
},

"length": {
    "pat": "祈使句 + of 后置定语",
    "flow": [["Measure", "测量", "v"], ["the length", "长度", "h"], ["of the wire", "导线的", "d"]],
    "core": ["Measure the length", "测量长度"],
    "tree": [[0, "the length", "长度"], [1, "of the wire", "导线的"]],
    "asm": [["导线的", "d"], ["长度", "h"]],
    "final": [["测量", "v"], ["导线的", "d"], ["长度", "h"], ["。", ""]],
    "tip": "最基本的「动词 + 名词 + of 短语」结构，认熟它，后面大量句子都是这个骨架。",
},

"distance": {
    "pat": "主谓宾（travel 带宾语）",
    "flow": [["The particles", "这些粒子", "s"], ["travel", "移动了", "v"], ["a short distance", "一小段距离", "h"]],
    "core": ["The particles travel a distance", "粒子移动一段距离"],
    "final": [["这些粒子", "s"], ["移动了", "v"], ["一小段距离", "h"], ["。", ""]],
    "tip": "travel 在科学英语里是「行进、传播」，后面可直接跟距离作宾语，不是「旅行」。语序与中文一致。",
},

"concentration": {
    "pat": "主谓宾 + 比较级 + per 状语",
    "flow": [["A higher concentration", "更高的浓度", "s"], ["gives", "会带来", "v"],
             ["more particles", "更多粒子", "h"], ["per unit volume", "每单位体积里", "a"]],
    "core": ["A concentration gives particles", "浓度带来粒子"],
    "asm": [["单位体积内", "a"], ["有更多粒子", "h"]],
    "final": [["更高浓度", "s"], ["意味着", "v"], ["单位体积内", "a"], ["有更多粒子", "h"], ["。", ""]],
    "tip": "give 在科学英语里常不是「给」，而是「得出、意味着」。per = 每，"
           "这个状语中文要提到宾语前面说。",
},

"rate": {
    "pat": "of 定语 + with 状语",
    "flow": [["The rate", "速率", "s"], ["of reaction", "反应的", "d"],
             ["decreases", "下降", "v"], ["with time", "随着时间", "a"]],
    "core": ["The rate decreases", "速率下降"],
    "asm": [["反应", "d"], ["速率", "s"], ["随时间", "a"], ["下降", "v"]],
    "final": [["反应速率", "s"], ["随时间", "a"], ["下降", "v"], ["。", ""]],
    "tip": "with time = 随着时间推移，是伴随状语。中文放在动词前面：「随时间下降」。",
},

"increase": {
    "pat": "主谓 + when 时间状语从句（含被动）",
    "flow": [["The pressure", "压强", "s"], ["increases", "升高", "v"],
             ["when the gas is heated", "在气体被加热的时候", "c"]],
    "core": ["The pressure increases", "压强升高"],
    "asm": [["气体受热时", "c"], ["压强", "s"], ["升高", "v"]],
    "final": [["气体受热时", "c"], ["，", ""], ["压强", "s"], ["升高", "v"], ["。", ""]],
    "tip": "when 从句放句末，中文提到句首。从句里 is heated 是被动，中文说「受热」比「被加热」更自然。",
},

"decrease": {
    "pat": "主谓 + when 时间状语从句（含被动）",
    "flow": [["The volume", "体积", "s"], ["decreases", "减小", "v"],
             ["when the gas is compressed", "在气体被压缩的时候", "c"]],
    "core": ["The volume decreases", "体积减小"],
    "asm": [["气体被压缩时", "c"], ["体积", "s"], ["减小", "v"]],
    "final": [["气体被压缩时", "c"], ["，", ""], ["体积", "s"], ["减小", "v"], ["。", ""]],
    "tip": "和 increase 那句是同一个骨架，成对记。条件在后、结果在前 → 中文一律倒过来。",
},

"remain constant": {
    "pat": "系表结构 + during 状语",
    "flow": [["The temperature", "温度", "s"], ["remains constant", "保持不变", "v"],
             ["during boiling", "在沸腾期间", "a"]],
    "core": ["The temperature remains constant", "温度保持不变"],
    "asm": [["沸腾过程中", "a"], ["温度", "s"], ["保持不变", "v"]],
    "final": [["沸腾过程中", "a"], ["温度", "s"], ["保持不变", "v"], ["。", ""]],
    "tip": "remain 是系动词，后面跟形容词 constant 作表语，不能用副词。during 状语中文提前。",
},

"measure": {
    "pat": "祈使句 + 频率状语",
    "flow": [["Measure", "测量", "v"], ["the temperature", "温度", "h"], ["every minute", "每分钟一次", "a"]],
    "core": ["Measure the temperature", "测量温度"],
    "asm": [["每分钟", "a"], ["测量一次", "v"], ["温度", "h"]],
    "final": [["每分钟", "a"], ["测量一次", "v"], ["温度", "h"], ["。", ""]],
    "tip": "every + 时间 表频率，中文提到句首。注意中文要补出「一次」，英语里靠 every 就够了。",
},

"record": {
    "pat": "祈使句 + 方式状语",
    "flow": [["Record", "记录", "v"], ["all observations", "所有观察到的现象", "h"], ["clearly", "要清楚", "a"]],
    "core": ["Record all observations", "记录所有现象"],
    "asm": [["清楚地", "a"], ["记录", "v"], ["所有实验现象", "h"]],
    "final": [["清楚地", "a"], ["记录", "v"], ["所有实验现象", "h"], ["。", ""]],
    "tip": "observation 在实验里指「观察到的现象」，不是「观察」这个动作。副词 clearly 中文提到动词前。",
},

"unit": {
    "pat": "祈使句 + 频度副词 + 地点状语",
    "flow": [["Always", "务必", "a"], ["include", "写上", "v"],
             ["the correct unit", "正确的单位", "h"], ["in your answer", "写在答案里", "a"]],
    "core": ["Include the correct unit", "写出正确单位"],
    "asm": [["答案中", "a"], ["必须写出", "v"], ["正确单位", "h"]],
    "final": [["答案中", "a"], ["必须", "a"], ["写出", "v"], ["正确单位", "h"], ["。", ""]],
    "tip": "always 放在动词前表强调，中文用「必须、务必」对应。漏单位是 IGCSE 最常见的丢分点。",
},

"scale": {
    "pat": "祈使句 + at 方式状语",
    "flow": [["Read", "读", "v"], ["the scale", "刻度", "h"], ["at eye level", "让视线与它齐平", "a"]],
    "core": ["Read the scale", "读刻度"],
    "asm": [["在视线与刻度水平时", "a"], ["读数", "v"]],
    "final": [["在视线与刻度水平时", "a"], ["读数", "v"], ["。", ""]],
    "tip": "at eye level 是「视线齐平」的固定说法，考的是读数姿势。中文把这个条件提到句首。",
},

# ========== 四、物质与粒子模型 ==========

"matter": {
    "pat": "判断句 + because 原因从句（并列谓语）",
    "flow": [["Air", "空气", "s"], ["is matter", "是物质", "v"],
             ["because it has mass", "因为它有质量", "c"], ["and occupies space", "还占据空间", "c"]],
    "core": ["Air is matter", "空气是物质"],
    "final": [["空气", "s"], ["是物质", "v"], ["，", ""], ["因为它有质量并占据空间", "c"], ["。", ""]],
    "tip": "because 从句在英语和中文里都可以放后面，这句语序一致。and 连接从句里的两个并列谓语，主语 it 共用。",
},

"substance": {
    "pat": "判断句 + when 条件从句",
    "flow": [["Water", "水", "s"], ["is a pure substance", "是纯净物", "v"],
             ["when it contains only H₂O", "条件是它只含 H₂O", "c"]],
    "core": ["Water is a pure substance", "水是纯净物"],
    "asm": [["当水中只含 H₂O 时", "c"], ["它是纯净物", "v"]],
    "final": [["当水中只含H₂O 时", "c"], ["，", ""], ["它", "s"], ["是纯净物", "v"], ["。", ""]],
    "tip": "when 在这里不是「当……时刻」而是表条件。中文条件一律前置，所以整个从句要搬到句首。",
},

"material": {
    "pat": "判断句 + for 后置定语",
    "flow": [["Glass", "玻璃", "s"], ["is a useful material", "是一种好用的材料", "v"],
             ["for laboratory equipment", "用来做实验器材的", "d"]],
    "core": ["Glass is a material", "玻璃是材料"],
    "tree": [[0, "a useful material", "常用材料"], [1, "for laboratory equipment", "制造实验器材的"]],
    "asm": [["制造实验器材的", "d"], ["常用材料", "h"]],
    "final": [["玻璃", "s"], ["是", "v"], ["制造实验器材的", "d"], ["常用材料", "h"], ["。", ""]],
    "tip": "for 短语说明材料的用途，是后置定语。中文提到「材料」前面。",
},

"property": {
    "pat": "判断句（最简）",
    "flow": [["Boiling point", "沸点", "s"], ["is", "是", "v"], ["a physical property", "一种物理性质", "h"]],
    "core": ["Boiling point is a property", "沸点是性质"],
    "final": [["沸点", "s"], ["是", "v"], ["一种物理性质", "h"], ["。", ""]],
    "tip": "A is B 判断句，英汉语序完全一致，直译即可。physical 是前置定语，不用移位。",
},

"particle": {
    "pat": "被动语态（be made of）",
    "flow": [["All matter", "所有物质", "s"], ["is made of", "是由……构成的", "v"],
             ["tiny particles", "微小的粒子", "h"]],
    "core": ["Matter is made of particles", "物质由粒子构成"],
    "final": [["所有物质", "s"], ["都", ""], ["由", "v"], ["微小粒子", "h"], ["构成", "v"], ["。", ""]],
    "tip": "be made of = 由……构成（看得出原料）。中文用「由……构成」这个框架，不说「被制造」。",
},

"atom": {
    "pat": "判断句 + of 定语 + that 定语从句",
    "flow": [["An atom", "原子", "s"], ["is the smallest particle", "是最小的粒子", "v"],
             ["of an element", "元素的", "d"],
             ["that takes part in a chemical reaction", "能参加化学反应的", "d"]],
    "core": ["An atom is the smallest particle", "原子是最小的粒子"],
    "tree": [[0, "the smallest particle", "最小粒子"], [1, "of an element", "元素的"],
             [1, "that takes part in a chemical reaction", "能够参加化学反应的"]],
    "asm": [["能够参加化学反应的", "d"], ["元素", "d"], ["最小粒子", "h"]],
    "final": [["原子", "s"], ["是", "v"], ["能够参加化学反应的", "d"], ["元素", "d"], ["最小粒子", "h"], ["。", ""]],
    "tip": "that 引导定语从句，和 of an element 一起修饰 particle——两个定语并列挂在同一个中心词上。"
           "中文全部前置，且离中心词越近的越靠后说。",
},

"molecule": {
    "pat": "主谓宾 + 并列宾语",
    "flow": [["A water molecule", "一个水分子", "s"], ["contains", "含有", "v"],
             ["two hydrogen atoms", "两个氢原子", "h"], ["and one oxygen atom", "和一个氧原子", "h"]],
    "core": ["A molecule contains atoms", "分子含有原子"],
    "final": [["一个水分子", "s"], ["含", "v"], ["两个氢原子和一个氧原子", "h"], ["。", ""]],
    "tip": "and 连接两个并列宾语。英语可数名词要加 s（atoms），中文没有这个变化，别漏读。",
},

"ion": {
    "pat": "主谓宾（have 结构）",
    "flow": [["A sodium ion", "钠离子", "s"], ["has", "带有", "v"], ["a positive charge", "一个正电荷", "h"]],
    "core": ["An ion has a charge", "离子带电荷"],
    "final": [["钠离子", "s"], ["带", "v"], ["正电", "h"], ["。", ""]],
    "tip": "have a charge = 带电。中文常省略量词直接说「带正电」，不必逐字译成「带有一个正电荷」。",
},

"element": {
    "pat": "判断句 + because 原因从句",
    "flow": [["Oxygen", "氧气", "s"], ["is an element", "是元素", "v"],
             ["because it contains only oxygen atoms", "因为它只含氧原子", "c"]],
    "core": ["Oxygen is an element", "氧气是元素"],
    "final": [["氧气", "s"], ["是元素", "v"], ["，", ""], ["因为它只含氧原子", "c"], ["。", ""]],
    "tip": "only 的位置很关键：only oxygen atoms = 只含氧原子（没有别的）。语序与中文一致。",
},

"compound": {
    "pat": "判断句 + of 后置定语",
    "flow": [["Water", "水", "s"], ["is a compound", "是一种化合物", "v"],
             ["of hydrogen and oxygen", "由氢和氧组成的", "d"]],
    "core": ["Water is a compound", "水是化合物"],
    "tree": [[0, "a compound", "化合物"], [1, "of hydrogen and oxygen", "由氢和氧组成的"]],
    "asm": [["由氢和氧组成的", "d"], ["化合物", "h"]],
    "final": [["水", "s"], ["是", "v"], ["由氢和氧组成的", "d"], ["化合物", "h"], ["。", ""]],
    "tip": "a compound of A and B 里的 of 表「由……构成」，译成「由 A 和 B 组成的」，整块前移。",
},

"mixture": {
    "pat": "判断句 + of 后置定语",
    "flow": [["Air", "空气", "s"], ["is a mixture", "是一种混合物", "v"],
             ["of several gases", "由好几种气体混成的", "d"]],
    "core": ["Air is a mixture", "空气是混合物"],
    "tree": [[0, "a mixture", "混合物"], [1, "of several gases", "多种气体的"]],
    "asm": [["多种气体的", "d"], ["混合物", "h"]],
    "final": [["空气", "s"], ["是", "v"], ["多种气体的", "d"], ["混合物", "h"], ["。", ""]],
    "tip": "和 compound 那句结构相同，但含义相反：mixture 是物理混合，compound 是化学结合。成对记。",
},

"pure substance": {
    "pat": "主谓宾（have 结构）",
    "flow": [["A pure substance", "纯净物", "s"], ["has", "具有", "v"],
             ["a fixed composition", "固定的组成", "h"]],
    "core": ["A substance has a composition", "物质有组成"],
    "final": [["纯净物", "s"], ["具有", "v"], ["固定的组成", "h"], ["。", ""]],
    "tip": "fixed 是过去分词作前置定语，在名词前面就不用移位了——只有放在名词后面才需要前移。",
},

"solid": {
    "pat": "主谓宾 + 并列宾语",
    "flow": [["A solid", "固体", "s"], ["has", "具有", "v"],
             ["a fixed shape", "固定的形状", "h"], ["and a fixed volume", "和固定的体积", "h"]],
    "core": ["A solid has a shape and a volume", "固体有形状和体积"],
    "final": [["固体", "s"], ["具有", "v"], ["固定形状和固定体积", "h"], ["。", ""]],
    "tip": "注意 fixed 重复出现了两次，英语不省，中文也照译两遍，强调两个性质都固定。",
},

"liquid": {
    "pat": "主谓宾 + but 转折",
    "flow": [["A liquid", "液体", "s"], ["has a fixed volume", "有固定体积", "v"],
             ["but no fixed shape", "但没有固定形状", "v"]],
    "core": ["A liquid has volume but no shape", "液体有体积但无形状"],
    "final": [["液体", "s"], ["有固定体积", "v"], ["，但", ""], ["没有固定形状", "v"], ["。", ""]],
    "tip": "but no… 是省略说法，完整是 but it has no fixed shape。这种「有 A 但没有 B」是三态对比的固定句式。",
},

"gas": {
    "pat": "主谓宾（最简）",
    "flow": [["A gas", "气体", "s"], ["fills", "充满", "v"], ["the whole container", "整个容器", "h"]],
    "core": ["A gas fills the container", "气体充满容器"],
    "final": [["气体", "s"], ["会充满", "v"], ["整个容器", "h"], ["。", ""]],
    "tip": "一般现在时表示普遍规律，中文可以补一个「会」字来体现这种必然性。",
},

"state of matter": {
    "pat": "并列主语 + 判断句",
    "flow": [["Solid, liquid and gas", "固体、液体和气体", "s"], ["are", "是", "v"],
             ["states of matter", "物质的状态", "h"]],
    "core": ["Solid, liquid and gas are states", "固液气是状态"],
    "asm": [["物质的", "d"], ["三种状态", "h"]],
    "final": [["固体、液体和气体", "s"], ["是", "v"], ["物质的", "d"], ["三种状态", "h"], ["。", ""]],
    "tip": "三个并列主语，谓语用复数 are。states 是复数，中文补出「三种」把这个信息说清楚。",
},

"arrangement": {
    "pat": "主语带 in 定语 + 主谓宾",
    "flow": [["The particles", "粒子", "s"], ["in a solid", "固体里的", "d"],
             ["have", "具有", "v"], ["a regular arrangement", "规则的排列", "h"]],
    "core": ["The particles have an arrangement", "粒子有排列"],
    "asm": [["固体中的", "d"], ["粒子", "s"]],
    "final": [["固体中的", "d"], ["粒子", "s"], ["排列规则", "v"], ["。", ""]],
    "tip": "in a solid 是主语的后置定语，中文前移成「固体中的粒子」。"
           "英语用「have + 名词」，中文直接说成「排列规则」这个主谓结构更顺。",
},

"motion": {
    "pat": "系表结构（be in + 名词）",
    "flow": [["Gas particles", "气体粒子", "s"], ["are in", "处于……状态", "v"],
             ["rapid random motion", "快速随机的运动", "h"]],
    "core": ["Particles are in motion", "粒子处于运动状态"],
    "shift": ["are in rapid random motion", "做快速的随机运动", "英语名词 motion → 中文动词「做……运动」"],
    "final": [["气体粒子", "s"], ["做", "v"], ["快速的随机运动", "h"], ["。", ""]],
    "tip": "be in motion 字面是「处于运动中」，中文说「做运动」更自然——又一处名词化还原成动词。",
},

"fixed position": {
    "pat": "主语带 in 定语 + about 状语",
    "flow": [["Particles", "粒子", "s"], ["in a solid", "固体里的", "d"],
             ["vibrate", "振动", "v"], ["about fixed positions", "绕着固定位置", "a"]],
    "core": ["Particles vibrate", "粒子振动"],
    "asm": [["固体中的", "d"], ["粒子", "s"], ["在固定位置附近", "a"], ["振动", "v"]],
    "final": [["固体中的", "d"], ["粒子", "s"], ["在固定位置附近", "a"], ["振动", "v"], ["。", ""]],
    "tip": "about 在这里不是「关于」，是「围绕、在……附近」。这是固体粒子模型的标准表述。",
},

"compress": {
    "pat": "形容词比较级 + 不定式",
    "flow": [["A gas", "气体", "s"], ["is easier to compress", "更容易被压缩", "v"],
             ["than a liquid", "比液体", "a"]],
    "core": ["A gas is easier to compress", "气体更容易压缩"],
    "asm": [["气体", "s"], ["比液体", "a"], ["更容易被压缩", "v"]],
    "final": [["气体", "s"], ["比液体", "a"], ["更容易被压缩", "v"], ["。", ""]],
    "tip": "「easy to do」里的不定式是主动形式表被动含义——compress 虽是主动，意思却是「被压缩」。"
           "than 比较状语中文要提到形容词前面。",
},

# ========== 五、化学反应、溶液与能量（上） ==========

"reactant": {
    "pat": "并列主语 + 判断句",
    "flow": [["Magnesium and oxygen", "镁和氧气", "s"], ["are", "是", "v"], ["the reactants", "反应物", "h"]],
    "core": ["Magnesium and oxygen are the reactants", "镁和氧气是反应物"],
    "final": [["镁和氧气", "s"], ["是", "v"], ["反应物", "h"], ["。", ""]],
    "tip": "反应物写在箭头左边。两个并列主语，谓语用 are。语序与中文一致。",
},

"product": {
    "pat": "判断句（最简）",
    "flow": [["Magnesium oxide", "氧化镁", "s"], ["is", "是", "v"], ["the product", "生成物", "h"]],
    "core": ["Magnesium oxide is the product", "氧化镁是生成物"],
    "final": [["氧化镁", "s"], ["是", "v"], ["生成物", "h"], ["。", ""]],
    "tip": "生成物写在箭头右边。metal + oxide 是「金属氧化物」的固定命名法。",
},

"chemical reaction": {
    "pat": "主谓宾",
    "flow": [["A chemical reaction", "化学反应", "s"], ["forms", "生成", "v"],
             ["one or more new substances", "一种或多种新物质", "h"]],
    "core": ["A reaction forms substances", "反应生成物质"],
    "final": [["化学反应", "s"], ["会生成", "v"], ["一种或多种新物质", "h"], ["。", ""]],
    "tip": "「有没有生成新物质」是判断化学变化的唯一标准。one or more 表示至少一种。",
},

"physical change": {
    "pat": "判断句 + because 从句（含被动）",
    "flow": [["Melting", "熔化", "s"], ["is a physical change", "是物理变化", "v"],
             ["because no new substance is formed", "因为没有新物质被生成", "c"]],
    "core": ["Melting is a physical change", "熔化是物理变化"],
    "final": [["熔化", "s"], ["是物理变化", "v"], ["，", ""], ["因为没有新物质生成", "c"], ["。", ""]],
    "tip": "从句里 is formed 是被动，主语是 no new substance。中文说「没有新物质生成」，"
           "把被动化掉更自然。",
},

"chemical change": {
    "pat": "判断句（动名词作主语）",
    "flow": [["Rusting", "生锈", "s"], ["is", "是", "v"], ["a chemical change", "一种化学变化", "h"]],
    "core": ["Rusting is a chemical change", "生锈是化学变化"],
    "final": [["生锈", "s"], ["是", "v"], ["一种化学变化", "h"], ["。", ""]],
    "tip": "动名词 Rusting 作主语，中文直接用动词「生锈」即可，不必加「……这件事」。",
},

"dissolve": {
    "pat": "主谓 + in 地点状语",
    "flow": [["Salt", "食盐", "s"], ["dissolves", "溶解", "v"], ["in water", "在水里", "a"]],
    "core": ["Salt dissolves", "食盐溶解"],
    "final": [["食盐", "s"], ["溶解", "v"], ["在水中", "a"], ["。", ""]],
    "tip": "dissolve 是不及物动词，「溶解在」用 dissolve in。这句语序与中文一致，直译即可。",
},

"solution": {
    "pat": "主谓 + when 时间状语从句",
    "flow": [["A solution", "溶液", "s"], ["forms", "形成", "v"],
             ["when a solute dissolves in a solvent", "在溶质溶进溶剂的时候", "c"]],
    "core": ["A solution forms", "溶液形成"],
    "asm": [["溶质溶解在溶剂中", "c"], ["形成溶液", "v"]],
    "final": [["溶质溶解在溶剂中", "c"], ["形成", "v"], ["溶液", "s"], ["。", ""]],
    "tip": "when 从句说明形成的条件，中文提到句首。这句把 solute / solvent / solution 三个词一次说清。",
},

"solute": {
    "pat": "判断句 + in 后置定语",
    "flow": [["Salt", "食盐", "s"], ["is the solute", "是溶质", "v"], ["in salt water", "在盐水里", "d"]],
    "core": ["Salt is the solute", "食盐是溶质"],
    "asm": [["盐水中的", "d"], ["食盐", "s"]],
    "final": [["盐水中的", "d"], ["食盐", "s"], ["是", "v"], ["溶质", "h"], ["。", ""]],
    "tip": "in 短语限定范围，中文提到主语前面：「盐水中的食盐」。被溶解的那个叫溶质。",
},

"solvent": {
    "pat": "判断句 + in 后置定语",
    "flow": [["Water", "水", "s"], ["is the solvent", "是溶剂", "v"], ["in salt water", "在盐水里", "d"]],
    "core": ["Water is the solvent", "水是溶剂"],
    "asm": [["盐水中的", "d"], ["水", "s"]],
    "final": [["盐水中的", "d"], ["水", "s"], ["是", "v"], ["溶剂", "h"], ["。", ""]],
    "tip": "与 solute 那句结构完全相同，成对记：去溶解别人的是溶剂，被溶解的是溶质。",
},

"soluble": {
    "pat": "系表结构 + in 状语",
    "flow": [["Sugar", "糖", "s"], ["is soluble", "是可溶的", "v"], ["in water", "在水里", "a"]],
    "core": ["Sugar is soluble", "糖可溶"],
    "final": [["糖", "s"], ["可溶于", "v"], ["水", "a"], ["。", ""]],
    "tip": "be soluble in = 可溶于。中文把形容词和介词合成一个动词「可溶于」，比直译顺。",
},

"insoluble": {
    "pat": "系表结构 + in 状语",
    "flow": [["Sand", "沙子", "s"], ["is insoluble", "是不溶的", "v"], ["in water", "在水里", "a"]],
    "core": ["Sand is insoluble", "沙子不溶"],
    "final": [["沙子", "s"], ["不溶于", "v"], ["水", "a"], ["。", ""]],
    "tip": "in- 是否定前缀。与 soluble 那句成对记，过滤法能分离的正是 insoluble 的那部分。",
},

"saturated solution": {
    "pat": "否定谓语 + at 条件状语",
    "flow": [["A saturated solution", "饱和溶液", "s"], ["cannot dissolve", "不能再溶解", "v"],
             ["more solute", "更多溶质", "h"], ["at that temperature", "在那个温度下", "a"]],
    "core": ["A solution cannot dissolve solute", "溶液不能溶解溶质"],
    "asm": [["在该温度下", "a"], ["饱和溶液", "s"], ["不能再溶解更多溶质", "v"]],
    "final": [["在该温度下", "a"], ["，", ""], ["饱和溶液", "s"], ["不能再溶解更多溶质", "v"], ["。", ""]],
    "tip": "「at that temperature」不能漏——饱和是有温度前提的，升温后还能继续溶。中文把这个条件提到句首。",
},

"aqueous": {
    "pat": "主谓宾 + 分词后置定语",
    "flow": [["NaCl(aq)", "NaCl(aq)", "s"], ["means", "表示", "v"],
             ["sodium chloride", "氯化钠", "h"], ["dissolved in water", "被溶解在水里的", "d"]],
    "core": ["NaCl(aq) means sodium chloride", "NaCl(aq) 表示氯化钠"],
    "tree": [[0, "sodium chloride", "氯化钠"], [1, "dissolved in water", "溶解在水中的"]],
    "final": [["NaCl(aq)", "s"], ["表示", "v"], ["氯化钠", "h"], ["溶解在水中", "d"], ["。", ""]],
    "tip": "dissolved 是过去分词作后置定语。中文这里顺着说成「氯化钠溶解在水中」比硬前移更自然。",
},

"precipitate": {
    "pat": "主谓 + when 从句（含被动）",
    "flow": [["A white precipitate", "白色沉淀", "s"], ["forms", "生成", "v"],
             ["when the two solutions are mixed", "在两种溶液被混合的时候", "c"]],
    "core": ["A precipitate forms", "沉淀生成"],
    "asm": [["两种溶液混合时", "c"], ["生成白色沉淀", "v"]],
    "final": [["两种溶液混合时", "c"], ["生成", "v"], ["白色沉淀", "s"], ["。", ""]],
    "tip": "are mixed 是被动，中文说「混合时」把被动化掉。沉淀的颜色是重要证据，答题要写清。",
},

"acid": {
    "pat": "主谓 + with 状语",
    "flow": [["Hydrochloric acid", "盐酸", "s"], ["reacts", "反应", "v"], ["with magnesium", "跟镁", "a"]],
    "core": ["Acid reacts", "酸反应"],
    "final": [["盐酸", "s"], ["与", "a"], ["镁", "a"], ["反应", "v"], ["。", ""]],
    "tip": "react with = 与……反应，是固定搭配。中文把 with 短语放动词前面。",
},

"base": {
    "pat": "判断句 + that 定语从句",
    "flow": [["Copper oxide", "氧化铜", "s"], ["is a base", "是一种碱", "v"],
             ["that reacts with acids", "能跟酸反应的", "d"]],
    "core": ["Copper oxide is a base", "氧化铜是碱"],
    "tree": [[0, "a base", "碱性物质"], [1, "that reacts with acids", "能与酸反应的"]],
    "asm": [["能与酸反应的", "d"], ["碱性物质", "h"]],
    "final": [["氧化铜", "s"], ["是", "v"], ["一种能与酸反应的", "d"], ["碱性物质", "h"], ["。", ""]],
    "tip": "that 引导定语从句修饰 base，整块前移。定语从句是英语后置修饰里最长的一类，"
           "但处理办法一样：搬到中心词前面加「的」。",
},

"alkali": {
    "pat": "判断句（最简）",
    "flow": [["Sodium hydroxide", "氢氧化钠", "s"], ["is", "是", "v"], ["an alkali", "一种碱", "h"]],
    "core": ["Sodium hydroxide is an alkali", "氢氧化钠是碱"],
    "final": [["氢氧化钠", "s"], ["是", "v"], ["一种碱", "h"], ["。", ""]],
    "tip": "alkali 特指可溶于水的碱；不溶的只能叫 base。这个区别 IGCSE 常考。",
},

"neutralisation": {
    "pat": "主谓宾（名词化主语）",
    "flow": [["Neutralisation", "中和（反应）", "s"], ["produces", "生成", "v"],
             ["a salt and water", "盐和水", "h"]],
    "core": ["Neutralisation produces salt and water", "中和生成盐和水"],
    "final": [["中和反应", "s"], ["生成", "v"], ["盐和水", "h"], ["。", ""]],
    "tip": "a salt 里的 a 很关键——salt 在这里是「盐类」的统称，不特指食盐。中文补出「反应」二字更清楚。",
},

"indicator": {
    "pat": "主谓宾 + of 后置定语",
    "flow": [["Universal indicator", "通用指示剂", "s"], ["shows", "显示", "v"],
             ["the pH", "pH 值", "h"], ["of a solution", "溶液的", "d"]],
    "core": ["Indicator shows the pH", "指示剂显示 pH"],
    "tree": [[0, "the pH", "pH"], [1, "of a solution", "溶液的"]],
    "asm": [["溶液的", "d"], ["pH", "h"]],
    "final": [["通用指示剂", "s"], ["可以显示", "v"], ["溶液的", "d"], ["pH", "h"], ["。", ""]],
    "tip": "of 短语前移。universal indicator 是「通用指示剂」，能显示整个 pH 范围，不只是变红变蓝。",
},

"pH": {
    "pat": "主语带 with 定语 + 系表",
    "flow": [["A solution", "溶液", "s"], ["with pH 2", "pH 是 2 的", "d"],
             ["is acidic", "呈酸性", "v"]],
    "core": ["A solution is acidic", "溶液呈酸性"],
    "asm": [["pH 为 2 的", "d"], ["溶液", "s"]],
    "final": [["pH 为2 的", "d"], ["溶液", "s"], ["呈酸性", "v"], ["。", ""]],
    "tip": "with 短语作主语的后置定语，中文前移。acidic 是形容词「酸性的」，acid 是名词「酸」，别混。",
},

"catalyst": {
    "pat": "主谓宾 + without 状语（含动名词被动）",
    "flow": [["A catalyst", "催化剂", "s"], ["increases", "提高", "v"],
             ["the rate of reaction", "反应速率", "h"],
             ["without being used up", "而自己不被消耗掉", "a"]],
    "core": ["A catalyst increases the rate", "催化剂提高速率"],
    "asm": [["在自身不被消耗的情况下", "a"], ["提高", "v"], ["反应速率", "h"]],
    "final": [["催化剂", "s"], ["在自身不被消耗的情况下", "a"], ["提高", "v"], ["反应速率", "h"], ["。", ""]],
    "tip": "without + 动名词的被动式 being used up，直译是「没有被用光」。"
           "「自身不被消耗」正是催化剂的定义要点，答题必须写到。",
},

"reaction rate": {
    "pat": "主谓宾 + 比较级",
    "flow": [["Powdered calcium carbonate", "粉末状碳酸钙", "s"], ["has", "具有", "v"],
             ["a faster reaction rate", "更快的反应速率", "h"]],
    "core": ["Calcium carbonate has a rate", "碳酸钙有速率"],
    "final": [["粉末状碳酸钙的", "s"], ["反应速率", "h"], ["更快", "v"], ["。", ""]],
    "tip": "powdered 是过去分词作前置定语，不用移位。中文常把「have + 形容词 + 名词」"
           "改说成「……的 X 更 Y」，读着更顺。",
},

"collision": {
    "pat": "主谓 + when 条件从句",
    "flow": [["A reaction", "反应", "s"], ["occurs", "发生", "v"],
             ["when particles collide successfully", "在粒子有效碰撞的时候", "c"]],
    "core": ["A reaction occurs", "反应发生"],
    "asm": [["粒子发生有效碰撞时", "c"], ["反应才会发生", "v"]],
    "final": [["粒子发生有效碰撞时", "c"], ["，", ""], ["反应才会发生", "v"], ["。", ""]],
    "tip": "successfully 指「有效碰撞」——能量足够且方向合适。中文补一个「才」字把条件的必要性说出来。",
},

"kinetic energy": {
    "pat": "主谓双宾（give sb sth）",
    "flow": [["Heating", "加热", "s"], ["gives", "给予", "v"],
             ["the particles", "粒子", "h"], ["more kinetic energy", "更多动能", "h"]],
    "core": ["Heating gives particles energy", "加热给粒子能量"],
    "final": [["加热", "s"], ["使", "v"], ["粒子", "h"], ["获得更多动能", "v"], ["。", ""]],
    "tip": "give A B 是双宾结构（给 A 一个 B）。中文常改成兼语句「使 A 获得 B」，比「给粒子更多动能」自然。",
},

"attractive force": {
    "pat": "被动语态 + 不定式目的状语",
    "flow": [["Energy", "能量", "s"], ["is needed", "是需要的", "v"],
             ["to overcome the attractive forces", "用来克服吸引力", "a"],
             ["between particles", "粒子之间的", "d"]],
    "core": ["Energy is needed", "需要能量"],
    "tree": [[0, "the attractive forces", "吸引力"], [1, "between particles", "粒子之间的"]],
    "asm": [["克服粒子之间的吸引力", "a"], ["需要能量", "v"]],
    "final": [["克服粒子之间的吸引力", "a"], ["需要", "v"], ["能量", "s"], ["。", ""]],
    "tip": "英语先说「需要能量」再说用途，中文习惯先说用途再说需要什么，整句要前后对调。"
           "between particles 是 forces 的后置定语，照例前移。",
},

"exothermic": {
    "pat": "判断句（最简）",
    "flow": [["Combustion", "燃烧", "s"], ["is", "是", "v"], ["an exothermic reaction", "一种放热反应", "h"]],
    "core": ["Combustion is an exothermic reaction", "燃烧是放热反应"],
    "final": [["燃烧", "s"], ["是", "v"], ["一种放热反应", "h"], ["。", ""]],
    "tip": "exo-（向外）+ therm（热）= 放热，温度计示数会升高。与 endothermic 成对记。",
},

"endothermic": {
    "pat": "判断句 + 频度副词",
    "flow": [["Thermal decomposition", "热分解", "s"], ["is often", "通常是", "v"],
             ["endothermic", "吸热的", "h"]],
    "core": ["Decomposition is endothermic", "分解是吸热的"],
    "final": [["热分解", "s"], ["通常", "v"], ["是吸热过程", "h"], ["。", ""]],
    "tip": "often 是频度副词，放在 be 动词后面。endo-（向内）+ therm（热）= 吸热，温度会下降。",
},

# ========== 五、化学反应、溶液与能量（下·物态变化） ==========

"melting": {
    "pat": "判断句 + from…to 后置定语",
    "flow": [["Melting", "熔化", "s"], ["is the change", "是那个变化", "v"],
             ["from a solid to a liquid", "从固体到液体的", "d"]],
    "core": ["Melting is the change", "熔化是变化"],
    "tree": [[0, "the change", "过程"], [1, "from a solid to a liquid", "固体变为液体的"]],
    "asm": [["固体变为液体的", "d"], ["过程", "h"]],
    "final": [["熔化", "s"], ["是", "v"], ["固体变为液体的", "d"], ["过程", "h"], ["。", ""]],
    "tip": "from A to B 整块是 change 的后置定语，中文前移。change 这里译「过程」比「变化」更顺。",
},

"freezing": {
    "pat": "主谓 + at 温度状语 + under 条件状语",
    "flow": [["Water", "水", "s"], ["freezes", "凝固", "v"],
             ["at 0 °C", "在 0 摄氏度", "a"], ["under normal conditions", "在通常条件下", "a"]],
    "core": ["Water freezes", "水凝固"],
    "asm": [["在通常条件下", "a"], ["水", "s"], ["在 0 摄氏度", "a"], ["凝固", "v"]],
    "final": [["在通常条件下", "a"], ["，", ""], ["水", "s"], ["在0 摄氏度", "a"], ["凝固", "v"], ["。", ""]],
    "tip": "两个状语：at 说温度，under 说前提。中文把范围大的前提放最前，具体数值贴着动词说。",
},

"boiling": {
    "pat": "主谓 + throughout 状语 + at 状语",
    "flow": [["Boiling", "沸腾", "s"], ["occurs", "发生", "v"],
             ["throughout the liquid", "在整个液体内部", "a"], ["at its boiling point", "在沸点时", "a"]],
    "core": ["Boiling occurs", "沸腾发生"],
    "asm": [["液体在沸点时", "a"], ["内部和表面都会发生沸腾", "v"]],
    "final": [["液体在沸点时", "a"], ["，", ""], ["其内部和表面都会", "a"], ["发生沸腾", "v"], ["。", ""]],
    "tip": "throughout = 贯穿整个，正是沸腾与蒸发的关键区别：沸腾整体发生，蒸发只在表面。",
},

"evaporation": {
    "pat": "主谓 + at 地点状语",
    "flow": [["Evaporation", "蒸发", "s"], ["occurs", "发生", "v"],
             ["at the surface", "在表面", "a"], ["of a liquid", "液体的", "d"]],
    "core": ["Evaporation occurs", "蒸发发生"],
    "asm": [["在液体表面", "a"]],
    "final": [["蒸发", "s"], ["发生", "v"], ["在液体表面", "a"], ["。", ""]],
    "tip": "只在表面、任何温度都能发生——这是蒸发；沸腾则要到沸点且整体发生。两句对照记。",
},

"condensation": {
    "pat": "主谓 + 不定式表结果",
    "flow": [["Water vapour", "水蒸气", "s"], ["condenses", "凝结", "v"],
             ["to form liquid water", "从而形成液态水", "a"]],
    "core": ["Water vapour condenses", "水蒸气凝结"],
    "final": [["水蒸气", "s"], ["凝结", "v"], ["形成", "v"], ["液态水", "h"], ["。", ""]],
    "tip": "不定式 to form 在这里表结果，不是目的——凝结之后自然就形成了水。中文直接顺着说。",
},

"sublimation": {
    "pat": "情态动词 + from…to + by 方式状语",
    "flow": [["Iodine", "碘", "s"], ["can change directly", "能够直接变化", "v"],
             ["from a solid to a gas", "从固体到气体", "a"], ["by sublimation", "通过升华", "a"]],
    "core": ["Iodine can change", "碘能变化"],
    "asm": [["通过升华", "a"], ["直接由固体变成气体", "v"]],
    "final": [["碘", "s"], ["可以通过升华", "a"], ["直接", "a"], ["由固体变成气体", "v"], ["。", ""]],
    "tip": "by + 名词 表方式，中文提到动词前。directly 是关键词：跳过液态，不经过熔化。",
},

"deposition": {
    "pat": "判断句 + from…to 后置定语",
    "flow": [["Deposition", "凝华", "s"], ["is the direct change", "是那个直接变化", "v"],
             ["from a gas to a solid", "从气体到固体的", "d"]],
    "core": ["Deposition is the change", "凝华是变化"],
    "tree": [[0, "the direct change", "过程"], [1, "from a gas to a solid", "气体直接变成固体的"]],
    "asm": [["气体直接变成固体的", "d"], ["过程", "h"]],
    "final": [["凝华", "s"], ["是", "v"], ["气体直接变成固体的", "d"], ["过程", "h"], ["。", ""]],
    "tip": "与 sublimation 互为逆过程，结构也和 melting 那句相同。三句放一起记最省力。",
},

# ========== 六、实验器材、操作与安全 ==========

"apparatus": {
    "pat": "祈使句 + for 目的状语",
    "flow": [["Choose", "选择", "v"], ["suitable apparatus", "合适的器材", "h"],
             ["for the experiment", "为这个实验", "a"]],
    "core": ["Choose suitable apparatus", "选择合适器材"],
    "asm": [["为实验", "a"], ["选择", "v"], ["合适的器材", "h"]],
    "final": [["为实验", "a"], ["选择", "v"], ["合适的器材", "h"], ["。", ""]],
    "tip": "apparatus 是不可数名词，没有 -s。for 短语表目的，中文提到句首。",
},

"test tube": {
    "pat": "祈使句 + in 地点状语",
    "flow": [["Heat", "加热", "v"], ["the solution", "溶液", "h"], ["in a test tube", "在试管里", "a"]],
    "core": ["Heat the solution", "加热溶液"],
    "asm": [["在试管中", "a"], ["加热", "v"], ["溶液", "h"]],
    "final": [["在试管中", "a"], ["加热", "v"], ["溶液", "h"], ["。", ""]],
    "tip": "地点状语英语放句末，中文放句首——这是英汉最稳定的一条差异，遇到 in / on / at 就想到前移。",
},

"beaker": {
    "pat": "祈使句 + into 方向状语",
    "flow": [["Pour", "倒", "v"], ["the water", "水", "h"], ["into a beaker", "进烧杯里", "a"]],
    "core": ["Pour the water", "倒水"],
    "final": [["把水", "h"], ["倒入", "v"], ["烧杯", "a"], ["。", ""]],
    "tip": "into 强调「进入内部」，in 只是「在里面」。中文用「把」字句把宾语提前更顺。",
},

"conical flask": {
    "pat": "主谓 + in 地点状语",
    "flow": [["The reaction", "反应", "s"], ["takes place", "进行", "v"],
             ["in a conical flask", "在锥形瓶里", "a"]],
    "core": ["The reaction takes place", "反应进行"],
    "final": [["反应", "s"], ["在锥形瓶中", "a"], ["进行", "v"], ["。", ""]],
    "tip": "take place = 发生、进行，是不及物短语，没有被动式。中文状语提到动词前。",
},

"measuring cylinder": {
    "pat": "祈使句 + 不定式目的状语",
    "flow": [["Use", "使用", "v"], ["a measuring cylinder", "量筒", "h"],
             ["to measure 25 cm³ of water", "来量取 25 立方厘米水", "a"]],
    "core": ["Use a measuring cylinder", "使用量筒"],
    "asm": [["用量筒", "a"], ["量取", "v"], ["25 立方厘米水", "h"]],
    "final": [["用量筒", "a"], ["量取", "v"], ["25 立方厘米水", "h"], ["。", ""]],
    "tip": "「Use A to do B」中文常合并成「用 A 做 B」，不必译成「使用 A 来做 B」两段。",
},

"thermometer": {
    "pat": "祈使句 + in 地点状语",
    "flow": [["Place", "放", "v"], ["the thermometer", "温度计", "h"], ["in the liquid", "进液体里", "a"]],
    "core": ["Place the thermometer", "放温度计"],
    "final": [["把温度计", "h"], ["放入", "v"], ["液体中", "a"], ["。", ""]],
    "tip": "place 作动词是「放置」，比 put 正式，实验步骤里常用。中文用「把」字句。",
},

"balance": {
    "pat": "祈使句 + 不定式目的状语",
    "flow": [["Use", "使用", "v"], ["a balance", "天平", "h"], ["to measure the mass", "来测质量", "a"]],
    "core": ["Use a balance", "使用天平"],
    "asm": [["用天平", "a"], ["测量", "v"], ["质量", "h"]],
    "final": [["用天平", "a"], ["测量", "v"], ["质量", "h"], ["。", ""]],
    "tip": "与 measuring cylinder 那句同一个骨架「Use A to do B」。认熟这个句型，实验题里反复出现。",
},

"funnel": {
    "pat": "祈使句 + inside 地点状语",
    "flow": [["Place", "放", "v"], ["the filter paper", "滤纸", "h"], ["inside the funnel", "在漏斗内侧", "a"]],
    "core": ["Place the filter paper", "放滤纸"],
    "final": [["把滤纸", "h"], ["放在", "v"], ["漏斗中", "a"], ["。", ""]],
    "tip": "inside 比 in 更强调「贴着内壁」。过滤装置的标准组合：漏斗 + 滤纸 + 烧杯。",
},

"filter paper": {
    "pat": "主谓 + on 地点状语",
    "flow": [["The insoluble solid", "不溶的固体", "s"], ["remains", "留下", "v"],
             ["on the filter paper", "在滤纸上", "a"]],
    "core": ["The solid remains", "固体留下"],
    "final": [["不溶性固体", "s"], ["留在", "v"], ["滤纸上", "a"], ["。", ""]],
    "tip": "留在滤纸上的叫 residue（残渣），流过去的叫 filtrate（滤液）。这两个词答题常要用到。",
},

"pipette": {
    "pat": "祈使句 + 不定式 + 方式状语",
    "flow": [["Use", "使用", "v"], ["a pipette", "移液管", "h"],
             ["to add the solution", "来加入溶液", "a"], ["drop by drop", "一滴一滴地", "a"]],
    "core": ["Use a pipette to add the solution", "用移液管加溶液"],
    "asm": [["用移液管", "a"], ["逐滴", "a"], ["加入", "v"], ["溶液", "h"]],
    "final": [["用移液管", "a"], ["逐滴", "a"], ["加入", "v"], ["溶液", "h"], ["。", ""]],
    "tip": "drop by drop 是「逐滴」的固定说法，同类还有 one by one、step by step。中文放动词前。",
},

"Bunsen burner": {
    "pat": "祈使句 + 方式状语",
    "flow": [["Light", "点燃", "v"], ["the Bunsen burner", "本生灯", "h"], ["carefully", "要小心", "a"]],
    "core": ["Light the Bunsen burner", "点燃本生灯"],
    "asm": [["小心", "a"], ["点燃", "v"], ["本生灯", "h"]],
    "final": [["小心", "a"], ["点燃", "v"], ["本生灯", "h"], ["。", ""]],
    "tip": "light 在这里是动词「点燃」，不是名词「光」。副词 carefully 中文提到动词前。",
},

"tripod": {
    "pat": "祈使句 + on 地点状语",
    "flow": [["Place", "放", "v"], ["the beaker", "烧杯", "h"], ["on the tripod", "在三脚架上", "a"]],
    "core": ["Place the beaker", "放烧杯"],
    "final": [["把烧杯", "h"], ["放在", "v"], ["三脚架上", "a"], ["。", ""]],
    "tip": "加热装置从下到上：本生灯 → 三脚架 → 石棉网 → 烧杯。这几句可以串起来记。",
},

"gauze": {
    "pat": "并列谓语",
    "flow": [["The gauze", "石棉网", "s"], ["supports the beaker", "支撑烧杯", "v"],
             ["and spreads the heat", "并把热摊开", "v"]],
    "core": ["The gauze supports and spreads", "网支撑并分散"],
    "final": [["金属网", "s"], ["支撑烧杯", "v"], ["并", ""], ["使热量分布更均匀", "v"], ["。", ""]],
    "tip": "and 连接两个并列谓语，主语共用。spread the heat 直译「摊开热量」，"
           "中文说「使热量分布更均匀」更专业。",
},

"evaporating basin": {
    "pat": "祈使句 + 方式状语 + 地点状语",
    "flow": [["Heat", "加热", "v"], ["the solution", "溶液", "h"],
             ["gently", "要缓慢", "a"], ["in an evaporating basin", "在蒸发皿里", "a"]],
    "core": ["Heat the solution", "加热溶液"],
    "asm": [["在蒸发皿中", "a"], ["缓慢", "a"], ["加热", "v"], ["溶液", "h"]],
    "final": [["在蒸发皿中", "a"], ["缓慢", "a"], ["加热", "v"], ["溶液", "h"], ["。", ""]],
    "tip": "两个状语都要前移，顺序是「地点 → 方式 → 动词」。gently 是结晶实验的关键，猛火会溅出来。",
},

"condenser": {
    "pat": "主谓宾 + into 结果状语",
    "flow": [["The condenser", "冷凝器", "s"], ["cools", "冷却", "v"],
             ["the vapour", "蒸气", "h"], ["into a liquid", "变成液体", "a"]],
    "core": ["The condenser cools the vapour", "冷凝器冷却蒸气"],
    "final": [["冷凝器", "s"], ["把蒸气", "h"], ["冷却成", "v"], ["液体", "a"], ["。", ""]],
    "tip": "「cool A into B」= 把 A 冷却成 B，into 表变化结果。中文用「把」字句最贴。",
},

"heat": {
    "pat": "祈使句 + 方式状语",
    "flow": [["Heat", "加热", "v"], ["the mixture", "混合物", "h"], ["gently", "要缓慢", "a"]],
    "core": ["Heat the mixture", "加热混合物"],
    "asm": [["缓慢", "a"], ["加热", "v"], ["混合物", "h"]],
    "final": [["缓慢", "a"], ["加热", "v"], ["混合物", "h"], ["。", ""]],
    "tip": "最短的祈使句骨架：动词 + 宾语 + 副词。中文只需把副词提前。",
},

"stir": {
    "pat": "祈使句 + with 工具状语",
    "flow": [["Stir", "搅拌", "v"], ["the solution", "溶液", "h"], ["with a glass rod", "用玻璃棒", "a"]],
    "core": ["Stir the solution", "搅拌溶液"],
    "asm": [["用玻璃棒", "a"], ["搅拌", "v"], ["溶液", "h"]],
    "final": [["用玻璃棒", "a"], ["搅拌", "v"], ["溶液", "h"], ["。", ""]],
    "tip": "with + 工具 表「用……」，中文一律提到动词前面。别用手或温度计搅拌，这是考点。",
},

"add": {
    "pat": "祈使句 + 方式状语",
    "flow": [["Add", "加入", "v"], ["the acid", "酸", "h"], ["slowly", "要慢", "a"]],
    "core": ["Add the acid", "加入酸"],
    "asm": [["缓慢", "a"], ["加入", "v"], ["酸", "h"]],
    "final": [["缓慢", "a"], ["加入", "v"], ["酸", "h"], ["。", ""]],
    "tip": "放热反应必须缓慢加酸，否则会暴沸溅出。安全题常考这个 slowly。",
},

"pour": {
    "pat": "祈使句 + 方式状语 + 不定式目的",
    "flow": [["Pour", "倾倒", "v"], ["the liquid", "液体", "h"], ["carefully", "要小心", "a"],
             ["to avoid spilling it", "以免洒出来", "a"]],
    "core": ["Pour the liquid", "倾倒液体"],
    "asm": [["小心", "a"], ["倾倒", "v"], ["液体", "h"], ["避免洒出", "a"]],
    "final": [["小心", "a"], ["倾倒", "v"], ["液体", "h"], ["，", ""], ["避免洒出", "a"], ["。", ""]],
    "tip": "to avoid + 动名词 表目的，中文用「以免、避免」对应，放句末即可，这一处不用前移。",
},

"collect": {
    "pat": "祈使句 + over 方式状语",
    "flow": [["Collect", "收集", "v"], ["the gas", "气体", "h"], ["over water", "在水面上", "a"]],
    "core": ["Collect the gas", "收集气体"],
    "asm": [["用排水法", "a"], ["收集", "v"], ["气体", "h"]],
    "final": [["用排水法", "a"], ["收集", "v"], ["气体", "h"], ["。", ""]],
    "tip": "collect over water 是行话，指「排水集气法」，不能直译成「在水上收集」。"
           "遇到固定实验术语要按中文习惯说法译。",
},

"filter": {
    "pat": "祈使句 + 不定式目的状语",
    "flow": [["Filter", "过滤", "v"], ["the mixture", "混合物", "h"],
             ["to remove the sand", "为了除掉沙子", "a"]],
    "core": ["Filter the mixture", "过滤混合物"],
    "final": [["过滤", "v"], ["混合物", "h"], ["以", ""], ["除去沙子", "a"], ["。", ""]],
    "tip": "不定式表目的，中文用「以、来」引出，放句末，语序与英语一致，不用调。",
},

"evaporate": {
    "pat": "祈使句 + some of 部分表达 + from 状语",
    "flow": [["Evaporate", "蒸发掉", "v"], ["some of the water", "一部分水", "h"],
             ["from the solution", "从溶液里", "a"]],
    "core": ["Evaporate some water", "蒸发掉一些水"],
    "asm": [["蒸发掉", "v"], ["溶液中的", "a"], ["一部分水", "h"]],
    "final": [["蒸发掉", "v"], ["溶液中的", "a"], ["一部分水", "h"], ["。", ""]],
    "tip": "some of the… = ……中的一部分。注意是蒸掉「一部分」不是全部，全蒸干就得不到晶体了。",
},

"crystallise": {
    "pat": "allow…to do + 并列不定式",
    "flow": [["Allow", "让", "v"], ["the concentrated solution", "浓溶液", "h"],
             ["to cool and crystallise", "冷却并结晶", "a"]],
    "core": ["Allow the solution to cool", "让溶液冷却"],
    "final": [["让", "v"], ["浓溶液", "h"], ["冷却并结晶", "a"], ["。", ""]],
    "tip": "allow A to do B = 让 A 去做 B。and 连接两个并列不定式，共用前面的 to。",
},

"distil": {
    "pat": "祈使句 + 不定式目的状语",
    "flow": [["Distil", "蒸馏", "v"], ["the solution", "该溶液", "h"],
             ["to collect pure water", "来收集纯水", "a"]],
    "core": ["Distil the solution", "蒸馏溶液"],
    "final": [["蒸馏", "v"], ["该溶液", "h"], ["以", ""], ["收集纯水", "a"], ["。", ""]],
    "tip": "蒸馏能得到纯溶剂，过滤只能除去不溶物——两种分离方法的目的不同，别混。",
},

"dilute": {
    "pat": "祈使句 + with 工具 + before 时间状语",
    "flow": [["Dilute", "稀释", "v"], ["the acid", "这个酸", "h"],
             ["with water", "用水", "a"], ["before use", "在使用之前", "a"]],
    "core": ["Dilute the acid", "稀释酸"],
    "asm": [["使用前", "a"], ["用水", "a"], ["稀释", "v"], ["该酸", "h"]],
    "final": [["使用前", "a"], ["用水", "a"], ["稀释", "v"], ["该酸", "h"], ["。", ""]],
    "tip": "两个状语都前移，中文顺序是「时间 → 方式 → 动词」。"
           "注意安全：永远是把酸加进水里，不能反过来。",
},

"concentrated": {
    "pat": "被动语态 + with 方式状语",
    "flow": [["Concentrated acid", "浓酸", "s"], ["must be handled", "必须被操作", "v"],
             ["with care", "要小心", "a"]],
    "core": ["Acid must be handled", "酸必须被操作"],
    "asm": [["浓酸", "s"], ["必须", ""], ["小心", "a"], ["操作", "v"]],
    "final": [["浓酸", "s"], ["必须", ""], ["小心操作", "v"], ["。", ""]],
    "tip": "英语被动 must be handled，中文说成主动「必须小心操作」。"
           "with care = carefully，介词短语当副词用。",
},

"flammable": {
    "pat": "并列谓语（系表 + 被动）",
    "flow": [["Ethanol", "乙醇", "s"], ["is flammable", "是易燃的", "v"],
             ["and must be kept away", "而且必须被隔开", "v"], ["from flames", "离火焰远点", "a"]],
    "core": ["Ethanol is flammable and must be kept away", "乙醇易燃且须远离"],
    "final": [["乙醇", "s"], ["易燃", "v"], ["，", ""], ["必须", ""], ["远离火焰", "v"], ["。", ""]],
    "tip": "keep A away from B = 让 A 远离 B。被动式中文化成主动「必须远离」。"
           "顺带一提：inflammable 也是「易燃」，不是反义词，别被 in- 骗了。",
},

"corrosive": {
    "pat": "系表结构（最简）",
    "flow": [["Concentrated acids", "浓酸", "s"], ["are", "是", "v"], ["corrosive", "有腐蚀性的", "h"]],
    "core": ["Acids are corrosive", "酸有腐蚀性"],
    "final": [["浓酸", "s"], ["具有", "v"], ["腐蚀性", "h"], ["。", ""]],
    "tip": "英语用形容词 corrosive，中文常改说成名词「具有腐蚀性」——词性转换的又一例。",
},

"toxic": {
    "pat": "否定祈使句",
    "flow": [["Do not breathe in", "不要吸入", "v"], ["toxic gases", "有毒气体", "h"]],
    "core": ["Do not breathe in gases", "不要吸入气体"],
    "final": [["不要", ""], ["吸入", "v"], ["有毒气体", "h"], ["。", ""]],
    "tip": "Do not + 动词原形 = 否定祈使句。breathe in 是「吸入」，breathe out 是「呼出」。",
},

"safety goggles": {
    "pat": "祈使句 + during 时间状语",
    "flow": [["Wear", "戴", "v"], ["safety goggles", "护目镜", "h"],
             ["during the experiment", "在实验期间", "a"]],
    "core": ["Wear safety goggles", "戴护目镜"],
    "asm": [["实验过程中", "a"], ["佩戴", "v"], ["护目镜", "h"]],
    "final": [["实验过程中", "a"], ["佩戴", "v"], ["护目镜", "h"], ["。", ""]],
    "tip": "during 时间状语中文提到句首。安全题问「一条注意事项」，写这句几乎总能得分。",
},

# ========== 七、物理学基础词汇 ==========

"speed": {
    "pat": "判断句 + 分词定语 + per 状语",
    "flow": [["Speed", "速率", "s"], ["is distance", "就是距离", "v"],
             ["travelled", "走过的", "d"], ["per unit time", "每单位时间", "a"]],
    "core": ["Speed is distance", "速率是距离"],
    "tree": [[0, "distance", "距离"], [1, "travelled", "通过的"], [2, "per unit time", "单位时间内"]],
    "asm": [["单位时间内", "a"], ["通过的", "d"], ["距离", "h"]],
    "final": [["速率", "s"], ["是", "v"], ["单位时间内", "a"], ["通过的", "d"], ["距离", "h"], ["。", ""]],
    "tip": "travelled 是过去分词后置定语，per unit time 又限定它。两层都要前移，中心词「距离」留到最后。",
},

"velocity": {
    "pat": "主谓宾 + both…and",
    "flow": [["Velocity", "速度", "s"], ["includes", "包含", "v"],
             ["both speed and direction", "大小和方向两样", "h"]],
    "core": ["Velocity includes speed and direction", "速度包含大小和方向"],
    "final": [["速度", "s"], ["同时", ""], ["包含", "v"], ["大小和方向", "h"], ["。", ""]],
    "tip": "both A and B = A 和 B 两者都。中文用「同时包含」把 both 的意思带出来。"
           "有方向的是 velocity，没方向的是 speed。",
},

"acceleration": {
    "pat": "判断句 + 两层 of 定语",
    "flow": [["Acceleration", "加速度", "s"], ["is the rate", "是那个快慢", "v"],
             ["of change", "变化的", "d"], ["of velocity", "速度的", "d"]],
    "core": ["Acceleration is the rate", "加速度是快慢"],
    "tree": [[0, "the rate", "快慢"], [1, "of change", "变化的"], [2, "of velocity", "速度的"]],
    "asm": [["速度", "d"], ["变化的", "d"], ["快慢", "h"]],
    "final": [["加速度", "s"], ["是", "v"], ["速度", "d"], ["变化的", "d"], ["快慢", "h"], ["。", ""]],
    "tip": "两个 of 层层套下去：rate of (change of velocity)。中文从最里层「速度」开始往外装。",
},

"force": {
    "pat": "情态动词 + 主谓宾 + of 定语",
    "flow": [["A force", "力", "s"], ["can change", "能够改变", "v"],
             ["the motion", "运动状态", "h"], ["of an object", "物体的", "d"]],
    "core": ["A force can change the motion", "力能改变运动"],
    "tree": [[0, "the motion", "运动状态"], [1, "of an object", "物体的"]],
    "asm": [["物体的", "d"], ["运动状态", "h"]],
    "final": [["力", "s"], ["可以改变", "v"], ["物体的", "d"], ["运动状态", "h"], ["。", ""]],
    "tip": "motion 译成「运动状态」比「运动」准确——力改变的是速度大小或方向，不是让它动起来。",
},

"gravity": {
    "pat": "主谓宾 + towards 方向状语",
    "flow": [["Gravity", "重力", "s"], ["pulls", "拉", "v"],
             ["objects", "物体", "h"], ["towards the Earth", "朝地球去", "a"]],
    "core": ["Gravity pulls objects", "重力拉物体"],
    "final": [["重力", "s"], ["把物体", "h"], ["拉向", "v"], ["地球", "a"], ["。", ""]],
    "tip": "「pull A towards B」中文合成「把 A 拉向 B」，动词和介词并成一个词。",
},

"pressure": {
    "pat": "被动语态 + 介词短语",
    "flow": [["Gas pressure", "气体压强", "s"], ["is caused by", "由……产生", "v"],
             ["particle collisions", "粒子碰撞", "h"], ["with the container walls", "跟容器壁的", "d"]],
    "core": ["Pressure is caused by collisions", "压强由碰撞产生"],
    "tree": [[0, "particle collisions", "粒子碰撞"], [1, "with the container walls", "与容器壁的"]],
    "asm": [["粒子", "h"], ["与容器壁的", "d"], ["碰撞", "h"]],
    "final": [["气体压强", "s"], ["由", "v"], ["粒子与容器壁的", "d"], ["碰撞", "h"], ["产生", "v"], ["。", ""]],
    "tip": "be + 过去分词 = 被动。中文很少说「被产生」，用「由……产生／造成」。"
           "with 短语修饰 collisions，同样要前移。",
},

"density": {
    "pat": "判断句 + 分词短语",
    "flow": [["Density", "密度", "s"], ["is mass", "就是质量", "v"],
             ["divided by volume", "被体积除过的", "d"]],
    "core": ["Density is mass", "密度是质量"],
    "final": [["密度", "s"], ["等于", "v"], ["质量除以体积", "h"], ["。", ""]],
    "tip": "divided by 是过去分词短语作后置定语，字面「被体积除的质量」。"
           "中文按算式说「质量除以体积」就行，不必硬套定语结构。",
},

"electric current": {
    "pat": "判断句 + of 定语（名词化）",
    "flow": [["Electric current", "电流", "s"], ["is the flow", "就是那种流动", "v"],
             ["of electric charge", "电荷的", "d"]],
    "core": ["Current is the flow", "电流是流动"],
    "tree": [[0, "the flow", "移动"], [1, "of electric charge", "电荷的"]],
    "asm": [["电荷的", "d"], ["定向移动", "h"]],
    "final": [["电流", "s"], ["是", "v"], ["电荷的", "d"], ["定向移动", "h"], ["。", ""]],
    "tip": "flow 是名词化的动作。中文译「移动」并补出「定向」——这是电流定义里的关键限定。",
},

"voltage": {
    "pat": "情态动词 + 主谓宾 + per 状语",
    "flow": [["A higher voltage", "更高的电压", "s"], ["can transfer", "能够传递", "v"],
             ["more energy", "更多能量", "h"], ["per unit charge", "每单位电荷", "a"]],
    "core": ["Voltage can transfer energy", "电压能传递能量"],
    "asm": [["使单位电荷", "a"], ["传递", "v"], ["更多能量", "h"]],
    "final": [["更高的电压", "s"], ["可以使单位电荷", "a"], ["传递", "v"], ["更多能量", "h"], ["。", ""]],
    "tip": "per unit charge = 每单位电荷。中文补一个「使」字，把「电压让电荷去传递」的关系说清楚。",
},

"resistance": {
    "pat": "主谓宾 + 比较级 + 频度副词",
    "flow": [["A longer wire", "更长的导线", "s"], ["usually has", "通常具有", "v"],
             ["a greater resistance", "更大的电阻", "h"]],
    "core": ["A wire has resistance", "导线有电阻"],
    "final": [["更长的导线", "s"], ["通常", ""], ["具有", "v"], ["更大的电阻", "h"], ["。", ""]],
    "tip": "两个比较级 longer / greater 前后呼应：越长越大。语序与中文一致，直译即可。",
},

"conductor": {
    "pat": "判断句（最简）",
    "flow": [["Copper", "铜", "s"], ["is", "是", "v"], ["a good electrical conductor", "良好的电导体", "h"]],
    "core": ["Copper is a conductor", "铜是导体"],
    "final": [["铜", "s"], ["是", "v"], ["良好的电导体", "h"], ["。", ""]],
    "tip": "electrical 是前置定语，不用移位。金属都是良导体，因为有自由电子。",
},

"insulator": {
    "pat": "判断句（最简）",
    "flow": [["Plastic", "塑料", "s"], ["is", "是", "v"], ["an electrical insulator", "电绝缘体", "h"]],
    "core": ["Plastic is an insulator", "塑料是绝缘体"],
    "final": [["塑料", "s"], ["是", "v"], ["电绝缘体", "h"], ["。", ""]],
    "tip": "与 conductor 那句成对记。导线外面包塑料，正是这两个词的实际用途。",
},

"wave": {
    "pat": "主谓 + as 方式状语",
    "flow": [["Sound", "声音", "s"], ["travels", "传播", "v"], ["as a wave", "以波的形式", "a"]],
    "core": ["Sound travels", "声音传播"],
    "final": [["声音", "s"], ["以波的形式", "a"], ["传播", "v"], ["。", ""]],
    "tip": "as = 作为、以……形式，这里是方式状语。中文提到动词前面。",
},

"frequency": {
    "pat": "主谓宾 + 比较级",
    "flow": [["A higher frequency", "更高的频率", "s"], ["produces", "产生", "v"],
             ["a higher-pitched sound", "音调更高的声音", "h"]],
    "core": ["Frequency produces sound", "频率产生声音"],
    "final": [["更高的频率", "s"], ["产生", "v"], ["更高的音调", "h"], ["。", ""]],
    "tip": "higher-pitched 是复合形容词（连字符连接），整体作前置定语。"
           "注意区分：pitch 是音调，loudness 才是响度。",
},

"energy transfer": {
    "pat": "判断句 + of 定语",
    "flow": [["Heating", "加热", "s"], ["is a method", "是一种方式", "v"],
             ["of energy transfer", "能量转移的", "d"]],
    "core": ["Heating is a method", "加热是一种方式"],
    "tree": [[0, "a method", "方式"], [1, "of energy transfer", "能量转移的"]],
    "asm": [["能量转移", "d"], ["方式", "h"]],
    "final": [["加热", "s"], ["是", "v"], ["一种能量转移", "d"], ["方式", "h"], ["。", ""]],
    "tip": "动名词 Heating 作主语。of 短语前移，「能量转移方式」是一个整体术语。",
},

# ========== 八、生物与环境基础词汇 ==========

"cell": {
    "pat": "判断句 + of 定语",
    "flow": [["The cell", "细胞", "s"], ["is the basic unit", "是基本单位", "v"], ["of life", "生命的", "d"]],
    "core": ["The cell is the basic unit", "细胞是基本单位"],
    "tree": [[0, "the basic unit", "基本单位"], [1, "of life", "生命的"]],
    "asm": [["生命的", "d"], ["基本单位", "h"]],
    "final": [["细胞", "s"], ["是", "v"], ["生命的", "d"], ["基本单位", "h"], ["。", ""]],
    "tip": "of 短语前移。生命层次：细胞 → 组织 → 器官 → 生物体，这四句可以串起来记。",
},

"tissue": {
    "pat": "判断句 + of 定语 + 分词定语",
    "flow": [["A tissue", "组织", "s"], ["is a group", "是一群", "v"],
             ["of similar cells", "相似细胞的", "d"], ["working together", "一起工作的", "d"]],
    "core": ["A tissue is a group", "组织是一群"],
    "tree": [[0, "a group", "群"], [1, "of similar cells", "相似细胞的"], [2, "working together", "共同工作的"]],
    "asm": [["共同工作的", "d"], ["相似细胞", "d"], ["群", "h"]],
    "final": [["组织", "s"], ["是", "v"], ["共同工作的", "d"], ["相似细胞群", "h"], ["。", ""]],
    "tip": "working together 是现在分词作后置定语，修饰 cells。两层定语都前移，"
           "离中心词越近的越靠后说。",
},

"organ": {
    "pat": "判断句（最简）",
    "flow": [["The heart", "心脏", "s"], ["is", "是", "v"], ["an organ", "一个器官", "h"]],
    "core": ["The heart is an organ", "心脏是器官"],
    "final": [["心脏", "s"], ["是", "v"], ["一个器官", "h"], ["。", ""]],
    "tip": "全书最短的句子之一。A is B 结构，英汉语序完全一致。",
},

"organism": {
    "pat": "判断句 + 复合形容词",
    "flow": [["A bacterium", "细菌", "s"], ["is", "是", "v"],
             ["a single-celled organism", "一种单细胞生物", "h"]],
    "core": ["A bacterium is an organism", "细菌是生物"],
    "final": [["细菌", "s"], ["是", "v"], ["一种单细胞生物", "h"], ["。", ""]],
    "tip": "bacterium 是单数，复数是 bacteria，别搞反。single-celled 是复合形容词作前置定语。",
},

"diffusion": {
    "pat": "判断句 + of 定语 + from…to 定语",
    "flow": [["Diffusion", "扩散", "s"], ["is the net movement", "是那种净移动", "v"],
             ["of particles", "粒子的", "d"],
             ["from high to low concentration", "从高浓度到低浓度的", "d"]],
    "core": ["Diffusion is the net movement", "扩散是净移动"],
    "tree": [[0, "the net movement", "净移动"], [1, "of particles", "粒子的"],
             [1, "from high to low concentration", "由高浓度向低浓度的"]],
    "asm": [["粒子", "d"], ["由高浓度区域向低浓度区域的", "d"], ["净移动", "h"]],
    "final": [["扩散", "s"], ["是", "v"], ["粒子", "d"], ["由高浓度区域向低浓度区域的", "d"],
              ["净移动", "h"], ["。", ""]],
    "tip": "两个定语并排挂在 movement 上：of 说谁在动，from…to 说往哪动。"
           "中文全部前移，中心词「净移动」压到最后。net = 净，不能漏。",
},

"osmosis": {
    "pat": "判断句 + of 定语 + through 定语",
    "flow": [["Osmosis", "渗透", "s"], ["is the movement", "是那种移动", "v"],
             ["of water", "水的", "d"], ["through a partially permeable membrane", "穿过半透膜的", "d"]],
    "core": ["Osmosis is the movement", "渗透是移动"],
    "tree": [[0, "the movement", "移动"], [1, "of water", "水的"],
             [1, "through a partially permeable membrane", "通过半透膜的"]],
    "asm": [["水", "d"], ["通过半透膜的", "d"], ["移动", "h"]],
    "final": [["渗透", "s"], ["是", "v"], ["水", "d"], ["通过半透膜的", "d"], ["移动", "h"], ["。", ""]],
    "tip": "和 diffusion 那句结构一模一样，只是移动的主体限定为「水」，路径限定为「半透膜」。"
           "两句对照着记，考试最爱考这个区别。",
},

"enzyme": {
    "pat": "判断句（最简）",
    "flow": [["An enzyme", "酶", "s"], ["is", "是", "v"], ["a biological catalyst", "一种生物催化剂", "h"]],
    "core": ["An enzyme is a catalyst", "酶是催化剂"],
    "final": [["酶", "s"], ["是", "v"], ["一种生物催化剂", "h"], ["。", ""]],
    "tip": "把酶和 catalyst 那条串起来：催化剂自身不被消耗，酶也一样，但酶怕高温会变性失活。",
},

"respiration": {
    "pat": "主谓宾 + from 来源状语",
    "flow": [["Respiration", "呼吸作用", "s"], ["releases", "释放", "v"],
             ["energy", "能量", "h"], ["from glucose", "从葡萄糖里", "a"]],
    "core": ["Respiration releases energy", "呼吸作用释放能量"],
    "asm": [["从葡萄糖中", "a"], ["释放", "v"], ["能量", "h"]],
    "final": [["呼吸作用", "s"], ["从葡萄糖中", "a"], ["释放", "v"], ["能量", "h"], ["。", ""]],
    "tip": "from 表来源，中文提到动词前面。注意 respiration 是「呼吸作用」这个化学过程，"
           "不是「呼吸」这个动作（那是 breathing）。",
},

"photosynthesis": {
    "pat": "主谓宾 + for 目的状语",
    "flow": [["Plants", "植物", "s"], ["use", "利用", "v"],
             ["light energy", "光能", "h"], ["for photosynthesis", "用来进行光合作用", "a"]],
    "core": ["Plants use light energy", "植物利用光能"],
    "final": [["植物", "s"], ["利用", "v"], ["光能", "h"], ["进行光合作用", "a"], ["。", ""]],
    "tip": "for + 名词表目的。中文把名词 photosynthesis 还原成动宾「进行光合作用」，读着更顺。",
},

"nutrient": {
    "pat": "主谓宾 + for 目的状语",
    "flow": [["Plants", "植物", "s"], ["need", "需要", "v"],
             ["mineral nutrients", "矿物质营养", "h"], ["for healthy growth", "为了健康生长", "a"]],
    "core": ["Plants need nutrients", "植物需要营养"],
    "asm": [["植物健康生长", "a"], ["需要", "v"], ["矿物质营养", "h"]],
    "final": [["植物健康生长", "a"], ["需要", "v"], ["矿物质营养", "h"], ["。", ""]],
    "tip": "for 目的状语中文提到句首，并把名词 growth 还原成动词「生长」——名词化还原的又一例。",
},

"habitat": {
    "pat": "主谓宾 + 省略 that 的定语从句",
    "flow": [["A habitat", "栖息地", "s"], ["provides", "提供", "v"],
             ["the conditions", "那些条件", "h"], ["an organism needs", "生物所需要的", "d"]],
    "core": ["A habitat provides the conditions", "栖息地提供条件"],
    "tree": [[0, "the conditions", "条件"], [1, "(that) an organism needs", "生物生存所需的"]],
    "asm": [["生物", "d"], ["生存所需的", "d"], ["条件", "h"]],
    "final": [["栖息地", "s"], ["为生物", "d"], ["提供", "v"], ["生存所需的", "d"], ["条件", "h"], ["。", ""]],
    "tip": "这里省略了关系词 that——「the conditions (that) an organism needs」。"
           "看到「名词 + 主语 + 谓语」直接相连，就要想到是省略了 that 的定语从句。",
},

"population": {
    "pat": "主谓宾 + of 定语 + in 定语",
    "flow": [["A population", "种群", "s"], ["contains", "包含", "v"],
             ["organisms", "生物", "h"], ["of the same species", "同一物种的", "d"],
             ["in one area", "在同一区域的", "d"]],
    "core": ["A population contains organisms", "种群包含生物"],
    "tree": [[0, "organisms", "生物"], [1, "of the same species", "同一物种的"],
             [1, "in one area", "同一区域内的"]],
    "asm": [["同一区域内", "d"], ["同一物种的", "d"], ["生物", "h"]],
    "final": [["一个种群", "s"], ["由", "v"], ["同一区域内", "d"], ["同一物种的", "d"],
              ["生物", "h"], ["组成", "v"], ["。", ""]],
    "tip": "两个定语并挂在 organisms 上。英语 contains（包含）在中文里说成「由……组成」更自然，"
           "主宾关系正好反过来。",
},

"adaptation": {
    "pat": "判断句 + to 后置定语",
    "flow": [["Thick fur", "厚毛皮", "s"], ["is an adaptation", "是一种适应", "v"],
             ["to a cold environment", "对寒冷环境的", "d"]],
    "core": ["Thick fur is an adaptation", "厚毛皮是适应"],
    "tree": [[0, "an adaptation", "适应"], [1, "to a cold environment", "对寒冷环境的"]],
    "asm": [["对寒冷环境的", "d"], ["一种适应", "h"]],
    "final": [["厚毛皮", "s"], ["是", "v"], ["对寒冷环境的", "d"], ["一种适应", "h"], ["。", ""]],
    "tip": "adaptation to = 对……的适应，介词是 to 不是 for。整块前移。",
},

"ecosystem": {
    "pat": "主谓宾 + 并列宾语",
    "flow": [["An ecosystem", "生态系统", "s"], ["includes", "包括", "v"],
             ["organisms", "生物", "h"], ["and their physical environment", "以及它们的物理环境", "h"]],
    "core": ["An ecosystem includes organisms and environment", "生态系统包括生物和环境"],
    "final": [["生态系统", "s"], ["包括", "v"], ["生物及其物理环境", "h"], ["。", ""]],
    "tip": "and 连接并列宾语。their 指代前面的 organisms，中文用「其」字接住，"
           "「生物及其物理环境」比「生物和它们的物理环境」更凝练。",
},

"food chain": {
    "pat": "主谓宾 + how 宾语从句",
    "flow": [["A food chain", "食物链", "s"], ["shows", "表示", "v"],
             ["how energy passes between organisms", "能量怎样在生物之间传递", "c"]],
    "core": ["A food chain shows how…", "食物链表示……如何"],
    "final": [["食物链", "s"], ["表示", "v"], ["能量如何在生物之间传递", "c"], ["。", ""]],
    "tip": "how 引导宾语从句，整块作 shows 的宾语，语序与中文一致。"
           "食物链的箭头方向就是能量传递方向。",
},

"renewable resource": {
    "pat": "判断句（最简）",
    "flow": [["Solar energy", "太阳能", "s"], ["is", "是", "v"], ["a renewable resource", "一种可再生资源", "h"]],
    "core": ["Solar energy is a resource", "太阳能是资源"],
    "final": [["太阳能", "s"], ["是", "v"], ["一种可再生资源", "h"], ["。", ""]],
    "tip": "re-（再）+ new（新）+ -able（能够）= 可再生的。构词法拆开就懂。",
},

"non-renewable resource": {
    "pat": "判断句（最简）",
    "flow": [["Coal", "煤", "s"], ["is", "是", "v"], ["a non-renewable resource", "一种不可再生资源", "h"]],
    "core": ["Coal is a resource", "煤是资源"],
    "final": [["煤", "s"], ["是", "v"], ["一种不可再生资源", "h"], ["。", ""]],
    "tip": "non- 是否定前缀。与上一句成对记：太阳能用不完，煤用完就没了。",
},

"pollution": {
    "pat": "情态动词 + 主谓宾",
    "flow": [["Air pollution", "空气污染", "s"], ["can harm", "会危害", "v"],
             ["human health", "人体健康", "h"]],
    "core": ["Pollution can harm health", "污染危害健康"],
    "final": [["空气污染", "s"], ["会", ""], ["危害", "v"], ["人体健康", "h"], ["。", ""]],
    "tip": "can 在这里不是「能够」而是表可能性「可能会」。语序与中文一致。",
},

"greenhouse gas": {
    "pat": "判断句（最简）",
    "flow": [["Carbon dioxide", "二氧化碳", "s"], ["is", "是", "v"], ["a greenhouse gas", "一种温室气体", "h"]],
    "core": ["Carbon dioxide is a gas", "二氧化碳是气体"],
    "final": [["二氧化碳", "s"], ["是", "v"], ["一种温室气体", "h"], ["。", ""]],
    "tip": "carbon dioxide = 二氧化碳，di- 表示「二」。greenhouse 原意「温室、暖房」。",
},

"conservation": {
    "pat": "主谓宾（help + 动词原形）",
    "flow": [["Conservation", "保护工作", "s"], ["helps protect", "有助于保护", "v"],
             ["species and habitats", "物种和栖息地", "h"]],
    "core": ["Conservation helps protect", "保护有助于保护"],
    "final": [["保护工作", "s"], ["有助于", "v"], ["保护物种和栖息地", "h"], ["。", ""]],
    "tip": "help 后面可以直接跟动词原形（省略 to）。conservation 也指「守恒」，"
           "如 conservation of energy 能量守恒，看语境判断。",
},

# ========== 衔接课程补充词汇 ==========

"Brownian motion": {
    "pat": "主谓宾 + that 同位语从句",
    "flow": [["Brownian motion", "布朗运动", "s"], ["provides evidence", "提供了证据", "v"],
             ["that particles are constantly moving", "内容是：粒子一直在动", "c"]],
    "core": ["Brownian motion provides evidence", "布朗运动提供证据"],
    "final": [["布朗运动", "s"], ["为", ""], ["粒子持续运动", "c"], ["提供了证据", "v"], ["。", ""]],
    "tip": "that 从句交代 evidence 的具体内容，是同位语从句不是定语从句。"
           "中文用「为……提供了证据」这个框架接住。",
},

"random": {
    "pat": "主谓 + in 方式状语",
    "flow": [["Gas particles", "气体粒子", "s"], ["move", "运动", "v"],
             ["in random directions", "朝随机的方向", "a"]],
    "core": ["Particles move", "粒子运动"],
    "final": [["气体粒子", "s"], ["朝随机方向", "a"], ["运动", "v"], ["。", ""]],
    "tip": "in + 名词表方式，中文提到动词前。directions 用复数，强调方向不止一个、还在变。",
},

"high concentration": {
    "pat": "There be 句型 + of 后置定语",
    "flow": [["There are", "存在", "v"], ["more particles", "更多粒子", "h"],
             ["in a region", "在一个区域里", "a"], ["of high concentration", "高浓度的", "d"]],
    "core": ["There are more particles", "有更多粒子"],
    "tree": [[0, "a region", "区域"], [1, "of high concentration", "高浓度的"]],
    "asm": [["高浓度", "d"], ["区域内的", "a"], ["粒子更多", "h"]],
    "final": [["高浓度区域内的", "a"], ["粒子", "h"], ["更多", "v"], ["。", ""]],
    "tip": "There be 句型直译成「有……」，但中文更常把地点提到句首说「某地有……」。"
           "of 短语修饰 region，照例前移。",
},

"low concentration": {
    "pat": "主谓 + into 方向状语",
    "flow": [["Particles", "粒子", "s"], ["spread", "扩散开", "v"],
             ["into the region", "进入那个区域", "a"], ["of low concentration", "低浓度的", "d"]],
    "core": ["Particles spread", "粒子扩散"],
    "tree": [[0, "the region", "区域"], [1, "of low concentration", "低浓度的"]],
    "asm": [["低浓度", "d"], ["区域", "a"]],
    "final": [["粒子", "s"], ["扩散进入", "v"], ["低浓度区域", "a"], ["。", ""]],
    "tip": "与 high concentration 那句成对：一个说起点粒子多，一个说粒子往终点去。"
           "into 强调「进入内部」，比 in 更有方向感。",
},

"net movement": {
    "pat": "判断句 + from…to 表语",
    "flow": [["The net movement", "净移动", "s"], ["is", "是", "v"],
             ["from high to low concentration", "由高浓度到低浓度", "a"]],
    "core": ["The net movement is from…to…", "净移动是由……到……"],
    "final": [["净移动的方向", "s"], ["是", "v"], ["由高浓度到低浓度", "a"], ["。", ""]],
    "tip": "net = 净、总，指所有随机运动叠加后的结果。中文补出「的方向」，"
           "否则「净移动是由高到低」读着不完整。",
},

"relative molecular mass": {
    "pat": "主语带 with 定语 + 主谓 + 比较级",
    "flow": [["A gas", "一种气体", "s"], ["with a smaller relative molecular mass", "相对分子质量较小的", "d"],
             ["diffuses faster", "扩散得更快", "v"]],
    "core": ["A gas diffuses faster", "气体扩散更快"],
    "tree": [[0, "A gas", "气体"], [1, "with a smaller relative molecular mass", "相对分子质量较小的"]],
    "asm": [["相对分子质量较小的", "d"], ["气体", "s"]],
    "final": [["相对分子质量较小的", "d"], ["气体", "s"], ["扩散更快", "v"], ["。", ""]],
    "tip": "with 短语作主语的后置定语，中文前移。这正是「氨气比氯化氢扩散快」那道题的依据："
           "NH₃ 的 Mr≈17，HCl≈36.5。",
},
}
