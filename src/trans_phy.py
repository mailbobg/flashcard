# -*- coding: utf-8 -*-
"""物理例句的翻译思路。字段与 trans.py 一致，按裸词索引。

与 trans.py 分开是因为同名词（pressure、density…）在两本书里的例句不是同一句，
构建时各自挂到所属的书上。

成分代号与 trans.py 相同：v 谓语 · s 主语 · h 中心词 · d 定语 · a 状语 · c 从句。
final 各段拼起来（去掉空白）必须与词条的 exzh 一致，构建时逐字比对。
"""
TRANS_PHY = {

# ========== 一、题目指令词 ==========

"calculate": {
    "pat": "祈使句：动词 + 宾语",
    "flow": [["Calculate", "计算", "v"], ["the average speed", "平均速度", "h"]],
    "core": ["Calculate the average speed", "计算平均速度"],
    "final": [["计算", "v"], ["平均速度", "h"], ["。", ""]],
    "tip": "指令词开头的祈使句，中文同样不加主语，直接「计算…」。记得带单位。",
},

"compare": {
    "pat": "祈使句：动词 + 宾语",
    "flow": [["Compare", "比较", "v"], ["the two graphs", "两幅图", "h"]],
    "core": ["Compare the two graphs", "比较两幅图"],
    "final": [["比较", "v"], ["两幅图", "h"], ["。", ""]],
    "tip": "compare 要说出相同点和不同点，不能只复述图上数据。",
},

"define": {
    "pat": "祈使句：动词 + 宾语",
    "flow": [["Define", "定义", "v"], ["acceleration", "加速度", "h"]],
    "core": ["Define acceleration", "定义加速度"],
    "final": [["定义", "v"], ["加速度", "h"], ["。", ""]],
    "tip": "define 要用规范定义句，别用例子代替。",
},

"describe": {
    "pat": "祈使句 + of 后置定语",
    "flow": [["Describe", "描述", "v"], ["the motion", "运动", "h"], ["of the car", "汽车的", "d"]],
    "core": ["Describe the motion", "描述运动"],
    "tree": [[0, "the motion", "运动"], [1, "of the car", "汽车的"]],
    "asm": [["汽车的", "d"], ["运动", "h"]],
    "final": [["描述", "v"], ["汽车的", "d"], ["运动", "h"], ["。", ""]],
    "tip": "describe 要按时间顺序讲变化（加速、匀速、减速），不能只给结论。",
},

"determine": {
    "pat": "祈使句 + of 后置定语",
    "flow": [["Determine", "求出", "v"], ["the density", "密度", "h"], ["of the block", "物块的", "d"]],
    "core": ["Determine the density", "求出密度"],
    "tree": [[0, "the density", "密度"], [1, "of the block", "物块的"]],
    "asm": [["物块的", "d"], ["密度", "h"]],
    "final": [["求出", "v"], ["物块的", "d"], ["密度", "h"], ["。", ""]],
    "tip": "determine 要写出计算过程：量出质量体积再算，不能只报答案。",
},

"explain": {
    "pat": "祈使句 + 宾语从句",
    "flow": [["Explain", "解释", "v"], ["why the pressure increases", "压强为什么增大", "h"]],
    "core": ["Explain why the pressure increases", "解释压强为什么增大"],
    "final": [["解释", "v"], ["压强为什么增大", "h"], ["。", ""]],
    "tip": "why 从句作宾语，中文语序一致：压强 + 为什么 + 增大，直接照读。",
},

"identify": {
    "pat": "祈使句：动词 + 宾语",
    "flow": [["Identify", "指出", "v"], ["the independent variable", "自变量", "h"]],
    "core": ["Identify the independent variable", "指出自变量"],
    "final": [["指出", "v"], ["自变量", "h"], ["。", ""]],
    "tip": "identify 是点名，不用展开解释。",
},

"predict": {
    "pat": "祈使句 + what 宾语从句 + when 时间状语",
    "flow": [["Predict", "预测", "v"], ["what happens", "会发生什么", "h"],
             ["when the force increases", "力增大时", "a"]],
    "core": ["Predict what happens", "预测会发生什么"],
    "final": [["预测", "v"], ["力增大时", "a"], ["会发生什么", "h"], ["。", ""]],
    "tip": "when 从句在中文里要提到主句前（先说条件再说结果），语序顺手多了。",
},

"sketch": {
    "pat": "祈使句：动词 + 宾语",
    "flow": [["Sketch", "画草图", "v"], ["a distance–time graph", "一张距离—时间图", "h"]],
    "core": ["Sketch a distance–time graph", "画距离—时间图草图"],
    "final": [["画出", "v"], ["距离—时间图的", "d"], ["草图", "h"], ["。", ""]],
    "tip": "sketch 只要求形状趋势对（起点、斜率走向），不要求逐点精确。",
},

"state": {
    "pat": "祈使句 + of 后置定语",
    "flow": [["State", "写出", "v"], ["the unit", "单位", "h"], ["of force", "力的", "d"]],
    "core": ["State the unit", "写出单位"],
    "tree": [[0, "the unit", "单位"], [1, "of force", "力的"]],
    "asm": [["力的", "d"], ["单位", "h"]],
    "final": [["写出", "v"], ["力的", "d"], ["单位", "h"], ["。", ""]],
    "tip": "state 只要答案本身，不写理由。单位是 N（牛顿）。",
},

"suggest": {
    "pat": "祈使句：动词 + 宾语",
    "flow": [["Suggest", "提出", "v"], ["one improvement", "一项改进建议", "h"]],
    "core": ["Suggest one improvement", "提出一项改进"],
    "final": [["提出", "v"], ["一项改进建议", "h"], ["。", ""]],
    "tip": "suggest 不用保证绝对正确，合理可行即可，但要具体（写清怎么做）。",
},

"show": {
    "pat": "祈使句 + that 宾语从句",
    "flow": [["Show", "说明", "v"], ["that the speed is 5 m/s", "速度是 5 米/秒", "h"]],
    "core": ["Show that the speed is 5 m/s", "说明速度是 5 米/秒"],
    "final": [["说明", "v"], ["速度是5米/秒", "h"], ["。", ""]],
    "tip": "show that 必须给推算过程（把数据代进公式），不能直接写结论。",
},

# ========== 二、测量与数据 ==========

"physical quantity": {
    "pat": "判断句：主语 + be + 宾语",
    "flow": [["Time", "时间", "s"], ["is", "是", "v"], ["a physical quantity", "一种物理量", "h"]],
    "core": ["Time is a physical quantity", "时间是一种物理量"],
    "final": [["时间", "s"], ["是", "v"], ["一种物理量", "h"], ["。", ""]],
    "tip": "物理量 = 有数值有单位（如 5 m），纯数（如 5）不算物理量。",
},

"unit": {
    "pat": "祈使句：副词 + 动词 + 宾语",
    "flow": [["Always", "务必", "a"], ["include", "包含", "v"], ["a unit", "单位", "h"]],
    "core": ["Always include a unit", "务必写单位"],
    "final": [["答案", "s"], ["必须", "a"], ["包含", "v"], ["单位", "h"], ["。", ""]],
    "tip": "主语「答案」是中文补出来的；英文祈使句没有主语，翻译成中文时按习惯补出。",
},

"SI unit": {
    "pat": "判断句 + of 后置定语 + be 表语",
    "flow": [["The SI unit", "国际单位", "s"], ["of mass", "质量的", "d"], ["is", "是", "v"],
             ["the kilogram", "千克", "h"]],
    "core": ["The SI unit of mass is the kilogram", "质量的国际单位是千克"],
    "tree": [[0, "the SI unit", "国际单位"], [1, "of mass", "质量的"]],
    "asm": [["质量的", "d"], ["国际单位", "s"]],
    "final": [["质量的", "d"], ["国际单位", "s"], ["是", "v"], ["千克", "h"], ["。", ""]],
    "tip": "of mass 是后置定语，中文要放到「国际单位」前面。",
},

"length": {
    "pat": "祈使句 + with 方式状语",
    "flow": [["Measure", "测量", "v"], ["the length", "长度", "h"], ["with a ruler", "用直尺", "a"]],
    "core": ["Measure the length", "测量长度"],
    "final": [["用直尺", "a"], ["测量", "v"], ["长度", "h"], ["。", ""]],
    "tip": "with 短语是方式状语，中文习惯放在动词前：用直尺测量。",
},

"mass": {
    "pat": "被动句 + in 方式状语",
    "flow": [["Mass", "质量", "s"], ["is measured", "被测量", "v"], ["in kilograms", "用千克", "a"]],
    "core": ["Mass is measured in kilograms", "质量用千克测量"],
    "final": [["质量", "s"], ["用千克", "a"], ["测量", "v"], ["。", ""]],
    "tip": "is measured in 中文说「用…测量」，不说「被测量于」；in 短语前移到动词前。",
},

"time": {
    "pat": "祈使句 + in 方式状语",
    "flow": [["Record", "记录", "v"], ["the time", "时间", "h"], ["in seconds", "用秒", "a"]],
    "core": ["Record the time", "记录时间"],
    "final": [["用秒", "a"], ["记录", "v"], ["时间", "h"], ["。", ""]],
    "tip": "in seconds = 用秒作单位，中文放动词前。",
},

"volume": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["The volume", "体积", "s"], ["is", "是", "v"], ["50 cm³", "50 立方厘米", "h"]],
    "core": ["The volume is 50 cm³", "体积是 50 立方厘米"],
    "final": [["体积", "s"], ["是", "v"], ["50立方厘米", "h"], ["。", ""]],
    "tip": "cm³ 中文说「立方厘米」；数字和单位连写即可。",
},

"precision": {
    "pat": "判断句：主语 + have + 宾语 + of 后置定语",
    "flow": [["The instrument", "仪器", "s"], ["has a precision", "有精度", "v"], ["of 1 mm", "为 1 毫米", "d"]],
    "core": ["The instrument has a precision of 1 mm", "仪器精度为 1 毫米"],
    "tree": [[0, "a precision", "精度"], [1, "of 1 mm", "为 1 毫米"]],
    "asm": [["精度", "h"], ["为 1 毫米", "d"]],
    "final": [["仪器", "s"], ["精度", "h"], ["为", "v"], ["1毫米", "h"], ["。", ""]],
    "tip": "「有精度为 1 毫米」太绕，中文说「仪器精度为 1 毫米」更顺。",
},

"resolution": {
    "pat": "判断句 + that 定语从句",
    "flow": [["Resolution", "分辨率", "s"], ["is", "是", "v"], ["the smallest change", "最小的变化", "h"],
             ["that can be detected", "能被检测到的", "d"]],
    "core": ["Resolution is the smallest change", "分辨率是最小的变化"],
    "tree": [[0, "the smallest change", "最小的变化"], [1, "that can be detected", "能被检测到的"]],
    "asm": [["能被检测到的", "d"], ["最小变化", "h"]],
    "final": [["分辨率", "s"], ["是", "v"], ["仪器可检测的", "d"], ["最小变化", "h"], ["。", ""]],
    "tip": "that 从句是后置定语，中文放中心词前；「仪器可检测的」比直译「能被检测到的」更贴物理语境。",
},

"uncertainty": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["Every measurement", "每次测量", "s"], ["has", "存在", "v"], ["uncertainty", "不确定度", "h"]],
    "core": ["Every measurement has uncertainty", "每次测量都有不确定度"],
    "final": [["每次测量", "s"], ["都存在", "v"], ["不确定度", "h"], ["。", ""]],
    "tip": "has 译成「存在」更自然：每次测量都存在不确定度。",
},

"error": {
    "pat": "判断句：主语 + 情态 + 谓语 + 宾语",
    "flow": [["Parallax", "视差", "s"], ["can cause", "会造成", "v"], ["a reading error", "读数误差", "h"]],
    "core": ["Parallax can cause a reading error", "视差会造成读数误差"],
    "final": [["视差", "s"], ["会造成", "v"], ["读数误差", "h"], ["。", ""]],
    "tip": "reading error 是「读数误差」不是「读的错误」；reading 作定语。",
},

"parallax": {
    "pat": "祈使句 + 方式状语 + 目的状语",
    "flow": [["Read the scale", "读数", "v"], ["directly from above", "从正上方", "a"],
             ["to avoid parallax", "以避免视差", "a"]],
    "core": ["Read the scale directly from above", "从正上方读数"],
    "final": [["从正上方", "a"], ["读数", "v"], ["以避免视差", "a"], ["。", ""]],
    "tip": "两个状语都往动词前挤：从正上方读数以避免视差。",
},

"repeat": {
    "pat": "祈使句 + 次数状语",
    "flow": [["Repeat", "重复", "v"], ["the measurement", "测量", "h"], ["three times", "三次", "a"]],
    "core": ["Repeat the measurement three times", "重复测量三次"],
    "final": [["重复", "v"], ["测量", "h"], ["三次", "a"], ["。", ""]],
    "tip": "measurement 是名词，中文常说「重复测量」还原成动作。",
},

"mean": {
    "pat": "祈使句 + of 后置定语",
    "flow": [["Calculate", "计算", "v"], ["the mean", "平均值", "h"], ["of the valid results", "有效结果的", "d"]],
    "core": ["Calculate the mean", "计算平均值"],
    "tree": [[0, "the mean", "平均值"], [1, "of the valid results", "有效结果的"]],
    "asm": [["有效结果的", "d"], ["平均值", "h"]],
    "final": [["计算", "v"], ["有效结果的", "d"], ["平均值", "h"], ["。", ""]],
    "tip": "of 短语后置定语，中文前移。mean 在这句是「平均值」。",
},

"anomalous result": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["The value 9.8 s", "9.8 秒这个值", "s"], ["is anomalous", "是异常的", "v"]],
    "core": ["The value 9.8 s is anomalous", "9.8 秒这个值是异常的"],
    "final": [["9.8秒", "s"], ["是", "v"], ["异常结果", "h"], ["。", ""]],
    "tip": "anomalous result 是术语「异常结果」；异常值作图时不连进线里。",
},

"reliable": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["Repeated results", "重复结果", "s"], ["improve", "提高", "v"], ["reliability", "可靠性", "h"]],
    "core": ["Repeated results improve reliability", "重复结果提高可靠性"],
    "final": [["重复结果", "s"], ["提高", "v"], ["可靠性", "h"], ["。", ""]],
    "tip": "improve reliability = 提高可靠性（结果一致才可靠）。",
},

"accurate": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["An accurate value", "准确值", "s"], ["is close to", "接近", "v"], ["the true value", "真实值", "h"]],
    "core": ["An accurate value is close to the true value", "准确值接近真实值"],
    "final": [["准确值", "s"], ["接近", "v"], ["真实值", "h"], ["。", ""]],
    "tip": "accurate = 靠近真值；precise = 多次结果彼此接近。两个概念别混。",
},

# ========== 三、运动 ==========

"motion": {
    "pat": "判断句：主语 + be in + 名词",
    "flow": [["The object", "物体", "s"], ["is in motion", "正在运动", "v"]],
    "core": ["The object is in motion", "物体正在运动"],
    "final": [["物体", "s"], ["正在运动", "v"], ["。", ""]],
    "tip": "be in motion = 处于运动状态，译成「正在运动」。",
},

"rest": {
    "pat": "判断句：主语 + be at + 名词",
    "flow": [["The book", "书", "s"], ["is at rest", "处于静止状态", "v"]],
    "core": ["The book is at rest", "书处于静止状态"],
    "final": [["书", "s"], ["处于静止状态", "v"], ["。", ""]],
    "tip": "at rest 是固定搭配「静止」，与 in motion 相对。",
},

"reference point": {
    "pat": "判断句：主语 + be relative to + 宾语",
    "flow": [["Motion", "运动", "s"], ["is relative to", "相对于", "v"], ["a reference point", "参照物", "h"]],
    "core": ["Motion is relative to a reference point", "运动相对于参照物"],
    "final": [["运动", "s"], ["相对于", "v"], ["参照物", "h"], ["描述", "v"], ["。", ""]],
    "tip": "中文补个「描述」更完整：运动是相对参照物来描述的。",
},

"distance": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["The total distance", "总路程", "s"], ["is", "是", "v"], ["200 m", "200 米", "h"]],
    "core": ["The total distance is 200 m", "总路程是 200 米"],
    "final": [["总路程", "s"], ["是", "v"], ["200米", "h"], ["。", ""]],
    "tip": "distance 在运动学里译「路程」（标量），别译成「距离」。",
},

"displacement": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["Displacement", "位移", "s"], ["includes", "包含", "v"], ["direction", "方向", "h"]],
    "core": ["Displacement includes direction", "位移包含方向"],
    "final": [["位移", "s"], ["包含", "v"], ["方向", "h"], ["。", ""]],
    "tip": "位移是矢量含方向，路程是标量不含方向——这是考点。",
},

"speed": {
    "pat": "判断句：主语 + tell + 宾语从句",
    "flow": [["Speed", "速度", "s"], ["tells us", "告诉我们", "v"], ["how fast an object moves", "物体运动得多快", "h"]],
    "core": ["Speed tells us how fast an object moves", "速度告诉我们物体运动多快"],
    "final": [["速度", "s"], ["表示", "v"], ["物体运动得多快", "h"], ["。", ""]],
    "tip": "tells us 译「表示」或「反映」，比「告诉我们」更书面。",
},

"average speed": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["Average speed", "平均速度", "s"], ["uses", "使用", "v"],
             ["total distance and total time", "总路程和总时间", "h"]],
    "core": ["Average speed uses total distance and total time", "平均速度使用总路程和总时间"],
    "final": [["平均速度", "s"], ["使用", "v"], ["总路程和总时间", "h"], ["。", ""]],
    "tip": "平均速度 = 总路程 ÷ 总时间；公式 v = s / t。",
},

"velocity": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["Velocity", "速度", "s"], ["includes", "包含", "v"], ["direction", "方向", "h"]],
    "core": ["Velocity includes direction", "速度包含方向"],
    "final": [["速度", "s"], ["包含", "v"], ["方向", "h"], ["。", ""]],
    "tip": "velocity 是含方向的矢量，speed 只是速率。",
},

"constant speed": {
    "pat": "判断句：主语 + 谓语 + at 介词短语",
    "flow": [["The car", "汽车", "s"], ["moves", "运动", "v"], ["at constant speed", "以恒定速度", "a"]],
    "core": ["The car moves at constant speed", "汽车以恒定速度运动"],
    "final": [["汽车", "s"], ["以恒定速度", "a"], ["运动", "v"], ["。", ""]],
    "tip": "at + 速度 = 「以…速度」，中文介词短语放动词前。",
},

"acceleration": {
    "pat": "判断句 + in 后置定语",
    "flow": [["Acceleration", "加速度", "s"], ["is", "是", "v"], ["change", "变化", "h"],
             ["in velocity per unit time", "单位时间内速度的", "d"]],
    "core": ["Acceleration is change in velocity per unit time", "加速度是单位时间内的速度变化"],
    "tree": [[0, "change", "变化"], [1, "in velocity per unit time", "单位时间内速度的"]],
    "asm": [["单位时间内速度的", "d"], ["变化", "h"]],
    "final": [["加速度", "s"], ["是", "v"], ["单位时间内速度的", "d"], ["变化", "h"], ["。", ""]],
    "tip": "in 短语是后置定语修饰 change，中文整体提到变化前。a = Δv / t。",
},

"deceleration": {
    "pat": "判断句：主语 + 谓语 + when 时间状语",
    "flow": [["The car", "汽车", "s"], ["decelerates", "减速", "v"], ["when braking", "刹车时", "a"]],
    "core": ["The car decelerates when braking", "汽车刹车时减速"],
    "final": [["汽车", "s"], ["刹车时", "a"], ["减速", "v"], ["。", ""]],
    "tip": "when braking 省略主语，中文补「刹车时」提到动词前。",
},

"initial velocity": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["The initial velocity", "初速度", "s"], ["is", "为", "v"], ["zero", "零", "h"]],
    "core": ["The initial velocity is zero", "初速度为零"],
    "final": [["初速度", "s"], ["为", "v"], ["零", "h"], ["。", ""]],
    "tip": "initial = 初始的，物体从静止出发时初速度为 0。",
},

"final velocity": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["The final velocity", "末速度", "s"], ["is", "为", "v"], ["12 m/s", "12 米/秒", "h"]],
    "core": ["The final velocity is 12 m/s", "末速度为 12 米/秒"],
    "final": [["末速度", "s"], ["为", "v"], ["12米/秒", "h"], ["。", ""]],
    "tip": "final velocity = 到达终点那一刻的速度。",
},

"distance–time graph": {
    "pat": "判断句 + of 后置定语 + be 表语",
    "flow": [["The gradient", "斜率", "s"], ["of a distance–time graph", "距离—时间图的", "d"],
             ["is speed", "是速度", "v"]],
    "core": ["The gradient of a distance–time graph is speed", "距离—时间图的斜率是速度"],
    "tree": [[0, "the gradient", "斜率"], [1, "of a distance–time graph", "距离—时间图的"]],
    "asm": [["距离—时间图的", "d"], ["斜率", "s"]],
    "final": [["距离—时间图的", "d"], ["斜率", "s"], ["表示", "v"], ["速度", "h"], ["。", ""]],
    "tip": "distance–time 图的斜率 = 速度。of 定语前移；中文里的破折号用 —。",
},

"speed–time graph": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["A horizontal line", "水平线", "s"], ["shows", "表示", "v"], ["constant speed", "恒定速度", "h"]],
    "core": ["A horizontal line shows constant speed", "水平线表示恒定速度"],
    "final": [["水平线", "s"], ["表示", "v"], ["恒定速度", "h"], ["。", ""]],
    "tip": "speed–time 图上水平线 = 速度不变；斜率表示加速度。",
},

"gradient": {
    "pat": "比较句：主语 + mean + 宾语",
    "flow": [["A steeper gradient", "越陡的斜率", "s"], ["means", "意味着", "v"], ["greater speed", "更大的速度", "h"]],
    "core": ["A steeper gradient means greater speed", "斜率越陡意味着速度越大"],
    "final": [["斜率越陡", "s"], ["，", ""], ["速度越大", "h"], ["。", ""]],
    "tip": "比较级成对出现，中文说「越…越…」：斜率越陡，速度越大。",
},

"stationary": {
    "pat": "判断句：主语 + 谓语 + 时间段状语",
    "flow": [["The object", "物体", "s"], ["is stationary", "静止", "v"], ["from 4 s to 6 s", "在 4 到 6 秒", "a"]],
    "core": ["The object is stationary from 4 s to 6 s", "物体在 4 到 6 秒静止"],
    "final": [["物体", "s"], ["在4到6秒", "a"], ["静止", "v"], ["。", ""]],
    "tip": "from…to… 时间段作状语，中文放动词前。stationary 是「静止的」。",
},

# ========== 四、力 ==========

"force": {
    "pat": "判断句：主语 + 情态 + 谓语 + 宾语",
    "flow": [["A force", "力", "s"], ["can change", "可以改变", "v"], ["motion", "运动", "h"]],
    "core": ["A force can change motion", "力可以改变运动"],
    "final": [["力", "s"], ["可以改变", "v"], ["运动", "h"], ["。", ""]],
    "tip": "力是矢量：能改变运动状态（快慢或方向）。",
},

"newton": {
    "pat": "被动句 + in 方式状语",
    "flow": [["Force", "力", "s"], ["is measured", "被测量", "v"], ["in newtons", "用牛顿", "a"]],
    "core": ["Force is measured in newtons", "力用牛顿测量"],
    "final": [["力", "s"], ["用牛顿", "a"], ["测量", "v"], ["。", ""]],
    "tip": "力的单位是牛顿 N；1 N = 1 kg·m/s²。",
},

"push": {
    "pat": "判断句：主语 + 谓语 + 宾语 + 副词",
    "flow": [["A push", "推力", "s"], ["moves", "推动", "v"], ["the box", "箱子", "h"], ["away", "远离", "a"]],
    "core": ["A push moves the box away", "推力把箱子推远"],
    "final": [["推力", "s"], ["使", "v"], ["箱子", "h"], ["远离", "v"], ["。", ""]],
    "tip": "moves…away = 使…移开，中文说「使箱子远离」。push 是「推」。",
},

"pull": {
    "pat": "判断句：主语 + 谓语 + 宾语 + 介词短语",
    "flow": [["A pull", "拉力", "s"], ["moves", "使移动", "v"], ["the box", "箱子", "h"],
             ["towards you", "靠近你", "a"]],
    "core": ["A pull moves the box towards you", "拉力使箱子靠近你"],
    "final": [["拉力", "s"], ["使", "v"], ["箱子", "h"], ["靠近你", "v"], ["。", ""]],
    "tip": "push/pull 成对记：推离你 vs 拉向你。",
},

"friction": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["Friction", "摩擦力", "s"], ["opposes", "阻碍", "v"], ["motion", "运动", "h"]],
    "core": ["Friction opposes motion", "摩擦力阻碍运动"],
    "final": [["摩擦力", "s"], ["阻碍", "v"], ["运动", "h"], ["。", ""]],
    "tip": "opposes = 阻碍，摩擦力方向与运动方向相反。",
},

"air resistance": {
    "pat": "判断句：主语 + 谓语 + 介词短语",
    "flow": [["Air resistance", "空气阻力", "s"], ["acts", "作用", "v"], ["opposite to motion", "与运动方向相反", "a"]],
    "core": ["Air resistance acts opposite to motion", "空气阻力与运动方向相反地作用"],
    "final": [["空气阻力", "s"], ["方向与运动方向相反", "v"], ["。", ""]],
    "tip": "中文补「方向」更顺：空气阻力方向与运动方向相反。",
},

"drag": {
    "pat": "判断句：主语 + 谓语 + with 伴随状语",
    "flow": [["Drag", "阻力", "s"], ["increases", "增加", "v"], ["with speed", "随速度", "a"]],
    "core": ["Drag increases with speed", "阻力随速度增加"],
    "final": [["阻力", "s"], ["随速度", "a"], ["增加", "v"], ["。", ""]],
    "tip": "with speed 表示「随速度一起」，中文放在动词前。",
},

"gravity": {
    "pat": "判断句：主语 + 谓语 + 宾语 + towards 介词短语",
    "flow": [["Gravity", "重力", "s"], ["pulls", "拉", "v"], ["objects", "物体", "h"],
             ["towards Earth", "向地球", "a"]],
    "core": ["Gravity pulls objects towards Earth", "重力把物体拉向地球"],
    "final": [["重力", "s"], ["把物体", "h"], ["拉向", "v"], ["地球", "h"], ["。", ""]],
    "tip": "pulls…towards = 把…拉向；中文用「把」字句更顺。",
},

"weight": {
    "pat": "判断句：主语 + be + 宾语",
    "flow": [["Weight", "重量", "s"], ["is", "是", "v"], ["a gravitational force", "一种重力", "h"]],
    "core": ["Weight is a gravitational force", "重量是一种重力"],
    "final": [["重量", "s"], ["是", "v"], ["一种重力", "h"], ["。", ""]],
    "tip": "重量是重力（W = mg），单位 N；质量才是 kg。",
},

"gravitational field strength": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["On Earth", "在地球上", "a"], ["g", "g", "s"], ["is about", "约为", "v"], ["9.8 N/kg", "9.8 牛/千克", "h"]],
    "core": ["g is about 9.8 N/kg", "g 约为 9.8 牛/千克"],
    "final": [["地球表面", "a"], ["g", "s"], ["约为", "v"], ["9.8牛/千克", "h"], ["。", ""]],
    "tip": "On Earth 译「地球表面」；g = 重力场强度，单位 N/kg。",
},

"normal contact force": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["The table", "桌面", "s"], ["exerts", "施加", "v"], ["a normal contact force", "支持力", "h"]],
    "core": ["The table exerts a normal contact force", "桌面施加支持力"],
    "final": [["桌面", "s"], ["对物体", "a"], ["施加", "v"], ["支持力", "h"], ["。", ""]],
    "tip": "「对物体」是中文补的受力对象，使句子完整；normal = 垂直于接触面。",
},

"tension": {
    "pat": "判断句：主语 + be under + 名词",
    "flow": [["The rope", "绳子", "s"], ["is under tension", "受到张力", "v"]],
    "core": ["The rope is under tension", "绳子受到张力"],
    "final": [["绳子", "s"], ["受到张力", "v"], ["。", ""]],
    "tip": "be under tension = 处于拉伸状态 = 受到张力。",
},

"resultant force": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["A non-zero resultant force", "非零合力", "s"], ["causes", "引起", "v"], ["acceleration", "加速度", "h"]],
    "core": ["A non-zero resultant force causes acceleration", "非零合力引起加速度"],
    "final": [["非零合力", "s"], ["引起", "v"], ["加速度", "h"], ["。", ""]],
    "tip": "resultant force 合力；非零合力 → 物体加速（F = ma）。",
},

"balanced forces": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["Balanced forces", "平衡力", "s"], ["give", "给出", "v"], ["zero resultant force", "零合力", "h"]],
    "core": ["Balanced forces give zero resultant force", "平衡力合力为零"],
    "final": [["平衡力的", "d"], ["合力", "s"], ["为", "v"], ["零", "h"], ["。", ""]],
    "tip": "平衡力 → 合力为零 → 物体匀速或静止。",
},

"unbalanced forces": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["Unbalanced forces", "不平衡力", "s"], ["change", "改变", "v"], ["motion", "运动状态", "h"]],
    "core": ["Unbalanced forces change motion", "不平衡力改变运动状态"],
    "final": [["不平衡力", "s"], ["改变", "v"], ["运动状态", "h"], ["。", ""]],
    "tip": "不平衡力 → 合力非零 → 改变运动状态（加速/减速/变向）。",
},

"free fall": {
    "pat": "判断句 + in 介词短语 + be 表语",
    "flow": [["In free fall", "在自由落体中", "a"], ["gravity", "重力", "s"], ["is the only force", "是唯一的力", "v"]],
    "core": ["In free fall, gravity is the only force", "自由落体中重力是唯一的力"],
    "final": [["自由落体中", "a"], ["只有重力", "s"], ["作用", "v"], ["。", ""]],
    "tip": "「只有…作用」比「…是唯一的力」更自然。自由落体只受重力。",
},

"terminal velocity": {
    "pat": "判断句：主语 + 谓语 + when 时间状语",
    "flow": [["Terminal velocity", "终端速度", "s"], ["occurs", "出现", "v"], ["when forces are balanced", "力平衡时", "a"]],
    "core": ["Terminal velocity occurs when forces are balanced", "力平衡时出现终端速度"],
    "final": [["力平衡时", "a"], ["达到", "v"], ["终端速度", "h"], ["。", ""]],
    "tip": "重力 = 阻力时速度不再变 = 终端速度；occurs 译「达到」更贴情境。",
},

# ========== 五、能量、功与功率 ==========

"energy": {
    "pat": "被动句：主语 + be 过去分词",
    "flow": [["Energy", "能量", "s"], ["is conserved", "守恒", "v"]],
    "core": ["Energy is conserved", "能量守恒"],
    "final": [["能量", "s"], ["守恒", "v"], ["。", ""]],
    "tip": "is conserved = 守恒（不增不减，只转移转化）。",
},

"energy store": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["A moving car", "运动汽车", "s"], ["has", "具有", "v"], ["a kinetic energy store", "动能储存", "h"]],
    "core": ["A moving car has a kinetic energy store", "运动汽车具有动能储存"],
    "final": [["运动汽车", "s"], ["具有", "v"], ["动能储存", "h"], ["。", ""]],
    "tip": "energy store 是「能量储存/能量库」，动能是其中一种储存形式。",
},

"kinetic energy": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["Kinetic energy", "动能", "s"], ["depends on", "取决于", "v"], ["mass and speed", "质量和速度", "h"]],
    "core": ["Kinetic energy depends on mass and speed", "动能取决于质量和速度"],
    "final": [["动能", "s"], ["取决于", "v"], ["质量和速度", "h"], ["。", ""]],
    "tip": "E_k = ½mv²：质量和速度共同决定动能。",
},

"gravitational potential energy": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["A raised object", "被举高的物体", "s"], ["has", "具有", "v"],
             ["gravitational potential energy", "重力势能", "h"]],
    "core": ["A raised object has gravitational potential energy", "被举高物体具有重力势能"],
    "final": [["被举高物体", "s"], ["具有", "v"], ["重力势能", "h"], ["。", ""]],
    "tip": "raised = 被举高的；物体越高，重力势能 GPE = mgh 越大。",
},

"elastic potential energy": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["A stretched spring", "被拉伸的弹簧", "s"], ["stores", "储存", "v"], ["elastic energy", "弹性势能", "h"]],
    "core": ["A stretched spring stores elastic energy", "拉伸弹簧储存弹性势能"],
    "final": [["拉伸弹簧", "s"], ["储存", "v"], ["弹性势能", "h"], ["。", ""]],
    "tip": "stretched = 被拉伸的；拉伸/压缩弹簧都储存弹性势能。",
},

"chemical energy": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["Fuel", "燃料", "s"], ["has", "具有", "v"], ["a chemical energy store", "化学能储存", "h"]],
    "core": ["Fuel has a chemical energy store", "燃料具有化学能储存"],
    "final": [["燃料", "s"], ["具有", "v"], ["化学能储存", "h"], ["。", ""]],
    "tip": "燃料、食物都带着化学能库，燃烧时释放。",
},

"thermal energy": {
    "pat": "被动句：主语 + 方式状语",
    "flow": [["Some energy", "部分能量", "s"], ["is transferred", "被转移", "v"], ["thermally", "以热方式", "a"]],
    "core": ["Some energy is transferred thermally", "部分能量以热方式转移"],
    "final": [["部分能量", "s"], ["以热方式", "a"], ["转移", "v"], ["。", ""]],
    "tip": "thermally = 以热量形式；方式状语中文放动词前。",
},

"transfer": {
    "pat": "被动句：主语 + 方式状语",
    "flow": [["Energy", "能量", "s"], ["is transferred", "被转移", "v"], ["electrically", "通过电方式", "a"]],
    "core": ["Energy is transferred electrically", "能量通过电方式转移"],
    "final": [["能量", "s"], ["通过电方式", "a"], ["转移", "v"], ["。", ""]],
    "tip": "能量转移的途径：热、光、电、机械、声音。electrically = 通过电。",
},

"conservation of energy": {
    "pat": "被动句：主语 + be 过去分词",
    "flow": [["Total energy", "总能量", "s"], ["is conserved", "守恒", "v"]],
    "core": ["Total energy is conserved", "总能量守恒"],
    "final": [["总能量", "s"], ["守恒", "v"], ["。", ""]],
    "tip": "能量守恒定律：总能量不增不减。",
},

"work done": {
    "pat": "被动句 + when 时间状语从句",
    "flow": [["Work is done", "做功", "v"], ["when a force moves an object", "力使物体移动时", "a"]],
    "core": ["Work is done when a force moves an object", "力使物体移动时做功"],
    "final": [["力使物体移动时", "a"], ["做功", "v"], ["。", ""]],
    "tip": "做功条件：有力 + 沿力方向有位移。W = F × s。",
},

"joule": {
    "pat": "被动句 + in 方式状语",
    "flow": [["Work", "功", "s"], ["is measured", "被测量", "v"], ["in joules", "用焦耳", "a"]],
    "core": ["Work is measured in joules", "功用焦耳测量"],
    "final": [["功", "s"], ["用焦耳", "a"], ["测量", "v"], ["。", ""]],
    "tip": "功和能量的单位都是焦耳 J；1 J = 1 N·m。",
},

"power": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["Power", "功率", "s"], ["is", "是", "v"], ["energy transferred per unit time", "单位时间转移的能量", "h"]],
    "core": ["Power is energy transferred per unit time", "功率是单位时间转移的能量"],
    "final": [["功率", "s"], ["是", "v"], ["单位时间转移的能量", "h"], ["。", ""]],
    "tip": "功率 P = 能量 ÷ 时间；单位瓦特 W。",
},

"watt": {
    "pat": "被动句 + in 方式状语",
    "flow": [["Power", "功率", "s"], ["is measured", "被测量", "v"], ["in watts", "用瓦特", "a"]],
    "core": ["Power is measured in watts", "功率用瓦特测量"],
    "final": [["功率", "s"], ["用瓦特", "a"], ["测量", "v"], ["。", ""]],
    "tip": "瓦特 W = 焦耳/秒；1 W = 1 J/s。",
},

"useful energy": {
    "pat": "判断句 + of 后置定语",
    "flow": [["Light", "光", "s"], ["is", "是", "v"], ["the useful energy output", "有用能量输出", "h"],
             ["of a lamp", "灯泡的", "d"]],
    "core": ["Light is the useful energy output of a lamp", "光是灯泡的有用能量输出"],
    "tree": [[0, "the useful energy output", "有用能量输出"], [1, "of a lamp", "灯泡的"]],
    "asm": [["灯泡的", "d"], ["有用能量输出", "h"]],
    "final": [["光", "s"], ["是", "v"], ["灯泡的", "d"], ["有用能量输出", "h"], ["。", ""]],
    "tip": "有用能量 = 想要的那部分输出；灯泡的有用输出是光，废热是浪费能量。",
},

"wasted energy": {
    "pat": "判断句：主语 + 情态被动",
    "flow": [["Thermal energy", "内能", "s"], ["may be wasted", "可能被浪费", "v"]],
    "core": ["Thermal energy may be wasted", "内能可能被浪费"],
    "final": [["内能", "s"], ["可能", "a"], ["是", "v"], ["浪费能量", "h"], ["。", ""]],
    "tip": "散失到环境的热 = 浪费能量；能量不消失，只是没被用上。",
},

"efficiency": {
    "pat": "判断句：主语 + 情态 + 谓语 + 宾语",
    "flow": [["Efficiency", "效率", "s"], ["cannot exceed", "不能超过", "v"], ["100%", "100%", "h"]],
    "core": ["Efficiency cannot exceed 100%", "效率不能超过 100%"],
    "final": [["效率", "s"], ["不能超过", "v"], ["100%", "h"], ["。", ""]],
    "tip": "效率 = 有用能量 ÷ 总能量，永远 ≤ 100%（能量不可能凭空增加）。",
},

# ========== 六、密度、压强与流体 ==========

"density": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["Density", "密度", "s"], ["is", "等于", "v"], ["mass divided by volume", "质量除以体积", "h"]],
    "core": ["Density is mass divided by volume", "密度等于质量除以体积"],
    "final": [["密度", "s"], ["等于", "v"], ["质量除以体积", "h"], ["。", ""]],
    "tip": "ρ = m / V；divided by = 除以。",
},

"regular object": {
    "pat": "祈使句 + of 后置定语",
    "flow": [["Measure", "测量", "v"], ["the dimensions", "尺寸", "h"], ["of a regular object", "规则物体的", "d"]],
    "core": ["Measure the dimensions", "测量尺寸"],
    "tree": [[0, "the dimensions", "尺寸"], [1, "of a regular object", "规则物体的"]],
    "asm": [["规则物体的", "d"], ["尺寸", "h"]],
    "final": [["测量", "v"], ["规则物体的", "d"], ["尺寸", "h"], ["。", ""]],
    "tip": "规则物体（长方体等）量长宽高就能算体积，不必用排水法。",
},

"irregular object": {
    "pat": "祈使句 + for 介词短语",
    "flow": [["Use water displacement", "用排水法", "v"], ["for an irregular object", "对不规则物体", "a"]],
    "core": ["Use water displacement", "用排水法"],
    "final": [["不规则物体", "s"], ["用排水法", "a"], ["测体积", "v"], ["。", ""]],
    "tip": "不规则物体的体积用排水法测；中文补「测体积」。",
},

"water displacement": {
    "pat": "被动句 + by 方式状语",
    "flow": [["The stone's volume", "石块的体积", "s"], ["is found", "被测得", "v"],
             ["by water displacement", "通过排水法", "a"]],
    "core": ["The stone's volume is found by water displacement", "石块体积通过排水法测得"],
    "final": [["石块", "d"], ["体积", "s"], ["通过排水法", "a"], ["测得", "v"], ["。", ""]],
    "tip": "排水法：溢出水的体积 = 物体体积。by 方式状语放动词前。",
},

"float": {
    "pat": "判断句：主语 + 谓语 + on 介词短语",
    "flow": [["The object", "物体", "s"], ["floats", "漂浮", "v"], ["on water", "在水面", "a"]],
    "core": ["The object floats on water", "物体漂浮在水面"],
    "final": [["物体", "s"], ["漂浮", "v"], ["在水面", "a"], ["。", ""]],
    "tip": "漂浮 = 密度小于液体，浮力等于重力。",
},

"sink": {
    "pat": "判断句：主语 + 谓语 + because 原因状语",
    "flow": [["The object", "物体", "s"], ["sinks", "下沉", "v"],
             ["because it is denser than water", "因为密度大于水", "a"]],
    "core": ["The object sinks because it is denser than water", "物体因为比水密而下沉"],
    "final": [["物体", "s"], ["因密度大于水", "a"], ["而下沉", "v"], ["。", ""]],
    "tip": "denser than water = 比水密；中文说「因密度大于水」。",
},

"pressure": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["Pressure", "压强", "s"], ["is", "是", "v"], ["force per unit area", "单位面积上的力", "h"]],
    "core": ["Pressure is force per unit area", "压强是单位面积上的力"],
    "final": [["压强", "s"], ["是", "v"], ["单位面积上的力", "h"], ["。", ""]],
    "tip": "p = F / A；per unit area = 每单位面积。",
},

"area": {
    "pat": "比较句：主语 + 谓语 + 宾语",
    "flow": [["A smaller area", "越小的面积", "s"], ["gives", "产生", "v"], ["greater pressure", "越大的压强", "h"]],
    "core": ["A smaller area gives greater pressure", "面积越小压强越大"],
    "final": [["面积越小", "s"], ["压强越大", "h"], ["。", ""]],
    "tip": "同一力作用下，面积越小压强越大——「越…越…」句。",
},

"pascal": {
    "pat": "被动句 + in 方式状语",
    "flow": [["Pressure", "压强", "s"], ["is measured", "被测量", "v"], ["in pascals", "用帕斯卡", "a"]],
    "core": ["Pressure is measured in pascals", "压强用帕斯卡测量"],
    "final": [["压强", "s"], ["用帕斯卡", "a"], ["测量", "v"], ["。", ""]],
    "tip": "压强的单位帕斯卡 Pa；1 Pa = 1 N/m²。",
},

"atmospheric pressure": {
    "pat": "判断句：主语 + 谓语 + in 介词短语",
    "flow": [["Atmospheric pressure", "大气压强", "s"], ["acts", "作用", "v"], ["in all directions", "向各个方向", "a"]],
    "core": ["Atmospheric pressure acts in all directions", "大气压强向各个方向作用"],
    "final": [["大气压强", "s"], ["向各个方向", "a"], ["作用", "v"], ["。", ""]],
    "tip": "大气压 ≈ 101 kPa，向各个方向作用（液体也一样）。",
},

"liquid pressure": {
    "pat": "判断句：主语 + 谓语 + with 伴随状语",
    "flow": [["Liquid pressure", "液体压强", "s"], ["increases", "增加", "v"], ["with depth", "随深度", "a"]],
    "core": ["Liquid pressure increases with depth", "液体压强随深度增加"],
    "final": [["液体压强", "s"], ["随深度", "a"], ["增加", "v"], ["。", ""]],
    "tip": "液体压强随深度增大，潜水越深压强越大。",
},

"upthrust": {
    "pat": "判断句：主语 + 谓语 + on 介词短语",
    "flow": [["Upthrust", "浮力", "s"], ["acts upward", "向上作用", "v"], ["on an object in a fluid", "对流体中的物体", "a"]],
    "core": ["Upthrust acts upward on an object in a fluid", "浮力对流体中的物体向上作用"],
    "final": [["流体中的", "d"], ["物体", "s"], ["受到", "v"], ["向上的浮力", "h"], ["。", ""]],
    "tip": "upthrust 浮力方向向上；中文用「物体受到浮力」的语序。",
},

# ========== 七、热学 ==========

"temperature": {
    "pat": "判断句：主语 + 谓语 + 宾语从句",
    "flow": [["Temperature", "温度", "s"], ["measures", "表示", "v"], ["how hot or cold something is", "物体冷热程度", "h"]],
    "core": ["Temperature measures how hot or cold something is", "温度表示物体的冷热程度"],
    "final": [["温度", "s"], ["表示", "v"], ["物体冷热程度", "h"], ["。", ""]],
    "tip": "温度是冷热程度的量度，不是「热」本身。",
},

"thermal energy transfer": {
    "pat": "判断句：主语 + 谓语 + from…to… 介词短语",
    "flow": [["Thermal energy", "热能", "s"], ["transfers", "转移", "v"], ["from hot to cold", "从高温到低温", "a"]],
    "core": ["Thermal energy transfers from hot to cold", "热能由高温传到低温"],
    "final": [["热能", "s"], ["从高温物体", "a"], ["转移", "v"], ["到低温物体", "a"], ["。", ""]],
    "tip": "热自发从高温传到低温；「物体」是补出来的主语，让句子完整。",
},

"conduction": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["Metals", "金属", "s"], ["are", "是", "v"], ["good thermal conductors", "良好的热导体", "h"]],
    "core": ["Metals are good thermal conductors", "金属是良好的热导体"],
    "final": [["金属", "s"], ["是", "v"], ["良好的热导体", "h"], ["。", ""]],
    "tip": "热传导靠粒子碰撞传递；金属是良导体。",
},

"convection": {
    "pat": "判断句：主语 + 谓语 + in 介词短语",
    "flow": [["Convection", "对流", "s"], ["occurs", "发生", "v"], ["in fluids", "在流体中", "a"]],
    "core": ["Convection occurs in fluids", "对流发生在流体中"],
    "final": [["对流", "s"], ["发生", "v"], ["在流体中", "a"], ["。", ""]],
    "tip": "对流只发生在流体（液体和气体）里：受热上升、变冷下沉形成环流。",
},

"radiation": {
    "pat": "判断句：主语 + 谓语 + 宾语 + through 介词短语",
    "flow": [["Infrared radiation", "红外辐射", "s"], ["transfers", "传递", "v"], ["energy", "能量", "h"],
             ["through a vacuum", "通过真空", "a"]],
    "core": ["Infrared radiation transfers energy through a vacuum", "红外辐射通过真空传递能量"],
    "final": [["红外辐射", "s"], ["可在真空中", "a"], ["传递", "v"], ["能量", "h"], ["。", ""]],
    "tip": "热辐射不需要介质，能穿过真空——太阳的热就是这样来的。",
},

"specific heat capacity": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["Water", "水", "s"], ["has", "有", "v"], ["a high specific heat capacity", "较大的比热容", "h"]],
    "core": ["Water has a high specific heat capacity", "水的比热容较大"],
    "final": [["水的", "d"], ["比热容", "s"], ["较大", "v"], ["。", ""]],
    "tip": "水的比热容大 → 升温慢、降温也慢，海边温差小就靠它。",
},

"melting": {
    "pat": "判断句：主语 + 谓语 + 宾语 + into 介词短语",
    "flow": [["Melting", "熔化", "s"], ["changes", "使改变", "v"], ["a solid", "固体", "h"], ["into a liquid", "变成液体", "a"]],
    "core": ["Melting changes a solid into a liquid", "熔化使固体变成液体"],
    "final": [["熔化", "s"], ["把固体", "h"], ["变成", "v"], ["液体", "h"], ["。", ""]],
    "tip": "change…into… = 把…变成…；熔化过程温度不变（吸收潜热）。",
},

"boiling": {
    "pat": "判断句：主语 + 谓语 + throughout 介词短语",
    "flow": [["Boiling", "沸腾", "s"], ["occurs", "发生", "v"], ["throughout a liquid", "在整个液体中", "a"]],
    "core": ["Boiling occurs throughout a liquid", "沸腾发生在整个液体中"],
    "final": [["沸腾", "s"], ["发生", "v"], ["在液体内部和表面", "a"], ["。", ""]],
    "tip": "沸腾在整个液体内部和表面同时进行；蒸发只在表面。",
},

"evaporation": {
    "pat": "判断句：主语 + 谓语 + at 介词短语",
    "flow": [["Evaporation", "蒸发", "s"], ["occurs", "发生", "v"], ["at the surface", "在表面", "a"]],
    "core": ["Evaporation occurs at the surface", "蒸发发生在表面"],
    "final": [["蒸发", "s"], ["发生", "v"], ["在液体表面", "a"], ["。", ""]],
    "tip": "蒸发只在液体表面，任何温度都能发生；沸腾需要达到沸点。",
},

"condensation": {
    "pat": "判断句：主语 + 谓语 + 宾语 + into 介词短语",
    "flow": [["Condensation", "凝结", "s"], ["changes", "使改变", "v"], ["gas", "气体", "h"], ["into liquid", "变成液体", "a"]],
    "core": ["Condensation changes gas into liquid", "凝结使气体变成液体"],
    "final": [["凝结", "s"], ["把气体", "h"], ["变成", "v"], ["液体", "h"], ["。", ""]],
    "tip": "凝结 = 气体 → 液体，放出热量。",
},

# ========== 八、波、声音与光 ==========

"wave": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["A wave", "波", "s"], ["transfers", "传递", "v"], ["energy", "能量", "h"]],
    "core": ["A wave transfers energy", "波传递能量"],
    "final": [["波", "s"], ["传递", "v"], ["能量", "h"], ["。", ""]],
    "tip": "波传递能量但不传递物质本身。",
},

"transverse wave": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["Light", "光", "s"], ["is", "是", "v"], ["a transverse wave", "横波", "h"]],
    "core": ["Light is a transverse wave", "光是横波"],
    "final": [["光", "s"], ["是", "v"], ["横波", "h"], ["。", ""]],
    "tip": "横波：振动方向 ⊥ 传播方向，光就是横波。",
},

"longitudinal wave": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["Sound in air", "空气中的声波", "s"], ["is longitudinal", "是纵波", "v"]],
    "core": ["Sound in air is longitudinal", "空气中的声波是纵波"],
    "final": [["空气中的", "d"], ["声波", "s"], ["是", "v"], ["纵波", "h"], ["。", ""]],
    "tip": "纵波：振动方向 ∥ 传播方向，声音是纵波。",
},

"amplitude": {
    "pat": "比较句：主语 + 谓语 + 宾语",
    "flow": [["Greater amplitude", "更大的振幅", "s"], ["means", "意味着", "v"], ["more energy", "更多的能量", "h"]],
    "core": ["Greater amplitude means more energy", "振幅越大能量越多"],
    "final": [["振幅越大", "s"], ["，", ""], ["能量越多", "h"], ["。", ""]],
    "tip": "振幅越大，波携带的能量越多、声音越响。",
},

"wavelength": {
    "pat": "被动句 + in 方式状语",
    "flow": [["Wavelength", "波长", "s"], ["is measured", "被测量", "v"], ["in metres", "用米", "a"]],
    "core": ["Wavelength is measured in metres", "波长用米测量"],
    "final": [["波长", "s"], ["用米", "a"], ["测量", "v"], ["。", ""]],
    "tip": "波长 λ = 相邻两个波峰间距离，单位米。",
},

"frequency": {
    "pat": "被动句 + in 方式状语",
    "flow": [["Frequency", "频率", "s"], ["is measured", "被测量", "v"], ["in hertz", "用赫兹", "a"]],
    "core": ["Frequency is measured in hertz", "频率用赫兹测量"],
    "final": [["频率", "s"], ["用赫兹", "a"], ["测量", "v"], ["。", ""]],
    "tip": "频率单位赫兹 Hz，f = 1/T。",
},

"period": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["Period", "周期", "s"], ["is", "是", "v"], ["the time for one complete wave", "一次完整振动所需的时间", "h"]],
    "core": ["Period is the time for one complete wave", "周期是一次完整振动所需的时间"],
    "final": [["周期", "s"], ["是", "v"], ["一次完整振动所需时间", "h"], ["。", ""]],
    "tip": "周期 T = 一次完整振动的时间；T = 1/f。",
},

"wave speed": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["Wave speed", "波速", "s"], ["equals", "等于", "v"], ["frequency times wavelength", "频率乘波长", "h"]],
    "core": ["Wave speed equals frequency times wavelength", "波速等于频率乘波长"],
    "final": [["波速", "s"], ["等于", "v"], ["频率乘波长", "h"], ["。", ""]],
    "tip": "v = f × λ；times = 乘以。",
},

"reflection": {
    "pat": "判断句：主语 + 谓语 + from 介词短语",
    "flow": [["Light", "光", "s"], ["reflects", "反射", "v"], ["from a mirror", "从镜面", "a"]],
    "core": ["Light reflects from a mirror", "光从镜面反射"],
    "final": [["光", "s"], ["从镜面", "a"], ["反射", "v"], ["。", ""]],
    "tip": "反射定律：入射角 = 反射角。",
},

"refraction": {
    "pat": "判断句：主语 + 谓语 + 宾语 + when 时间状语",
    "flow": [["Light", "光", "s"], ["changes direction", "改变方向", "v"], ["when it enters glass", "进入玻璃时", "a"]],
    "core": ["Light changes direction when it enters glass", "光进入玻璃时改变方向"],
    "final": [["光", "s"], ["进入玻璃时", "a"], ["改变方向", "v"], ["。", ""]],
    "tip": "光从一种介质进入另一种介质时方向改变 = 折射。",
},

"normal": {
    "pat": "被动句 + from 介词短语",
    "flow": [["Angles", "角度", "s"], ["are measured", "被测量", "v"], ["from the normal", "从法线", "a"]],
    "core": ["Angles are measured from the normal", "角度从法线量起"],
    "final": [["角度", "s"], ["从法线", "a"], ["量起", "v"], ["。", ""]],
    "tip": "法线是垂直界面的虚线，入射角/反射角都从它量。",
},

"angle of incidence": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["The angle of incidence", "入射角", "s"], ["equals", "等于", "v"], ["the angle of reflection", "反射角", "h"]],
    "core": ["The angle of incidence equals the angle of reflection", "入射角等于反射角"],
    "final": [["入射角", "s"], ["等于", "v"], ["反射角", "h"], ["。", ""]],
    "tip": "入射角 i = 反射角 r（反射定律）；角度都从法线量。",
},

"sound": {
    "pat": "判断句：主语 + 谓语 + 宾语 + 不定式目的",
    "flow": [["Sound", "声音", "s"], ["needs", "需要", "v"], ["a medium", "介质", "h"], ["to travel", "来传播", "a"]],
    "core": ["Sound needs a medium to travel", "声音传播需要介质"],
    "final": [["声音", "s"], ["传播", "v"], ["需要", "v"], ["介质", "h"], ["。", ""]],
    "tip": "to travel 不定式表目的；中文「传播需要介质」语序更顺。",
},

"vacuum": {
    "pat": "判断句：主语 + 情态否定 + through 介词短语",
    "flow": [["Sound", "声音", "s"], ["cannot travel", "不能传播", "v"], ["through a vacuum", "通过真空", "a"]],
    "core": ["Sound cannot travel through a vacuum", "声音不能通过真空传播"],
    "final": [["声音", "s"], ["不能", "a"], ["在真空中", "a"], ["传播", "v"], ["。", ""]],
    "tip": "真空没有介质，声音传不了；光可以。",
},

"echo": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["An echo", "回声", "s"], ["is", "是", "v"], ["reflected sound", "反射的声音", "h"]],
    "core": ["An echo is reflected sound", "回声是反射的声音"],
    "final": [["回声", "s"], ["是", "v"], ["反射的声音", "h"], ["。", ""]],
    "tip": "回声 = 声波碰到障碍物反射回来。",
},

# ========== 九、电与磁 ==========

"electric charge": {
    "pat": "被动句 + in 方式状语",
    "flow": [["Charge", "电荷", "s"], ["is measured", "被测量", "v"], ["in coulombs", "用库仑", "a"]],
    "core": ["Charge is measured in coulombs", "电荷量用库仑测量"],
    "final": [["电荷量", "s"], ["用库仑", "a"], ["测量", "v"], ["。", ""]],
    "tip": "「电荷量」比「电荷」更准；单位库仑 C。",
},

"current": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["Current", "电流", "s"], ["is", "是", "v"], ["the rate of flow of charge", "电荷流动的速率", "h"]],
    "core": ["Current is the rate of flow of charge", "电流是电荷流动的速率"],
    "final": [["电流", "s"], ["是", "v"], ["电荷流动的速率", "h"], ["。", ""]],
    "tip": "电流 I = 单位时间流过的电荷；rate of flow = 流动速率。",
},

"ampere": {
    "pat": "被动句 + in 方式状语",
    "flow": [["Current", "电流", "s"], ["is measured", "被测量", "v"], ["in amperes", "用安培", "a"]],
    "core": ["Current is measured in amperes", "电流用安培测量"],
    "final": [["电流", "s"], ["用安培", "a"], ["测量", "v"], ["。", ""]],
    "tip": "电流单位安培 A；1 A = 1 C/s。",
},

"potential difference": {
    "pat": "判断句：主语 + 谓语 + 宾语 + 后置定语",
    "flow": [["Potential difference", "电势差", "s"], ["transfers", "转移", "v"], ["energy", "能量", "h"],
             ["per unit charge", "单位电荷的", "d"]],
    "core": ["Potential difference transfers energy", "电势差转移能量"],
    "tree": [[0, "energy", "能量"], [1, "per unit charge", "单位电荷的"]],
    "asm": [["单位电荷的", "d"], ["能量", "h"]],
    "final": [["电势差", "s"], ["表示", "v"], ["单位电荷转移的", "d"], ["能量", "h"], ["。", ""]],
    "tip": "电势差（电压）= 单位电荷获得的能量；V = E / Q。",
},

"voltage": {
    "pat": "被动句 + in 方式状语",
    "flow": [["Voltage", "电压", "s"], ["is measured", "被测量", "v"], ["in volts", "用伏特", "a"]],
    "core": ["Voltage is measured in volts", "电压用伏特测量"],
    "final": [["电压", "s"], ["用伏特", "a"], ["测量", "v"], ["。", ""]],
    "tip": "电压单位伏特 V；用伏特计并联测量。",
},

"resistance": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["Resistance", "电阻", "s"], ["opposes", "阻碍", "v"], ["current", "电流", "h"]],
    "core": ["Resistance opposes current", "电阻阻碍电流"],
    "final": [["电阻", "s"], ["阻碍", "v"], ["电流", "h"], ["。", ""]],
    "tip": "R = V / I；电阻越大电流越小。",
},

"circuit": {
    "pat": "判断句：主语 + 谓语 + in 介词短语",
    "flow": [["Current", "电流", "s"], ["flows", "流动", "v"], ["in a complete circuit", "在完整电路中", "a"]],
    "core": ["Current flows in a complete circuit", "电流在完整电路中流动"],
    "final": [["电流", "s"], ["在完整电路中", "a"], ["流动", "v"], ["。", ""]],
    "tip": "电路闭合才有电流流通；complete = 完整的/闭合的。",
},

"series circuit": {
    "pat": "判断句：主语 + be + 表语 + in 介词短语",
    "flow": [["Current", "电流", "s"], ["is the same", "相同", "v"], ["in a series circuit", "在串联电路中", "a"]],
    "core": ["Current is the same in a series circuit", "串联电路中电流相同"],
    "final": [["串联电路中", "a"], ["各处", "a"], ["电流", "s"], ["相同", "v"], ["。", ""]],
    "tip": "串联电路处处电流相同；「各处」是补出来让句子完整的。",
},

"parallel circuit": {
    "pat": "判断句：主语 + be + 表语 + across 介词短语",
    "flow": [["Potential difference", "电压", "s"], ["is the same", "相同", "v"],
             ["across parallel branches", "并联支路两端", "a"]],
    "core": ["Potential difference is the same across parallel branches", "并联支路两端电压相同"],
    "final": [["并联支路两端", "a"], ["电压", "s"], ["相同", "v"], ["。", ""]],
    "tip": "并联各支路两端电压相同；串联则电流相同。",
},

"conductor": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["Copper", "铜", "s"], ["is", "是", "v"], ["a good conductor", "良导体", "h"]],
    "core": ["Copper is a good conductor", "铜是良导体"],
    "final": [["铜", "s"], ["是", "v"], ["良导体", "h"], ["。", ""]],
    "tip": "conductor 导体——金属（铜、铝）都是良导体。",
},

"insulator": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["Plastic", "塑料", "s"], ["is", "是", "v"], ["an electrical insulator", "电绝缘体", "h"]],
    "core": ["Plastic is an electrical insulator", "塑料是电绝缘体"],
    "final": [["塑料", "s"], ["是", "v"], ["电绝缘体", "h"], ["。", ""]],
    "tip": "绝缘体不导电（塑料、橡胶、玻璃），与导体相对。",
},

"magnetic field": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["A magnetic field", "磁场", "s"], ["surrounds", "包围", "v"], ["a magnet", "磁体", "h"]],
    "core": ["A magnetic field surrounds a magnet", "磁场包围磁体"],
    "final": [["磁体周围", "a"], ["存在", "v"], ["磁场", "s"], ["。", ""]],
    "tip": "磁体周围存在磁场；磁感线从 N 极到 S 极。",
},

"electromagnet": {
    "pat": "判断句：主语 + 情态被动",
    "flow": [["An electromagnet", "电磁铁", "s"], ["can be switched on and off", "可以接通和断开", "v"]],
    "core": ["An electromagnet can be switched on and off", "电磁铁可以接通和断开"],
    "final": [["电磁铁", "s"], ["可以接通和断开", "v"], ["。", ""]],
    "tip": "电磁铁靠电流产生磁性，断电就消磁——可以开关。",
},

"transformer": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["A transformer", "变压器", "s"], ["changes", "改变", "v"], ["alternating voltage", "交流电压", "h"]],
    "core": ["A transformer changes alternating voltage", "变压器改变交流电压"],
    "final": [["变压器", "s"], ["改变", "v"], ["交流电压", "h"], ["。", ""]],
    "tip": "变压器只对交流电工作，靠电磁感应升降电压。",
},

# ========== 十、原子核与空间物理 ==========

"atom": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["An atom", "原子", "s"], ["has", "有", "v"], ["a nucleus and electrons", "原子核和电子", "h"]],
    "core": ["An atom has a nucleus and electrons", "原子有原子核和电子"],
    "final": [["原子", "s"], ["由", "v"], ["原子核和电子", "h"], ["组成", "v"], ["。", ""]],
    "tip": "「由…组成」比「有…」更符合中文表述：原子由原子核和电子组成。",
},

"nucleus": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["The nucleus", "原子核", "s"], ["contains", "包含", "v"], ["protons and neutrons", "质子和中子", "h"]],
    "core": ["The nucleus contains protons and neutrons", "原子核包含质子和中子"],
    "final": [["原子核", "s"], ["包含", "v"], ["质子和中子", "h"], ["。", ""]],
    "tip": "原子核 = 质子 + 中子；电子在核外绕行。",
},

"proton": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["A proton", "质子", "s"], ["has", "带", "v"], ["positive charge", "正电", "h"]],
    "core": ["A proton has positive charge", "质子带正电"],
    "final": [["质子", "s"], ["带", "v"], ["正电", "h"], ["。", ""]],
    "tip": "质子带正电；质子数决定元素种类。",
},

"neutron": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["A neutron", "中子", "s"], ["has no charge", "不带电", "v"]],
    "core": ["A neutron has no charge", "中子不带电"],
    "final": [["中子", "s"], ["不带电", "v"], ["。", ""]],
    "tip": "中子不带电，和质子一起组成原子核。",
},

"electron": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["An electron", "电子", "s"], ["has", "带", "v"], ["negative charge", "负电", "h"]],
    "core": ["An electron has negative charge", "电子带负电"],
    "final": [["电子", "s"], ["带", "v"], ["负电", "h"], ["。", ""]],
    "tip": "电子带负电，围绕原子核运动。",
},

"isotope": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["Isotopes", "同位素", "s"], ["have", "有", "v"], ["the same proton number", "相同的质子数", "h"]],
    "core": ["Isotopes have the same proton number", "同位素质子数相同"],
    "final": [["同位素", "s"], ["质子数", "s"], ["相同", "v"], ["。", ""]],
    "tip": "同位素：质子数相同、中子数不同 → 化学性质相同。",
},

"radioactive decay": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["Radioactive decay", "放射性衰变", "s"], ["is", "具有", "v"], ["random and spontaneous", "随机性和自发性", "h"]],
    "core": ["Radioactive decay is random and spontaneous", "放射性衰变是随机自发的"],
    "final": [["放射性衰变", "s"], ["具有", "v"], ["随机性和自发性", "h"], ["。", ""]],
    "tip": "衰变随机（无法预测何时发生）、自发（不受外界影响）。",
},

"alpha particle": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["Alpha particles", "α粒子", "s"], ["are", "具有", "v"], ["strongly ionising", "很强的电离能力", "h"]],
    "core": ["Alpha particles are strongly ionising", "α粒子电离能力强"],
    "final": [["α粒子", "s"], ["电离能力强", "v"], ["。", ""]],
    "tip": "α粒子电离强、穿透弱（一张纸就能挡）。",
},

"beta particle": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["Beta particles", "β粒子", "s"], ["are", "具有", "v"], ["moderately penetrating", "中等的穿透能力", "h"]],
    "core": ["Beta particles are moderately penetrating", "β粒子穿透能力中等"],
    "final": [["β粒子", "s"], ["穿透能力中等", "v"], ["。", ""]],
    "tip": "β粒子穿透中等（几毫米铝板）。",
},

"gamma radiation": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["Gamma radiation", "γ射线", "s"], ["is", "具有", "v"], ["highly penetrating", "很强的穿透能力", "h"]],
    "core": ["Gamma radiation is highly penetrating", "γ射线穿透能力强"],
    "final": [["γ射线", "s"], ["穿透能力强", "v"], ["。", ""]],
    "tip": "γ射线穿透最强（厚铅板），电离最弱。",
},

"half-life": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["Half-life", "半衰期", "s"], ["is", "是", "v"], ["the time for activity to halve", "活度减半所需的时间", "h"]],
    "core": ["Half-life is the time for activity to halve", "半衰期是活度减半所需的时间"],
    "final": [["半衰期", "s"], ["是", "v"], ["活度减半所需时间", "h"], ["。", ""]],
    "tip": "半衰期 = 放射性活度减到一半所需的时间。",
},

"planet": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["Earth", "地球", "s"], ["is", "是", "v"], ["a planet", "一颗行星", "h"]],
    "core": ["Earth is a planet", "地球是一颗行星"],
    "final": [["地球", "s"], ["是", "v"], ["一颗行星", "h"], ["。", ""]],
    "tip": "行星绕恒星运行、本身不发光；地球是行星，太阳是恒星。",
},

"orbit": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["Planets", "行星", "s"], ["orbit", "绕……运行", "v"], ["the Sun", "太阳", "h"]],
    "core": ["Planets orbit the Sun", "行星绕太阳运行"],
    "final": [["行星", "s"], ["绕太阳", "a"], ["运行", "v"], ["。", ""]],
    "tip": "orbit 作动词 = 绕行，作名词 = 轨道。",
},

"gravitational field": {
    "pat": "判断句：主语 + 谓语 + 宾语 + 介词短语",
    "flow": [["The Sun's gravitational field", "太阳的重力场", "s"], ["keeps", "使保持", "v"], ["planets", "行星", "h"],
             ["in orbit", "在轨道上", "a"]],
    "core": ["The Sun's gravitational field keeps planets in orbit", "太阳重力场使行星保持在轨道上"],
    "final": [["太阳重力场", "s"], ["使", "v"], ["行星", "h"], ["保持轨道运动", "v"], ["。", ""]],
    "tip": "keep…in orbit = 使…保持在轨道上；引力提供向心力。",
},

"star": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["The Sun", "太阳", "s"], ["is", "是", "v"], ["a star", "一颗恒星", "h"]],
    "core": ["The Sun is a star", "太阳是一颗恒星"],
    "final": [["太阳", "s"], ["是", "v"], ["一颗恒星", "h"], ["。", ""]],
    "tip": "恒星自身发光；太阳是离我们最近的恒星。",
},

"galaxy": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["The Milky Way", "银河系", "s"], ["is", "是", "v"], ["a galaxy", "一个星系", "h"]],
    "core": ["The Milky Way is a galaxy", "银河系是一个星系"],
    "final": [["银河系", "s"], ["是", "v"], ["一个星系", "h"], ["。", ""]],
    "tip": "星系由大量恒星等组成；我们住在银河系。",
},

"light-year": {
    "pat": "判断句：主语 + be + 表语",
    "flow": [["A light-year", "光年", "s"], ["is", "是", "v"], ["a unit of distance", "距离单位", "h"]],
    "core": ["A light-year is a unit of distance", "光年是距离单位"],
    "final": [["光年", "s"], ["是", "v"], ["距离单位", "h"], ["。", ""]],
    "tip": "光年是长度单位（光走一年的距离），不是时间单位。",
},

# ========== 十一、实验技能 ==========

"independent variable": {
    "pat": "祈使句：动词 + 宾语",
    "flow": [["Change", "改变", "v"], ["the independent variable", "自变量", "h"]],
    "core": ["Change the independent variable", "改变自变量"],
    "final": [["改变", "v"], ["自变量", "h"], ["。", ""]],
    "tip": "自变量是你主动改变的量，只能一次改一个。",
},

"dependent variable": {
    "pat": "祈使句：动词 + 宾语",
    "flow": [["Measure", "测量", "v"], ["the dependent variable", "因变量", "h"]],
    "core": ["Measure the dependent variable", "测量因变量"],
    "final": [["测量", "v"], ["因变量", "h"], ["。", ""]],
    "tip": "因变量是被测量、随自变量变化的量。",
},

"control variable": {
    "pat": "祈使句：动词 + 宾语 + 补语",
    "flow": [["Keep", "保持", "v"], ["control variables", "控制变量", "h"], ["constant", "不变", "c"]],
    "core": ["Keep control variables constant", "保持控制变量不变"],
    "final": [["保持", "v"], ["控制变量", "h"], ["不变", "c"], ["。", ""]],
    "tip": "控制变量 = 除自变量外保持不变的那些量（公平实验的关键）。",
},

"fair test": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["A fair test", "公平实验", "s"], ["changes", "改变", "v"], ["one main factor", "一个主要因素", "h"]],
    "core": ["A fair test changes one main factor", "公平实验只改变一个主要因素"],
    "final": [["公平实验", "s"], ["只改变", "v"], ["一个主要因素", "h"], ["。", ""]],
    "tip": "公平实验 = 只变一个变量，其余全部不变。",
},

"method": {
    "pat": "祈使句：动词 + 宾语",
    "flow": [["Write", "写出", "v"], ["a clear experimental method", "清晰实验方法", "h"]],
    "core": ["Write a clear experimental method", "写出清晰的实验方法"],
    "final": [["写出", "v"], ["清晰实验方法", "h"], ["。", ""]],
    "tip": "实验方法要写清步骤，让别人能照着重复。",
},

"apparatus": {
    "pat": "祈使句：动词 + 宾语 + 后置定语",
    "flow": [["List", "列出", "v"], ["the apparatus needed", "所需仪器", "h"]],
    "core": ["List the apparatus needed", "列出所需仪器"],
    "final": [["列出", "v"], ["所需仪器", "h"], ["。", ""]],
    "tip": "needed 是后置分词定语，中文提前说「所需的」。",
},

"observation": {
    "pat": "祈使句：动词 + 宾语",
    "flow": [["Record", "记录", "v"], ["each observation", "每个观察结果", "h"]],
    "core": ["Record each observation", "记录每个观察结果"],
    "final": [["记录", "v"], ["每个观察结果", "h"], ["。", ""]],
    "tip": "observation 在这句是「观察结果」而不是「观察」。",
},

"result": {
    "pat": "祈使句：动词 + 宾语 + in 介词短语",
    "flow": [["Enter", "填入", "v"], ["the result", "结果", "h"], ["in a table", "表格中", "a"]],
    "core": ["Enter the result in a table", "把结果填入表格"],
    "final": [["把结果", "h"], ["填入", "v"], ["表格", "h"], ["。", ""]],
    "tip": "enter…in a table = 把…填进表格；中文用「把」字句。",
},

"conclusion": {
    "pat": "判断句：主语 + 情态 + 谓语 + 宾语",
    "flow": [["The conclusion", "结论", "s"], ["must use", "必须使用", "v"], ["the evidence", "证据", "h"]],
    "core": ["The conclusion must use the evidence", "结论必须使用证据"],
    "final": [["结论", "s"], ["必须使用", "v"], ["证据", "h"], ["。", ""]],
    "tip": "结论要从数据（证据）推出，不能凭想象。",
},

"evidence": {
    "pat": "祈使句：动词 + 宾语 + as 介词短语",
    "flow": [["Use", "使用", "v"], ["data", "数据", "h"], ["as evidence", "作为证据", "a"]],
    "core": ["Use data as evidence", "用数据作证据"],
    "final": [["使用", "v"], ["数据", "h"], ["作为证据", "a"], ["。", ""]],
    "tip": "use…as… = 把…用作…；数据就是证据。",
},

"risk": {
    "pat": "祈使句：动词 + 宾语 + and 并列",
    "flow": [["State", "写出", "v"], ["the risk", "风险", "h"], ["and how to reduce it", "及降低风险的方法", "h"]],
    "core": ["State the risk and how to reduce it", "写出风险及降低方法"],
    "final": [["写出", "v"], ["风险", "h"], ["及降低风险的方法", "h"], ["。", ""]],
    "tip": "风险题要答两件事：风险是什么 + 怎么降低。",
},

"safety precaution": {
    "pat": "祈使句：动词 + 宾语 + as 介词短语",
    "flow": [["Wear", "佩戴", "v"], ["goggles", "护目镜", "h"], ["as a safety precaution", "作为安全措施", "a"]],
    "core": ["Wear goggles as a safety precaution", "戴护目镜作为安全措施"],
    "final": [["佩戴", "v"], ["护目镜", "h"], ["作为安全措施", "a"], ["。", ""]],
    "tip": "safety precaution = 安全措施；戴护目镜就是典型安全措施。",
},

"valid": {
    "pat": "判断句：主语 + 谓语 + 宾语",
    "flow": [["A valid test", "有效实验", "s"], ["answers", "回答", "v"], ["the stated question", "所提出的问题", "h"]],
    "core": ["A valid test answers the stated question", "有效实验回答所提出的问题"],
    "final": [["有效实验", "s"], ["能回答", "v"], ["所提出的问题", "h"], ["。", ""]],
    "tip": "valid = 能真正回答研究问题的实验设计。",
},

"range": {
    "pat": "祈使句：动词 + 宾语",
    "flow": [["Use", "使用", "v"], ["a wide range of values", "较宽的数据范围", "h"]],
    "core": ["Use a wide range of values", "使用较宽的取值范围"],
    "final": [["使用", "v"], ["较宽的数据范围", "h"], ["。", ""]],
    "tip": "取值范围宽、数据点多，结论趋势更可靠。",
},

"interval": {
    "pat": "祈使句：动词 + 宾语",
    "flow": [["Use", "使用", "v"], ["equal intervals", "相等间隔", "h"]],
    "core": ["Use equal intervals", "使用相等间隔"],
    "final": [["使用", "v"], ["相等间隔", "h"], ["。", ""]],
    "tip": "读数间隔取相等（如每 10℃ 记一次），作图更方便。",
},

}
