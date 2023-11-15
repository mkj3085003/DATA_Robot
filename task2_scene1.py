import math
import time
import random

from utils.RobotTaskController import RobotTaskController
from utils.SceneManager import SceneManager
from utils.PedestrianController import PedestrianController
from utils.NavigationController import NavigationController

from VLN_find_chair.model.InquireChairNeeds import *
from VLN_find_chair.model.match_best_chair import *



'''场景一：咖啡厅服务员位于吧台处等待，识别顾客靠近，为行人匹配座位'''


def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def check_proximity(pos, obstacles, min_distance=100):  # 假设最小安全距离是100
    for obstacle_pos in obstacles:
        if distance(pos, obstacle_pos) < min_distance:
            return False  # 如果距离太近，返回False
    return True

# 定义一个函数用来检测顾客靠近的操作
def detect_customer_proximity(walkers):

    for walker in walkers:
        robot_x = scene.location.X
        robot_y = scene.location.Y

        detection_range = 200

        walker_x, walker_y = walker.pose.X, walker.pose.Y

        distance = ((walker_x - robot_x) ** 2 + (walker_y - robot_y) ** 2) ** 0.5
        if distance <= detection_range:
            detected_customer = walker.name
            return detected_customer

'''
1. 场景生成
'''
 # Create an instance of the SceneManager class
scene_manager = SceneManager()
map_id = 11    # 地图编号
scene_num = 1  # 场景数量
print('------------ 初始化加载场景 ------------')
scene_manager.Init()
scene_manager.AcquireAvailableMaps()
scene_manager.SetWorld(map_id, scene_num)
time.sleep(5.0)
print('------------ 场景操作 ------------')
scene_manager.Reset(0)
scene=scene_manager.Observe(0)

'''
2. 添加随机行人
'''
pedestrian_min = 3
pedestrian_max = 15
pedestrian_count = random.randint(pedestrian_min,pedestrian_max)
print(pedestrian_count)

#场景坐标的范围
scene_bounds_x = [-700, 700]
scene_bounds_y = [-1400, 1400]

#生成行人坐标
pedestrian_data = []
# #障碍物的位置
# obstacle_positions = []
# for obj in scene.objects:
#     obstacle_positions.append((obj.location.X, obj.location.Y))
# # 与场景中的物体坐标进行判断，生成可以生成行人的位置坐标
# for walker_id in range(pedestrian_count):
#     valid_position = False
#     while not valid_position:
#         start_x = random.uniform(scene_bounds_x[0], scene_bounds_x[1])
#         start_y = random.uniform(scene_bounds_y[0], scene_bounds_y[1])
#         start_yaw = random.uniform(0, 360)
#         if check_proximity((start_x, start_y), obstacle_positions):
#             valid_position = True
#             pedestrian_data.append([walker_id, start_x, start_y, start_yaw])
# print(pedestrian_data)
# 先暂时改成固定点
pedestrian_data = [[0, 0, 880, 0], [1, 250, 1200,45], [2, -55, 750,90], [3, 70, -200,180]]

#添加行人
pedestrian_controller = PedestrianController(scene_manager)
result_scene = pedestrian_controller.add_multiple_pedestrians(pedestrian_data, scene_id=0)

walkers = pedestrian_controller.get_walkers()
print(walkers)

# 生成有walker_id和walker索引的列表
walker_list = [{'walker_id': index, 'walker': walker} for index, walker in enumerate(walkers)]
print(walker_list)

#让所有行人都随便走
for pedestrian_data in walker_list:
    pedestrian_id = pedestrian_data['walker_id']
    auto_control=True
    pedestrian_controller.control_one_pedestrian_autowalk(pedestrian_id, autowalker=auto_control, walker_speed=200, scene_id=0)

# # 创建并启动一个线程来检测顾客靠近机器人
# stop_event = threading.Event()  # Event to stop the thread
# result_queue = queue.Queue()  # Queue to store detected customer name
#
# detection_thread = threading.Thread(target=detect_customer_proximity, args=(scene_manager, result_queue, stop_event))
# detection_thread.start()
'''
3. 某个行人靠近吧台
'''
# 延时5s以后
time.sleep(5)
# 从现有行人中随机选择一个走向吧台
selected_walker = random.choice(walker_list)
walker_id = selected_walker['walker_id']  # 获取选定行人的ID

# 确定吧台的坐标
bar_x = 100
bar_y = 530#在[520-540]范围内
end_yaw = 0

# # 生成其他行人的随机终点位置并让它们走向这些位置
# for pedestrian_data in walker_list:
#     if pedestrian_data['walker_id'] != walker_id:
#         pedestrian_id = pedestrian_data['walker_id']
#         x = random.uniform(scene_bounds_x[0], scene_bounds_x[1])
#         y = random.uniform(scene_bounds_y[0], scene_bounds_y[1])
#         yaw = random.uniform(0, 360)
#         pedestrian_controller.control_one_pedestrian(pedestrian_id, x, y, yaw, walker_speed=200, scene_id=0)
#     else:
#         # 控制选定的行人走向吧台
#         pedestrian_controller.control_one_pedestrian(walker_id, bar_x, bar_y, end_yaw, walker_speed=200, scene_id=0)
pedestrian_controller.control_one_pedestrian_autowalk(walker_id, autowalker=False, walker_speed=200, scene_id=0)
# 控制选定的行人走向吧台
pedestrian_controller.control_one_pedestrian(walker_id, bar_x, bar_y, end_yaw, walker_speed=200, scene_id=0)


'''
4. 识别到顾客靠近，向顾客问好，并询问具体的人数，座位需求
'''
# TODO:调用视觉模型，检测到顾客靠近
#现在的实现方式的话，你可以遍历walker中的每一个，判断是否在机器人附近

# 识别到顾客靠近
while True:
    current_scene = scene_manager.Observe(0)
    detected_customer = detect_customer_proximity(current_scene.walkers)
    if detected_customer:
        print(f"Detected customer : {detected_customer}")
        break
    else:
        print("No customer detected near the robot")
    time.sleep(1)  # 添加一个时间间隔

# 向顾客问好
robot_task_controller = RobotTaskController(scene_manager)
robot_task_controller.display_text_bubble("您好，您需要什么帮助吗？")
time.sleep(2)
talk_walker_response = " I'm here alone.I'd like a seat by the fireplace for a warm and cozy ambiance."
pedestrian_controller.talk_walkers(detected_customer, talk_walker_response)
#执行输出
inquirer = InquireChairNeeds()  # 初始化对话类
response = inquirer.initiate_conversation()  # 调用对话函数
res = inquirer.get_completion_from_messages(talk_walker_response)#开始匹配

chair_list = ChairList()
ordered_feature = chair_list.decode_feature("{\n  \"seat_preference\": \"near window\",\n  \"number_of_people\": 4\n }")
chair = chair_list.find_the_best(ordered_feature)
print(chair)

#带领
navi = NavigationController(scene_manager)
navi.navigate_to(chair["position"][0],chair["position"][1],end_yaw)
#行人走向目标椅子
pedestrian_controller.control_one_pedestrian(walker_id, bar_x, bar_y, end_yaw, walker_speed=200, scene_id=0)




