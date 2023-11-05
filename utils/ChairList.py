import numpy as np
import math
CHAIR_NUM=30
CHAIR_LIST={
    {'id':0,
    'position':(11.5,12.7),
    'feature':'0110100', #7位编码的方式，含有对应FEATURE_DESCRIPTION，则该位为1，否则为0
    'sitted':False
    },
    {
    'id':1,
    'position':(22.5,12.7),
    'feature':'010110', #7位编码的方式，含有对应FEATURE_DESCRIPTION，则该位为1，否则为0
    'sitted':False
    }
    #……
}
#LLM使用模型对输入进行编码？or使用一个text特征提取的方式进行匹配
FEATURE_DESCRIPTION=['near the windows','near the bar','high','low','sofa','alone','high capacity']
#TO DO:获取Starbucks里所有座椅的类型坐标以及对应的位置。及特征，补充完CHAIR_LIST的值
def hamming_distance(code1, code2):
    if len(code1) != len(code2):
        raise ValueError("Binary codes must have the same length")
    
    distance = sum(c1 != c2 for c1, c2 in zip(code1, code2))
    return distance

class ChairList:
    def __init__(self):
        self.chairs = []
        self.empty_chairs=[chair for chair in CHAIR_LIST if not chair['sitted']]
    
    def updata_empty_list(self):
        self.empty_chairs=[chair for chair in CHAIR_LIST if not chair['sitted']]  
    
    def get_chair_by_id(self, chair_id):
        for chair in self.chairs:
            if chair["id"] == chair_id:
                return chair
        return None

    def get_position(self, chair_id):
        chair = self.get_chair_by_id(chair_id)
        return chair['position'] 
    
    def get_empty_chairs(self):
        return self.empty_chairs

