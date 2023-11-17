import time
import cv2
import numpy as np

from DATA_Robot.VLM_container.InquireTempNeeds import InquireTempNeeds
from DATA_Robot.utils.NavigationController import NavigationController
from DATA_Robot.utils.RobotTaskController import RobotTaskController
from DATA_Robot.utils.SceneManager import SceneManager
from DATA_Robot.utils.JointController import JointController
from DATA_Robot.VLM_container.conditioner import Conditioner

'''场景：机器人调节空调温度'''

'''
1. 场景生成
'''
# Create an instance of the SceneManager class
scene_manager = SceneManager()
map_id = 11  # 地图编号
scene_num = 1  # 场景数量
print('------------ 初始化加载场景 ------------')
scene_manager.Init()
scene_manager.AcquireAvailableMaps()
scene_manager.SetWorld(map_id, scene_num)
time.sleep(5.0)
print('------------ 场景操作 ------------')
# scene_manager.Reset(0)
scene = scene_manager.Observe(0)

'''
2. 关闭窗帘，开筒灯，开大厅灯
'''
task = RobotTaskController(scene_manager)
# task.close_curtains()
# time.sleep(2)  # 延时2秒
# task.turn_on_tube_light()
# time.sleep(2)  # 延时2秒
# task.turn_on_hall_light()
# time.sleep(2)  # 延时2秒

'''
3. 移动到空调附近
'''
nav = NavigationController(scene_manager)
#250
nav.navigate_to_limit(248.0, -148.0, 0, 100, 0)

'''
4. 打开空调
'''
conditioner = Conditioner(scene_manager)
conditioner.turn_on_container()

'''
4. 调整温度
'''
# while True:
#     key = input(
#         "Robot:Is the room temperature suitable? Does it need to be adjusted? Does it need to be adjusted higher or "
#         "lower?\n option:no、higher、lower、set").lower().strip()
#     if key == "no":
#         print("OK!")
#         pass
#     elif key == "higher":
#         temp = input("Robot: How many degrees higher would you like to set the temperature? Please enter a number: ").lower().strip()
#         conditioner.Turn_up_temperature(int(temp))
#         continue
#     elif key == "lower":
#         temp = input( "Robot: How many degrees lower would you like to set the temperature? Please enter a number: ").lower().strip()
#         conditioner.Turn_down_temperature(int(temp))
#         continue
#     elif key == "set":
#         temp = input("Robot: What temperature would you like to set? Please enter a number: ").lower().strip()
#         conditioner.set_temperature(int(temp))

inquire = InquireTempNeeds()
print("robot:Robot:Is the room temperature suitable? Does it need to be adjusted? Does it need to be adjusted higher "
      "or lower?")

inquire.chat(0)
need = inquire.get_json()
print(need)

if need["option"]== "no":
    print("OK!")
    pass
elif need["option"] == "higher":
    conditioner.Turn_up_temperature(need["temp"])
elif need["option"]== "lower":
    conditioner.Turn_down_temperature(need["temp"])
elif need["option"] == "set":
    conditioner.set_temperature(need["temp"])
