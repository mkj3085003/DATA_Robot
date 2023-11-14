import time
import os
import torch
import torch.nn as nn
import clip
import matplotlib.pyplot as plt
import numpy as np
from torchvision import transforms
device = "cuda" if torch.cuda.is_available() else "cpu"
ClipModel, transform = clip.load("ViT-B/32", device)
from VLN_find_chair.model.robot_pose_prediction import RobotPosePrediction,preprocess
model=RobotPosePrediction(ClipModel,3)

import sys
sys.path.append("../")
# import utils
from utils import *
import GrabSim_pb2_grpc
import GrabSim_pb2
# Create an instance of the SceneManager class
from utils.SceneManager import SceneManager


if __name__ == '__main__':
    scene_manager = SceneManager()

    map_id = 11    # 地图编号

    scene_num = 1  # 场景数量

    print('------------ 初始化加载场景 ------------')
    scene_manager.Init()
    scene_manager.AcquireAvailableMaps()
    scene_manager.SetWorld(map_id, scene_num)
    time.sleep(5.0)


    camera = CameraController.CameraController(scene_manager)
    navigator= NavigationController.NavigationController(scene_manager)
    agent = scene_manager.Observe(0)

    frame_count=0

    print('------------ 开始导航 ------------')
    while True:
        print('------------new frame ------------')
        walk_value = [agent.location.X,agent.location.Y, agent.rotation.Yaw]#机器人的当前位姿
        img_data = camera.capture_image(GrabSim_pb2.CameraName.Head_Color,0)
        img = img_data.images[0]
        img = np.frombuffer(img.data, dtype=img.dtype).reshape((img.height, img.width, img.channels))
        instr = "we have three person and want to sit near the window."#"get me the chair."
        img,instr,state=preprocess(image=img,instruction=instr,state=walk_value)
        move_pose = model(img.to(device),instr.to(device),state.to(device)).tolist()
        # dx,dy,dz=random.random()*500,random.random()*500,random.random()*500
        dx,dy=move_pose[0]
        print(f"walk_v for this frame:,{dx},{dy}")
        action = navigator.navigate_to_limit(x=agent.location.X+dx*100,y=agent.location.Y+dy*100,yaw=agent.rotation.Yaw - 90,velocity=900,distance_limit=100)
        print("navi result:",action)  # print navigation info
        # print(agent.info)  # print navigation info
        time.sleep(2)
        frame_count+=1