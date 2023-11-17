import time

from GQA_order.COT_prompting import OrderAgent
from DATA_Robot.utils.NavigationController import NavigationController
from DATA_Robot.utils.RobotTaskController import RobotTaskController
from DATA_Robot.utils.SceneManager import SceneManager
from DATA_Robot.utils.PedestrianController import PedestrianController

'''场景：顾客落座后，机器人询问顾客点餐需求，与顾客完成点餐基本对话'''


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
2. 顾客落座后，咖啡厅服务员找到顾客落座的位置
'''
# 在吧台附近生成行人
pedestrian_controller = PedestrianController(scene_manager)
pedestrian_controller.add_one_pedestrian(walker_id=0, start_x=70, start_y=1074, start_yaw=20, scene_id=0)
walkers = pedestrian_controller.get_walkers()
print(walkers)
time.sleep(2)

# 机器人导航到固定点
navigator = NavigationController(scene_manager)
result_scene = navigator.navigate_to_limit(75.7, 1084, 200, 200, 100)

'''
3. 询问顾客的点餐需求
'''
robot_task_controller = RobotTaskController(scene_manager)
ORDER_LIST = []
order_agent = OrderAgent(menu_path="GQA_order/data_object.json")

# 问好
robot_task_controller.display_text_bubble("It's my pleasure to serve you. What would you like to order? Here is our menu.")
print(f"order bot: It's my pleasure to serve you. What would you like to order? Here is our menu \n{order_agent.menu}")

# 多轮对话
order_agent.chat_with_bubble(temp=0,robot_task_controller=robot_task_controller,pedestrian_controller=pedestrian_controller,customer_name=walkers[0].name)
print(order_agent.get_json())




