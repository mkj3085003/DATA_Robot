import time
import sys
sys.path.append('../')
import utils
from utils.SceneManager import SceneManager
scene_manager = SceneManager()
map_id = 11    # 地图编号
scene_num = 1  # 场景数量

print('------------ 初始化加载场景 ------------')
scene_manager.Init()
scene_manager.AcquireAvailableMaps()
scene_manager.SetWorld(map_id, scene_num)
time.sleep(5.0)


import utils
from utils.JointController import JointController
from utils.NavigationController import NavigationController
from utils.CameraController import CameraController
import GrabSim_pb2
import cv2
import numpy as np
from sobel_number_detect import ReadNumber
joint = JointController(scene_manager)
nav =NavigationController(scene_manager)
nav_threshhold = 3
class Conditioner():
        def __init__(self) -> None:
                self.work_state=False
                self.temperature = 25
                #减、加、开关
                self.key=[(300.50,-137.499,111.0),(300.50,-139.999,111.0),(300.50,-142.4999,111.0)]
                self.delta_collision = 0.01

        def get_temp_vision(self):
                camera = CameraController(scene_manager)
                cam_data = camera.capture_image(GrabSim_pb2.CameraName.Chest_Color)
                # camera.show_image(cam_data)

                img_data=cam_data.images[0]
                np_img = np.frombuffer(img_data.data, dtype=img_data.dtype).reshape((img_data.height, img_data.width, img_data.channels))
                """cv数字识别"""
                numreader = ReadNumber()
                numreader.get_template()
                bin=numreader.preprocess_image(np_img)
                cv2.imwrite("C:\\Users\\12245\\Documents\\Unreal Projects\\HarixSim2\\python\\DATA_Robot\\VLM_container\\bina.png",bin)
                if numreader.detect_digits():
                        self.temperature=numreader.detect_digits()
                
                
        def press_buttom(self,key_id):
                #按上开关
                print(f"按下按键{key_id}开始")
                joint.reset_joints()
                x,y,z = self.key[key_id]
                time.sleep(5.0)
                #按下
                if key_id == 0:
                        joint.ik_control_right_hand(x,y,z+self.delta_collision)
                else:
                        joint.ik_control_left_hand(x,y,z+self.delta_collision)

                time.sleep(5.0)
                #收回手臂防止二次触碰
                if key_id == 2:
                        joint.reset_joints()
                        time.sleep(5.0)
                elif key_id ==1:
                       joint.reset_joints()
                #        joint.ik_control_left_hand(\
                        # x,y,z-5*self.delta_collision)
                       time.sleep(5.0)
                else:
                        joint.reset_joints()
                        # joint.ik_control_right_hand(\
                        # x,y,z-5*self.delta_collision)
                        time.sleep(5.0)
                print(f"按下按键{key_id}结束")
                return True

        def turn_on_container(self):
                #按上开关 
                if self.work_state == False:
                        if self.press_buttom(2):
                                self.work_state = True
                        self.get_temp_vision()
                        print(f"空调为关闭状态，现打开空调,温度为{self.temperature}℃")
                else : print("空调已经为开启状态")
                return True

        def turn_off_container(self):
                #按上开关 
                if self.work_state == True:
                        if self.press_buttom(2):
                                self.work_state = True
                        print("空调为打开状态，现已关闭")
                else : print("空调已经为关闭状态")
                return True

        def Turn_up_temperature(self,temp=1):
                #调高温度
                print("调高温度开始执行")
                for i in range(temp):
                        self.turn_on_container()
                        self.press_buttom(1)
                print(f"调高温度{temp}℃")
                self.temperature += temp
                self.get_temp_vision()
                return True
                #可以加视觉数字检测判断温度

        def Turn_dwon_temperature(self,temp=1):
                #降低温度
                print("降低温度开始执行")
                for i in range(temp):
                        self.turn_on_container()
                        self.press_buttom(0)
                print(f"降低温度{temp}℃")
                self.temperature -= temp
                self.get_temp_vision()
                return True
                #可以加视觉数字检测判断温度

        def set_temperature(self,temp):
                if temp<self.temperature:
                        print("----I think temperature now is",self.temperature)
                        while self.temperature!=temp:
                                #通过视觉反馈调整
                                # delta=self.get_temp_vision()-temp
                                delta=self.temperature-temp
                                self.Turn_dwon_temperature(delta)
                                # self.temperature=self.get_temp_vision()
                                # print("I see temp is",self.get_temp_vision())
                elif temp>self.temperature:
                        print("----I think temperature now is",self.temperature)
                        while self.temperature!=temp:
                                # delta=temp-self.get_temp_vision()
                                delta=temp-self.temperature
                                self.Turn_up_temperature(delta)
                                # self.temperature=self.get_temp_vision()
                                # print("I see temp is",self.get_temp_vision())
                # else:print(f"alrady in {self.get_temp_vision()} ℃")
                      

import utils
from utils.RobotTaskController import RobotTaskController
from utils.NavigationController import NavigationController
task= RobotTaskController(scene_manager)
# task.close_curtains()
time.sleep(5)  # 延时2秒
# task.turn_on_tube_light()

# 定义开关位置减少，增加，打开
key=[(300.50,-137.499,111.0),(300.50,-139.999,111.0),(300.50,-142.4999,111.0)]
key_id = [4,4]

#获取开关按键
def input():
    key=input("Is the room temperature suitable? Does it need to be adjusted? Does it need to be adjusted higher or lower?\n option:no、higher、lower").lower().strip()
    if key=="no":
        pass 
    elif key=="higher":
        id = [2,1]
        return id
    elif key=="lower":
        id =[2,0]
        return id
    
if __name__ == "__main__"  :
    nav = NavigationController(scene_manager)
    nav_threshhold = 10
    nav.navigate_to_limit(250.0,-148.0,0,-1,0)

    conditioner = Conditioner()
    conditioner.turn_on_container()
#     conditioner.get_temp_vision()
    conditioner.set_temperature(27)
    print("开始设置23度")
    conditioner.set_temperature(23)
    # # time.sleep(5)
    # conditioner.Turn_up_temperature(3)
