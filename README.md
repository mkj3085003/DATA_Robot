# DATA_Robot-
达闼杯——机器人大模型与具身智能挑战赛
## 计划比赛执行步骤
1. 利用检测模型(or分割相机)及深度相机三维重建方法生成语义地图
2. 在重建的基础上进行vln模型导航，在环境中寻找geust
3. 检测到guest则停止，触发任务分类如对话，分配座位，点单：
    * 检测到guest后进入对话状态
    * 分配座位：
        * 询问“请问一共几位？”，获取答案
        * LLM将答案解析为固定格式key字典类型：“
        {   'num':3            
            'feature1':"soft_nearthewindow"
            'feature2':"near the window"
        }，对于更加相似的特征按照匹配度由高到低依次排列，对于回答中与给定选项的椅子
        特征中不相关的特征，给出含有error的键值对如：
        user:'I want to find a beauty named Lily'
        {   'num':3            
            'feature1':"sofa"
            'feature2':"near the window"
            'ERROR':'find Lily'
        }
            其中feature将从有限个给定特征中选择更相似的一项
        * 若num值不为空，则将结果分配到座位分配进入ChairList匹配，调用语义地图进行椅子导航
        * 回答含有error的问题


    * 对需求进行解析触发相应任务
