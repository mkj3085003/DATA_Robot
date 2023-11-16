#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#enconding = utf8
import sys
import time
import grpc

sys.path.append('./')
sys.path.append('../')

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

import GrabSim_pb2_grpc
import GrabSim_pb2

channel = grpc.insecure_channel('localhost:30001',options = [
            ('grpc.max_send_message_length', 1024*1024*1024),
            ('grpc.max_receive_message_length', 1024*1024*1024)
        ])

sim_client = GrabSim_pb2_grpc.GrabSimStub(channel)

'''
初始化，卸载已经加载的关卡，清除所有机器人
'''
def Init():
    sim_client.Init(GrabSim_pb2.NUL())

'''
获取当前可加载的地图信息(地图名字、地图尺寸)
'''
def AcquireAvailableMaps():
    AvailableMaps = sim_client.AcquireAvailableMaps(GrabSim_pb2.NUL())
    print(AvailableMaps)

'''
1、根据mapID加载指定地图
2、如果scene_num>1,则根据地图尺寸偏移后加载多个相同地图
3、这样就可以在一个关卡中训练多个地图
'''
def SetWorld(map_id = 0, scene_num = 1):
    print('------------------SetWorld----------------------')
    world = sim_client.SetWorld(GrabSim_pb2.BatchMap(count = scene_num, mapID = map_id))

'''
返回场景的状态信息
1、返回机器人的位置和旋转
2、返回各个关节的名字和旋转
3、返回场景中标记的物品信息(名字、类型、位置、旋转)
4、返回场景中行人的信息(名字、位置、旋转、速度)
5、返回机器人手指和双臂的碰撞信息
'''
def Observe(scene_id=0):
    print('------------------show_env_info----------------------')
    scene = sim_client.Observe(GrabSim_pb2.SceneID(value=scene_id))
    print(
        f"location:{[scene.location]}, rotation:{scene.rotation}\n",
        f"joints number:{len(scene.joints)}, fingers number:{len(scene.fingers)}\n", 
        f"objects number: {len(scene.objects)}, walkers number: {len(scene.walkers)}\n"
        f"timestep:{scene.timestep}, timestamp:{scene.timestamp}\n"
        f"collision:{scene.collision}, info:{scene.info}")

'''
重置场景
1、重置桌子的宽度和高度
2、清除生成的行人和物品
3、重置关节角度、位置旋转
4、清除碰撞信息
5、重置场景中标记的物品
'''
def Reset(scene_id = 0):
    print('------------------Reset----------------------')
    scene = sim_client.Reset(GrabSim_pb2.ResetParams(scene = scene_id))
    print(scene)

    # 如果场景支持调整桌子
    # sim_client.Reset(GrabSim_pb2.ResetParams(scene = scene_id, adjust = True, height = 100.0, width = 100.0))"
'''
根据传入的部位名字，获取相机数据
'''
def get_camera(part, scene_id = 0):
    print('------------------get_camera----------------------')
    action = GrabSim_pb2.CameraList(cameras = part, scene = scene_id)
   
    return sim_client.Capture(action)

'''
显示相机画面
'''
def show_image(img_data):
    print('------------------show_image----------------------')
    im = img_data.images[0]
    d = np.frombuffer(im.data, dtype = im.dtype).reshape((im.height, im.width, im.channels))
    print(img_data.info)
    plt.imshow(d, cmap = "gray" if "depth" in im.name.lower() else None)
    plt.show()
if __name__ == '__main__':
    map_id = 11     # 地图编号
    scene_num = 1   # 场景数量
    
    print('------------ 初始化加载场景 ------------')
    Init()
    AcquireAvailableMaps()
    SetWorld(map_id, scene_num)
    time.sleep(5.0)

    for i in range(scene_num):
        print('------------ 场景操作 ------------')
        Observe(i)
        Reset(i)
        for camera_name in [ GrabSim_pb2.CameraName.Head_Segment]:
            img_data = get_camera([camera_name], i)
            show_image(img_data)
