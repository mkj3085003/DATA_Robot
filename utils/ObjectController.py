import time
import grpc
import GrabSim_pb2_grpc
import GrabSim_pb2

from DATA_Robot.utils.SceneManager import SceneManager

class ObjectController:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager

    def generate_objects(self, object_list,scene_id=0):
        print('------------------生成物体----------------------')
        # 获取当前场景中所有物体包括机器人的信息
        scene = self.scene_manager.sim_client.Observe(GrabSim_pb2.SceneID(value=scene_id))
        # 调用本地python仿真器对象sim_client的AddObjects方法，向UE端传入物品列表object_list对象
        scene = self.scene_manager.sim_client.AddObjects(GrabSim_pb2.ObjectList(objects=object_list, scene=scene_id))
        print(scene.collision)
        time.sleep(5)
        return scene

    def remove_objects(self, id_list, scene_id=0):
        print('------------------移除物体----------------------')
        # 向UE端传入RemoveList对象，包括要删除的物品列表id_list对象，场景id为scene_id
        scene = self.scene_manager.sim_client.RemoveObjects(GrabSim_pb2.RemoveList(IDs=id_list, scene=scene_id))
        print(f"Removed objects {id_list}. Current objects:")
        time.sleep(1)
        return scene

    def clean_all_objects(self, scene_id=0):
        # 调用本地python仿真器对象sim_client的CleanObjects方法，向UE端传入要删除的场景id
        scene = self.scene_manager.sim_client.CleanObjects(GrabSim_pb2.SceneID(value=scene_id))
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
    time.sleep(1)
    object_controller.remove_objects([0, 1])  # 移除物品测试
    time.sleep(1)
    object_controller.clean_all_objects()  # 清除场景中所有物品
