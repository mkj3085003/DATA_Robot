import os.path

import numpy as np
import math
import json
from InquireChairNeeds import InquireChairNeeds
from scipy.spatial.distance import hamming
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
        self.CHAIR_LIST = []
        # TO DO:获取Starbucks里所有座椅的类型坐标以及对应的位置及特征存储在find_chair\model\data_chair.json，
        # 补充完CHAIR_LIST的值
        current_path = os.path.dirname(__file__)
        filepath = os.path.abspath(os.path.join(current_path,"..\data\zhuozi.json"))
        with open(filepath, 'r') as json_file:
            json_str = json_file.read()
            self.CHAIR_LIST = json.loads(json_str)
        self.total_empty_chair=list(self.CHAIR_LIST)#完全没有人坐
        self.empty_chair=list(self.CHAIR_LIST)#有空位

    def decode_feature(self, json_str):
        #更改，因为alone会造成一个人时都是alone
        '''FEATURE_DESCRIPTION={
            #总共7位二进制编码
            #location
            "dont mind":"00", 
            "Near the window":"01", 
            "near the bar":"10",
            #share
            "dont mind sharing a table":"0", 
            "dont want to share":"1",
            #height
            "dont mind":"00",
            "high":"01", #高度这里空了一个11码……导致了有2^5个空值……但便于比较
            "low":"10",
            #metiral
            "dont mind":"00",
            "hard":"01", 
            "soft":"10"
            返回none代表不知道有多少人，重新询问
        }'''
        #返回orderdata
        capacity=0
        str=""
        parsed_json = json.loads(json_str)
        try:
            if  "window" in parsed_json['Location'].lower():
                str += "01"
            elif "bar" in parsed_json['Location'].lower():
                str += "10"
            else:
                str += "00"
        except:
            str += "00"

        try:
            if "dont want" in parsed_json['Share'].lower():
                str += "1"
            else:
                str += "0"
        except:
            str += "0"

        try:
            if "high" in parsed_json['Height'].lower():
                str += "01"
            elif "low" in parsed_json['Height'].lower() :
                str += "10"
            else:
                str += "00"
        except:
            str += "00"

        try:
            if "hard" in parsed_json['Material'].lower():
                str += "01"
            elif "soft" in parsed_json['Material'].lower():
                str += "10"
            else:
                str += "00"

        except:
            str += "00"

        try:
            capacity = parsed_json['number_of_people']
        except:
            capacity = 1

        order_data={}
        order_data["Location"]=str[0:2]
        order_data["Share"]=str[2]
        order_data["Height"]=str[3:5]
        order_data["Material"]=str[5:7]
        order_data["Capacity"]=capacity
        order_data["Feature"]=str
        return order_data

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
        return self.total_empty_chair
    
    def match_best_chair(self,empty_chairs, demand_feature):
        min_distance = 10
        for chair in empty_chairs:
            if chair['Capacity']>= demand_feature['Capacity']: #检查大小
                dis=hamming(list(chair['feature']),list(demand_feature["Feature"]))*len(chair['feature'])
                # 如果不介意，dontmind编码距离减去1
                if demand_feature["Location"]=="00":
                    dis-1
                if demand_feature["Share"]=="0":
                    dis-1
                if demand_feature["Height"]=="00":
                    dis-1
                if demand_feature["Material"]=="00":
                    dis-1

                if dis < min_distance:
                    min_distance = dis
                    best_chair = chair
        return best_chair
    
    def hamming_distance(self, str1, str2):
        assert len(str1) == len(str2), "Input strings must have the same length."
        return sum(bit1 != bit2 for bit1, bit2 in zip(str1, str2))
    
    def find_the_best(self,demand_feature_ordered):
        min_distance=7 #7位全不一样
        if demand_feature_ordered["Share"]=="0":
            best_chair=self.match_best_chair(self.total_empty_chair,demand_feature_ordered)

        else :
            best_chair=self.match_best_chair(self.empty_chair,demand_feature_ordered)

         #把非要alone和有其他需求的进行比较，一起加入best_chairs
        return best_chair
    
    # TO DO：需要更新分配后座位容量和座位是否有人
    def update_chair_list(self,seat_id,capacity):
        # 'Capacity' -ord_data['Capacity']
        
    # def update_empty_chair_list(self, sitted_seat):
    #     for seat in sitted_seat:
    #         # 找到分配座位后的椅子
    #         assigned_chair = next((chair for chair in CHAIR_LIST if chair['id'] == seat['id']), None)
    #         if assigned_chair:
    #             # 标记座位已经被占用
    #             assigned_chair['sitted'] = True
    #             # 更新剩余空椅子列表
    #             self.total_empty_chair = [chair for chair in CHAIR_LIST if not chair['sitted']]
        # originalChairData = next((item for item in ChairList if item['id'] == seat_id), None)
        emptyChairData = next((item for item in self.empty_chair if item['id'] == seat_id), None)
        emptyChairData['Capacity'] = emptyChairData['Capacity'] - capacity
        if capacity > emptyChairData['Capacity']:
            raise ValueError("wrong capacity!")
        if emptyChairData['Capacity'] == 0:
            self.empty_chair.remove(emptyChairData)
        totalEmptyChairData = next((item for item in self.total_empty_chair if item['id'] == seat_id), None)
        if totalEmptyChairData != None:
            self.total_empty_chair.remove(totalEmptyChairData)


    #TODO 人走了之后的管理


if __name__ == '__main__':
    talk_walker_response = " I'm here alone.I'd like a seat by the window."
    #执行输出
    inquirer = InquireChairNeeds()  # 初始化对话类

    while True:
        # response = inquirer.initiate_conversation()  # 调用对话函数
        res = inquirer.get_completion(talk_walker_response)#开始匹配
        print(res)
        # 测试
        chair_list = ChairList()
        ordered_feature = chair_list.decode_feature(res)
        if ordered_feature!=None:
            break

    
    print(ordered_feature)
    chair = chair_list.find_the_best(ordered_feature)
    print(chair)
    chair_list.update_chair_list(chair["id"],ordered_feature["Capacity"])
    print(chair_list.empty_chair)