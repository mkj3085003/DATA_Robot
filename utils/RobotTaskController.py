import time
import GrabSim_pb2
from .SceneManager import SceneManager
from utils.NavigationController import NavigationController

# # For prerequisites running the following sample, visit https://help.aliyun.com/document_detail/611472.html
# from http import HTTPStatus
# import dashscope
#
# def simple_sample():
#     # specify llama model.
#     response = dashscope.Generation.call(model='llama2-7b-chat-v2',
#                                          prompt='Hey, are you conscious? Can you talk to me?')
#     if response.status_code == HTTPStatus.OK:
#         print('Result is: %s' % response.output)
#     else:
#         print('Failed request_id: %s, status_code: %s, code: %s, message:%s' %
#               (response.request_id, response.status_code, response.code,
#                response.message))
#
# def call_with_messages(user_text):
#     messages = [
#         {'role': 'user', 'content': user_text}]
#     response = dashscope.Generation.call(
#         'qwen-14b-chat',
#         messages=messages,
#         result_format='message',  # set the result is message format.
#     )
#     if response.status_code == HTTPStatus.OK:
#         # return response
#         print(response)
#         # print("成功")
#         return response
#     else:
#         print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
#             response.request_id, response.status_code,
#             response.code, response.message
#         ))
#         print("不成功")




class RobotTaskController:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager

    # 移动到任务可执行区域内
    def move_task_area(self,task_type=0, scene_id=0):
        scene = self.scene_manager.sim_client.Observe(GrabSim_pb2.SceneID(value=scene_id))

        walk_value = [scene.location.X, scene.location.Y, scene.rotation.Yaw]
        print('------------------move_task_area----------------------')
        print("position:", walk_value)

        #做咖啡
        if task_type == 1:
            v_list = [[250.0, 310.0]]
        #倒水
        elif task_type == 2:
            v_list = [[-70.0, 480.0]]
        #夹点心
        elif task_type == 3:
            v_list = [[250.0, 630.0]]
        #拖地
        elif task_type == 4:
            v_list = [[-70.0, 740.0]]
        #擦桌子
        elif task_type == 5:
            v_list = [[260.0, 1120.0]]
        #开关灯
        elif task_type == 6:
            v_list = [[300.0, -220.0]]
        #搬椅子
        elif task_type == 7:
            v_list = [[0.0, -70.0]]
        else:
            v_list = [[0, 0]]

        for walk_v in v_list:
            walk_v = walk_v + [scene.rotation.Yaw, 60, 0]
            print("walk_v:", walk_v)
            action = GrabSim_pb2.Action(scene=scene_id, action=GrabSim_pb2.Action.ActionType.WalkTo, values=walk_v)
            scene = self.scene_manager.sim_client.Do(action)
            print(scene.info)

    def control_robot_action(self, task_type, action_step, message="",scene_id=0):
        # 调用本地python仿真器对象的ControlRobot方法，控制机器人执行特定任务步骤
        scene = self.scene_manager.sim_client.ControlRobot(GrabSim_pb2.ControlInfo(scene=scene_id, type=task_type, action=action_step, content=message))
        if (str(scene.info).find("Action Success") > -1):
            # print(scene.info)
            return True
        else:
            # print(scene.info)
            return False



    #机器人文字冒泡
    def display_text_bubble(self, text,scene_id=0):
        # 显示文字冒泡
        self.control_robot_action(0, 1, text,scene_id)

    #做咖啡
    def make_coffee(self,scene_id=0):
        self.move_task_area(1)
        self.control_robot_action(0, 1, "开始制作咖啡",scene_id)

        result = self.control_robot_action(1, 1,"",scene_id)
        self.control_robot_action(0, 2,"",scene_id)
        if result:
            self.control_robot_action(1, 2,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(1, 3,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(1, 4,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(0, 1, "咖啡制作结束",scene_id)
        else:
            self.control_robot_action(0, 1, "制作咖啡失败",scene_id)

    #倒水
    def pour_water(self,scene_id=0):
        self.move_task_area(2)
        self.control_robot_action(0, 1, "开始倒水",scene_id)
        result = self.control_robot_action(2, 1,"",scene_id)
        self.control_robot_action(0, 2,"",scene_id)
        if result:
            self.control_robot_action(2, 2,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(2, 3,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(2, 4,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(2, 5,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(0, 1, "倒水结束",scene_id)
        else:
            self.control_robot_action(0, 1, "倒水失败",scene_id)

    #夹点心
    def grab_snack(self,scene_id=0):
        self.move_task_area(3)
        self.control_robot_action(0, 1, "开始夹点心",scene_id)
        result = self.control_robot_action(3, 1,"",scene_id)
        self.control_robot_action( 0, 2,"",scene_id)
        if result:
            self.control_robot_action(3, 2,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(3, 3,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(3, 4,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(3, 5,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(3, 6,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(3, 7,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(0, 1, "夹点心结束",scene_id)
        else:
            self.control_robot_action(0, 1, "夹点心失败",scene_id)

    #拖地
    def mop_floor(self,scene_id=0):
        self.move_task_area(4)
        self.control_robot_action(0, 1, "开始拖地",scene_id)
        result = self.control_robot_action(4, 1,"",scene_id)
        self.control_robot_action(0, 2)
        if result:
            self.control_robot_action(4, 2,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(4, 3,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(4, 4,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(0, 1, "拖地结束",scene_id)
        else:
            self.control_robot_action(0, 1, "拖地失败",scene_id)

    #擦桌子
    def wipe_table(self,scene_id=0):
        self.move_task_area(5)
        self.control_robot_action(0, 1, "开始擦桌子",scene_id)
        result = self.control_robot_action(5, 1,"",scene_id)
        self.control_robot_action(0, 2)

        if result:
            self.control_robot_action(5, 2,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(5, 3,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(0, 1, "擦桌子结束",scene_id)
        else:
            self.control_robot_action(0, 1, "擦桌子失败",scene_id)

    #关窗帘
    def close_curtains(self,scene_id=0):
        self.control_robot_action(0, 1, "关闭窗帘",scene_id)
        result = self.control_robot_action(8, 1,"",scene_id)
        self.control_robot_action(0, 2,"",scene_id)
        if(result):
            self.control_robot_action(0, 1, "关闭窗帘成功",scene_id)
        else:
            self.control_robot_action(0, 1, "关闭窗帘失败",scene_id)

    #开窗帘
    def open_curtains(self,scene_id=0):
        self.control_robot_action(0, 1, "打开窗帘",scene_id)
        result = self.control_robot_action(8, 2,"",scene_id)
        self.control_robot_action(0, 2,"",scene_id)
        if (result):
            self.control_robot_action(0, 1, "打开窗帘成功",scene_id)
        else:
            self.control_robot_action(0, 1, "打开窗帘失败",scene_id)

    # 开筒灯
    def turn_on_tube_light(self, scene_id=0):
        self.move_task_area(6)
        self.control_robot_action(0, 1, "开筒灯",scene_id)
        result = self.control_robot_action(6, 1,"",scene_id)
        self.control_robot_action(0, 2,"",scene_id)
        if (result):
            self.control_robot_action(0, 1, "开筒灯成功",scene_id)
        else:
            self.control_robot_action(0, 1, "关筒灯失败",scene_id)

    # 关筒灯
    def turn_off_tube_light(self,scene_id=0):
        self.move_task_area(6)
        self.control_robot_action( 0, 1, "关筒灯",scene_id)
        result = self.control_robot_action(6, 2,"",scene_id)
        self.control_robot_action(0, 2,"",scene_id)
        if (result):
            self.control_robot_action(0, 1, "关筒灯成功",scene_id)
        else:
            self.control_robot_action(0, 1, "关筒灯失败",scene_id)




    #开大厅灯
    def turn_on_hall_light(self,scene_id=0):
        self.move_task_area(6)
        self.control_robot_action(0, 1, "开大厅灯",scene_id)
        result = self.control_robot_action( 6, 3,"",scene_id)
        self.control_robot_action(0, 2,"",scene_id)
        if (result):
            self.control_robot_action(0, 1, "开大厅灯成功",scene_id)
        else:
            self.control_robot_action(0, 1, "开大厅灯失败",scene_id)


    # 关大厅灯
    def turn_off_hall_light(self, scene_id=0):
        self.move_task_area(6)
        self.control_robot_action(0, 1, "关大厅灯",scene_id)
        result = self.control_robot_action(6, 4,"",scene_id)
        self.control_robot_action(0, 2,"",scene_id)
        if (result):
            self.control_robot_action(0, 1, "关大厅灯成功",scene_id)
        else:
            self.control_robot_action(0, 1, "关大厅灯失败",scene_id)


    #搬椅子
    def move_chairs(self,scene_id=0):
        self.move_task_area(7)
        self.control_robot_action(0, 1, "开始搬椅子",scene_id)
        result = self.control_robot_action(7, 1,"",scene_id)
        self.control_robot_action(0, 2,"",scene_id)
        if (result):
            self.control_robot_action(7, 2,"",scene_id)
            self.control_robot_action(0, 2,"",scene_id)
            self.control_robot_action(0, 1, "搬椅子结束",scene_id)
        else:
            self.control_robot_action(0, 1, "搬椅子失败",scene_id)

if __name__ == '__main__':

    # Create an instance of the SceneManager class
    scene_manager = SceneManager()

    map_id = 11  # 地图编号

    scene_num = 1  # 场景数量

    print('------------ 初始化加载场景 ------------')
    scene_manager.Init()
    scene_manager.AcquireAvailableMaps()
    scene_manager.SetWorld(map_id, scene_num)
    time.sleep(5.0)

    for i in range(scene_num):
        print('------------ 场景操作 ------------')
        scene_manager.Observe(i)
        scene_manager.Reset(i)

    task_controller = RobotTaskController(scene_manager)

    # dashscope.api_key = 'sk-7e8e9830a5b94c908a00e2521f56188b'
    #
    # while(1):
    #     user_text = input("'role': 'user', 'content':'")
    #     response = call_with_messages(user_text)
    #     response_text = response.output.choices[0]['message']['content']
    #     print("'role': 'robot', 'content':'", response_text)
    #     task_controller.display_text_bubble(response_text)
    #     time.sleep(2)  # 延时2秒

    # 依次执行不同的任务

    task_controller.make_coffee()
    time.sleep(5)  # 延时2秒
    task_controller.pour_water()
    time.sleep(5)
    task_controller.grab_snack()
    time.sleep(5)
    task_controller.mop_floor()
    time.sleep(5)
    task_controller.wipe_table()
    time.sleep(5)
    task_controller.close_curtains()
    time.sleep(5)
    task_controller.open_curtains()
    time.sleep(5)
    task_controller.turn_on_tube_light()
    time.sleep(5)
    task_controller.turn_off_tube_light()
    time.sleep(5)
    task_controller.turn_on_hall_light()
    time.sleep(5)
    task_controller.turn_off_hall_light()
    time.sleep(5)
    task_controller.move_chairs()
    time.sleep(5)



