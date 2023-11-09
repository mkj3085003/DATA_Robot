import numpy as np
import math
import json
CHAIR_LIST=[]
# TO DO:获取Starbucks里所有座椅的类型坐标以及对应的位置及特征存储在find_chair\model\data_chair.json，
# 补充完CHAIR_LIST的值
with open("..\data\data_chair.json", 'r') as json_file:
    json_str = json_file.read()
    CHAIR_LIST = json.loads(json_str)
# 打开JSON文件并加载数据

CHAIR_NUM=30
#LLM使用模型对输入进行文本匹配
# 再使用一个hamming distance进行最佳座位匹配
FEATURE_DESCRIPTION={
    #总共7位二进制编码
    #location
   "dont mind":"00", 
   "Near the window":"01", 
   "near the bar":"10",
    #share
   "dont mind sharing a table":"0", 
   "alone":"1",
    #height
   "dont mind":"00",
   "high":"01", #高度这里空了一个11码……导致了有2^5个空值……但便于比较
   "low":"10",
   #metiral
   "dont mind":"00",
   "hard":"01", 
   "soft":"10"

}


class ChairList:
    def __init__(self):
        self.order_data
        self.empty_seat=[seat for seat in CHAIR_LIST if not seat['sitted']]#完全没有人坐
        self.empty_chair=[chair for chair in CHAIR_LIST if  not chair['Capacity']]#有空位
                

    def encode_feature(self,order_data):
        self.num=int(order_data['Capacity'])
        self.order_data=order_data
        self.encode_feature=\
            FEATURE_DESCRIPTION[order_data["Location"]]+\
            FEATURE_DESCRIPTION[order_data["Share"]]+ \
            FEATURE_DESCRIPTION[order_data["Height"]]+\
            FEATURE_DESCRIPTION[order_data["Material"]]
        return self.encode_feature
    
    def get_chair_by_id(self, chair_id):
        for chair in self.chairs:
            if chair["id"] == chair_id:
                return chair
        return None

    def get_position(self, chair_id):
        chair = self.get_chair_by_id(chair_id)
        return chair['position'] 
    
    def get_empty_seat(self):
        return self.empty_seat
    
    def match_best_chair(self,empty_chairs):
        for chair in empty_chairs:
            if chair['Capacity']>= self.num:
                dis=self.hamming_distance(chair['feature'],self.order_feature)
                # 如果不介意，dontmind编码距离减去1
                if FEATURE_DESCRIPTION[self.order_data["Location"]]=="00":dis-1
                if FEATURE_DESCRIPTION[self.order_data["Share"]]=="0":dis-1
                if FEATURE_DESCRIPTION[self.order_data["Height"]]=="00":dis-1
                if FEATURE_DESCRIPTION[self.order_data["Material"]]=="00":dis-1

                if dis < min_distance:
                    min_distance = dis
                    self.best_chair = chair
        return self.best_chair
    
    def hamming_distance(str1, str2):
        assert len(str1) == len(str2), "Input strings must have the same length."
        return sum(bit1 != bit2 for bit1, bit2 in zip(str1, str2))   
    
    def find_the_best(self):
        min_distance=7 #7位全不一样
        best_chairs=[] #取海明距离最小的座位
        if self.order_data["Share"]=="alone":
            best_empty=self.match_best_chair(self.empty_seat)
            best_chair.append[best_empty]
        else :
            best_chair=self.match_best_chair(self.empty_chair)
            if best_empty['id'] != best_chair['id']:
                best_chairs.append[best_chair] 
                #把非要alone和有其他需求的进行比较，一起加入best_chairs
        return best_chairs
    
    # TO DO：需要更新分配后座位容量和座位是否有人
    def updata_empty_chair_list(self,sitted_seat):
        # 'Capacity' -ord_data['Capacity']
        self.empty_chair
        # sitted = true
        self.empty_seat