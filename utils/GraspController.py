import time
import grpc
import GrabSim_pb2_grpc
import GrabSim_pb2

from utils.SceneManager import SceneManager
from utils.ObjectController import ObjectController
from utils.JointController import JointController


class GraspController:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager

    def grasp_object(self, hand_id, object_id, scene_id=0):
        # 创建抓取行为的Action对象，包括（场景id，行动类型为抓取，值包括手的id和物体的id）
        action = GrabSim_pb2.Action(scene=scene_id, action=GrabSim_pb2.Action.ActionType.Grasp, values=[hand_id, object_id])
        # 调用本地python仿真器对象sim_client的Do方法，向UE端发送抓取行为action
        scene = self.scene_manager.sim_client.Do(action)
        time.sleep(1)  # 等待一段时间以完成抓取动作
        return scene

    def release_object(self, hand_id, scene_id=0):
        # 创建释放行为的Action对象，包括（场景id，行动类型为释放，值包括手的id）
        action = GrabSim_pb2.Action(scene=scene_id, action=GrabSim_pb2.Action.ActionType.Release, values=[hand_id])
        # 调用本地python仿真器对象sim_client的Do方法，向UE端发送释放行为action
        scene = self.scene_manager.sim_client.Do(action)
        time.sleep(1)  # 等待一段时间以完成释放动作
        return scene

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
        # print(scene_info)  # You can access various scene information from the 'scene_info' object

    object_controller = ObjectController(scene_manager)

    scene = scene_manager.sim_client.Observe(GrabSim_pb2.SceneID(value=0))
    # 获取机器人当前位置坐标（x,y,z）
    ginger_loc = [scene.location.X, scene.location.Y, scene.location.Z]
    h=80
    # 创建物品列表
    object_list = [
        GrabSim_pb2.ObjectList.Object(x=ginger_loc[0] - 90, y=ginger_loc[1] + 30, yaw=10, z=h, type=7),
        GrabSim_pb2.ObjectList.Object(x=ginger_loc[0] - 80, y=ginger_loc[1] + 31, z=h, type=5),

        #        #物品3               （物体生成位置横坐标，      物体生成位置横坐标，        物品生成位置高度，物品生成类型4是盒装冰红茶）
        GrabSim_pb2.ObjectList.Object(x=ginger_loc[0] - 33, y=ginger_loc[1] - 10.5, z=h + 20, type=4),
        GrabSim_pb2.ObjectList.Object(x=ginger_loc[0] - 70, y=ginger_loc[1] + 33, z=h, type=9),
        GrabSim_pb2.ObjectList.Object(x=ginger_loc[0] - 60, y=ginger_loc[1] + 34, z=h, type=13)
    ]

    result_scene = object_controller.generate_objects(object_list)  # 生成物品测试
    # print(result_scene)
    # time.sleep(1)
    # object_controller.remove_objects([0, 1])  # 移除物品测试
    # time.sleep(1)
    # object_controller.clean_all_objects()  # 清除场景中所有物品
    # 抓取物品
    joint_controller = JointController(scene_manager)
    joint_values =  [[0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 4.09, -13.15, -11.97, -107.35, 13.08, 8.58, 3.33]]
    joint_controller.rotate_joints(joint_values)  # 关节控制测试
    grasp_controller = GraspController(scene_manager)
    hand_id = 1  # 1表示左手，2表示右手，根据你的需求设置
    object_id_to_grasp = 2  # 要抓取的物品的ID，根据实际情况设置
    grasp_controller.grasp_object(hand_id, object_id_to_grasp)
    #放下物品
    grasp_controller.release_object(hand_id)