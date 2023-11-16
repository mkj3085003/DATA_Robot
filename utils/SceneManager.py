import sys
import time
import grpc

import GrabSim_pb2_grpc
import GrabSim_pb2


class SceneManager:

    def __init__(self):
        # Set up the gRPC channel and client
        self.channel = grpc.insecure_channel('localhost:30001', options=[
            ('grpc.max_send_message_length', 1024 * 1024 * 1024),
            ('grpc.max_receive_message_length', 1024 * 1024 * 1024)
        ])
        self.sim_client = GrabSim_pb2_grpc.GrabSimStub(self.channel)

    '''
    初始化，卸载已经加载的关卡，清除所有机器人
    '''

    def Init(self):
        self.sim_client.Init(GrabSim_pb2.NUL())

    '''
    获取当前可加载的地图信息(地图名字、地图尺寸)
    '''

    def AcquireAvailableMaps(self):
        AvailableMaps = self.sim_client.AcquireAvailableMaps(GrabSim_pb2.NUL())
        print(AvailableMaps)

    '''
    1、根据mapID加载指定地图
    2、如果scene_num>1,则根据地图尺寸偏移后加载多个相同地图
    3、这样就可以在一个关卡中训练多个地图
    '''

    def SetWorld(self, map_id=0, scene_num=1):
        print('------------------SetWorld----------------------')
        world = self.sim_client.SetWorld(GrabSim_pb2.BatchMap(count=scene_num, mapID=map_id))
        return world

    '''
    返回场景的状态信息
    1、返回机器人的位置和旋转
    2、返回各个关节的名字和旋转
    3、返回场景中标记的物品信息(名字、类型、位置、旋转)
    4、返回场景中行人的信息(名字、位置、旋转、速度)
    5、返回机器人手指和双臂的碰撞信息
    '''

    def Observe(self, scene_id=0):
        print('------------------show_env_info----------------------')
        scene = self.sim_client.Observe(GrabSim_pb2.SceneID(value=scene_id))
        print(
            f"location:{[scene.location]}, rotation:{scene.rotation}\n",
            f"joints number:{len(scene.joints)}, fingers number:{len(scene.fingers)}\n",
            f"objects number: {len(scene.objects)}, walkers number: {len(scene.walkers)}\n"
            f"timestep:{scene.timestep}, timestamp:{scene.timestamp}\n"
            f"collision:{scene.collision}, info:{scene.info}")
        return scene
    
    def show_env_info(self,scene_id=0):
        scene = self.sim_client.Observe(GrabSim_pb2.SceneID(value=scene_id))
        print('------------------show_env_info----------------------')
        print(
            f"location:{[scene.location.X, scene.location.Y]}, rotation:{scene.rotation.Yaw}\n",
            f"joints number:{len(scene.joints)}, fingers number:{len(scene.fingers)}\n", f"objects number: {len(scene.objects)}\n"
            f"rotation:{scene.rotation}, timestep:{scene.timestep}\n"
            f"timestamp:{scene.timestamp}, collision:{scene.collision}, info:{scene.info}")

    '''
    return robot pose
    (X, Y,Yaw(deg))         
    '''
    def get_pose_XYDeg(self,scene_id=0):
        scene =  self.sim_client.Observe(GrabSim_pb2.SceneID(value=scene_id))
        return scene.location.X,scene.location.Y,(scene.rotation.Yaw)
    '''
    return robot pose 
    (X, Y,Yaw(deg))         
    '''
    def get_pose_XYRad(self,scene_id=0):
        scene =  self.sim_client.Observe(GrabSim_pb2.SceneID(value=scene_id))
        return scene.location.X,scene.location.Y,(scene.rotation.Yaw)*3.1415926/180.0


    '''
    尝试返回坐标
    '''
    def Observe_new(self, scene_id=0):
        print('------------------show_env_info----------------------')

        scene1 = self.sim_client.Observe(GrabSim_pb2.SceneID(value=scene_id))

        for scene_object in scene1.objects:
            print(scene_object)

    '''
    重置场景
    1、重置桌子的宽度和高度（传入adjust_table=true)
    2、清除生成的行人和物品
    3、重置关节角度、位置旋转
    4、清除碰撞信息
    5、重置场景中标记的物品
    '''

    def Reset(self, scene_id=0, adjust=False, height=0, width=0):
        print('------------------Reset----------------------')
        if adjust:
            scene = self.sim_client.Reset(
                GrabSim_pb2.ResetParams(scene=scene_id, adjust=True, height=height, width=width))
        else:
            scene = self.sim_client.Reset(GrabSim_pb2.ResetParams(scene=scene_id))
        print(scene)


if __name__ == '__main__':
    # Create an instance of the SceneManager class
    scene_manager = SceneManager()

    map_id = 11    # 地图编号

    scene_num = 1  # 场景数量

    print('------------ 初始化加载场景 ------------')
    scene_manager.Init()
    scene_manager.AcquireAvailableMaps()
    scene_manager.SetWorld(map_id, scene_num)
    time.sleep(5.0)

    for i in range(scene_num):
        print('------------ 场景操作 ------------')
        scene=scene_manager.Observe(i)
        scene_manager.Observe_new(i)
        #
        # print(scene)
        # scene_manager.Reset(i)




