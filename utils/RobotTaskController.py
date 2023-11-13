import time
import GrabSim_pb2
from utils.SceneManager import SceneManager
from utils.NavigationController import NavigationController

# For prerequisites running the following sample, visit https://help.aliyun.com/document_detail/611472.html
from http import HTTPStatus
import dashscope

def simple_sample():
    # specify llama model.
    response = dashscope.Generation.call(model='llama2-7b-chat-v2',
                                         prompt='Hey, are you conscious? Can you talk to me?')
    if response.status_code == HTTPStatus.OK:
        print('Result is: %s' % response.output)
    else:
        print('Failed request_id: %s, status_code: %s, code: %s, message:%s' %
              (response.request_id, response.status_code, response.code,
               response.message))

def call_with_messages(user_text):
    messages = [
        {'role': 'user', 'content': user_text}]
    response = dashscope.Generation.call(
        'qwen-14b-chat',
        messages=messages,
        result_format='message',  # set the result is message format.
    )
    if response.status_code == HTTPStatus.OK:
        # return response
        print(response)
        # print("成功")
        return response
    else:
        print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))
        print("不成功")




class RobotTaskController:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager

    def control_robot_action(self, task_type, action_step, message="",scene_id=0):
        # 调用本地python仿真器对象的ControlRobot方法，控制机器人执行特定任务步骤
        scene = self.scene_manager.sim_client.ControlRobot(GrabSim_pb2.ControlInfo(scene=scene_id, type=task_type, action=action_step, content=message))
        return scene.info == "action success"

    def display_text_bubble(self, text,scene_id=0):
        # 显示文字冒泡
        self.control_robot_action(0, 1, text,scene_id)
    def make_coffee(self,scene_id=0):
        self.control_robot_action(0, 1, "开始制作咖啡",scene_id)
        result = self.control_robot_action(1, 1,"",scene_id)

        if result:
            self.control_robot_action(1, 2,"",scene_id)
            self.control_robot_action(1, 3,"",scene_id)
            self.control_robot_action(1, 4,"",scene_id)
        else:
            self.control_robot_action(0, 1, "制作咖啡失败",scene_id)

    def pour_water(self,scene_id=0):
        self.control_robot_action(0, 1, "开始倒水",scene_id)
        result = self.control_robot_action(2, 1,"",scene_id)

        if result:
            self.control_robot_action(2, 2,"",scene_id)
            self.control_robot_action(2, 3,"",scene_id)
            self.control_robot_action(2, 4,"",scene_id)
            self.control_robot_action(2, 5,"",scene_id)
        else:
            self.control_robot_action(0, 1, "","倒水失败")

    def grab_snack(self,scene_id=0):
        self.control_robot_action(0, 1, "开始夹点心",scene_id)
        result = self.control_robot_action(3, 1,"",scene_id)

        if result:
            self.control_robot_action(3, 2,"",scene_id)
            self.control_robot_action(3, 3,"",scene_id)
            self.control_robot_action(3, 4,"",scene_id)
            self.control_robot_action(3, 5,"",scene_id)
            self.control_robot_action(3, 6,"",scene_id)
            self.control_robot_action(3, 7,"",scene_id)
        else:
            self.control_robot_action(0, 1, "夹点心失败",scene_id)

    def mop_floor(self,scene_id=0):
        self.control_robot_action(0, 1, "开始拖地",scene_id)
        result = self.control_robot_action(4, 1,"",scene_id)

        if result:
            self.control_robot_action(4, 2,"",scene_id)
            self.control_robot_action(4, 3,"",scene_id)
            self.control_robot_action(4, 4,"",scene_id)
        else:
            self.control_robot_action(0, 1, "拖地失败",scene_id)

    def wipe_table(self,scene_id=0):
        self.control_robot_action(0, 1, "开始擦桌子",scene_id)
        result = self.control_robot_action(5, 1,"",scene_id)

        if result:
            self.control_robot_action(5, 2,"",scene_id)
            self.control_robot_action(5, 3,"",scene_id)
        else:
            self.control_robot_action(0, 1, "擦桌子失败",scene_id)

if __name__ == '__main__':


    scene_manager = SceneManager()
    map_id = 3  # Map ID: 3 for the coffee shop
    scene_num = 1  # Number of scenes to load
    scene_manager.load_scene(map_id, scene_num)
    time.sleep(5)

    for i in range(scene_num):
        print(f"------------------ Scene {i} ----------------------")
        scene_manager.reset_scene(i)
        scene_info = scene_manager.get_scene_info(i)
        print(scene_info)  # You can access various scene information from the 'scene_info' object

    scene_id = 0  # 选择场景ID
    task_controller = RobotTaskController(scene_manager)

    dashscope.api_key = 'sk-7e8e9830a5b94c908a00e2521f56188b'

    while(1):
        user_text = input("'role': 'user', 'content':'")
        response = call_with_messages(user_text)
        response_text = response.output.choices[0]['message']['content']
        print("'role': 'robot', 'content':'", response_text)
        task_controller.display_text_bubble(response_text)
        time.sleep(2)  # 延时2秒

    # # 依次执行不同的任务
    # navigator = NavigationController(scene_manager)
    # scene = scene_manager.sim_client.Observe(GrabSim_pb2.SceneID(value=0))
    # # 获取机器人当前位置坐标（x,y,z）
    # ginger_loc = [scene.location.X, scene.location.Y, scene.location.Z]
    # navigator.navigate_to_limit(ginger_loc[0],  ginger_loc[1]-200, 90, 200, 100)
    # task_controller.make_coffee()
    # time.sleep(2)  # 延时2秒
    # task_controller.pour_water()
    # time.sleep(2)
    # task_controller.grab_snack()
    # time.sleep(2)
    # task_controller.mop_floor()
    # time.sleep(2)
    # task_controller.wipe_table()
