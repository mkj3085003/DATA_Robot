import time
import matplotlib.pyplot as plt
import numpy as np
import GrabSim_pb2
from utils.SceneManager import SceneManager
from utils.CameraController import CameraController
from utils.NavigationController import NavigationController
from map.MapBuilder import MapBuilder,show_pointcloud
import map.depth_utils as du
import threading
import argparse
import sys
import open3d as o3d

navigate_end =False

test_point_cloud=False

def get_args():
    parser = argparse.ArgumentParser(
        description='buildmap')



    parser.add_argument('-fw', '--frame_width', type=int, default=640,
                        help='Frame width (default:160)')
    parser.add_argument('-fh', '--frame_height', type=int, default=480,
                        help='Frame height (default:120)')

    parser.add_argument('--camera_height', type=float, default=0,
                        help="agent camera height in cm")
    parser.add_argument('--fov', type=float, default=80.5,
                        help="horizontal field of view in degrees")


    parser.add_argument('--max_depth', type=float, default=6.0,
                        help="Maximum depth for depth sensor in meters")

    # Model Hyperparameters
    # Mapping
    # parser.add_argument('--global_downscaling', type=int, default=2)
    parser.add_argument('--vision_range', type=int, default=600)
    parser.add_argument('--resolution', type=int, default=5)
    parser.add_argument('--du_scale', type=int, default=1)
    parser.add_argument('--map_size_cm', type=int, default=2400)
    #相机俯仰角
    parser.add_argument('--agent_view_angle',type=float, default=-12.0)

    parser.add_argument('--obs_threshold',type=float, default=1.0)
    parser.add_argument('--agent_min_z',type=int, default=-110)
    parser.add_argument('--agent_max_z',type=int, default=270)
    parser.add_argument('--agent_height', type=float, default=72,
                        help="agent camera height in metres")
    # parse arguments
    args = parser.parse_args()



    return vars(args)


def get_obs(stub):
    images=[] 
    images= stub.Capture(GrabSim_pb2.CameraList(scene=0, cameras=[  \
        GrabSim_pb2.CameraName.Head_Depth, GrabSim_pb2.CameraName.Head_Color, \
        GrabSim_pb2.CameraName.Head_Segment ])).images
    depth = np.frombuffer(images[0].data, dtype=images[0].dtype).reshape(
        (images[0].height, images[0].width, images[0].channels))
    rgb = np.frombuffer(images[1].data, dtype=images[1].dtype).reshape(
        (images[1].height, images[1].width, images[1].channels))
   
    seg = np.frombuffer(images[2].data, dtype=images[2].dtype).reshape(
        (images[2].height, images[2].width, images[2].channels))

    return rgb,depth,seg

def navigate():
    time.sleep(5)
    navigator = NavigationController(scene_manager)

    
    result_scene = navigator.navigate_to_limit(247, -10,270,100,100)
    
    result_scene = navigator.navigate_to_limit(320, -250,300,100,100)

    result_scene = navigator.navigate_to_limit(170, -330,270,80,100)

    result_scene = navigator.navigate_to_limit(170, -330,220,80,100)

    result_scene = navigator.navigate_to_limit(-50, 0,180,100,100)

    result_scene = navigator.navigate_to_limit(300, 1300,90,100,100)

    # result_scene = navigator.navigate_to_limit(-50, 500,180,80,100)

    result_scene = navigator.navigate_to_limit(-240, 73,90,100,100)

    result_scene = navigator.navigate_to_limit(-240, 480,90,100,100)

    
    
    global navigate_end
    navigate_end = True

def vis_map(plt,map2d,pose):
    plt.clf()
    
    plt.imshow(map2d, cmap='viridis',vmin=0,vmax=15) 
    circle = plt.Circle((pose[1], pose[0]), radius=10.0,color="blue", fill=True)
    plt.gca().add_patch(circle)

    arrow = pose[0:2] + np.array([35, 0]).dot(np.array([[np.cos(pose[2]), np.sin(pose[2])], [-np.sin(pose[2]), np.cos(pose[2])]]))
    plt.plot([pose[1], arrow[1]], [pose[0], arrow[0]])
    plt.text(8, 8, f'({pose[0]:d}, {pose[1]:f})')  # 显示机器人坐标

    plt.pause(0.005)


def add_walkers(sim_client,scene_id = 0):
    print('------------------add_walkers----------------------')
    walker_loc = [[0, 880], [250, 1200],[-50,500], [-55, 750], [70, -200]]
    walker_list = []
    for i in range(len(walker_loc)):
        loc = walker_loc[i] + [0, 0, 100]
        action = GrabSim_pb2.Action(scene = scene_id, action = GrabSim_pb2.Action.ActionType.WalkTo, values = loc)
        scene = sim_client.Do(action)
        print(scene.info)
        if(str(scene.info).find('unreachable') > -1):
            print('当前位置不可达,无法初始化NPC')
        else:
            walker_list.append(GrabSim_pb2.WalkerList.Walker(id = i + 5, pose = GrabSim_pb2.Pose(X = loc[0], Y = loc[1], Yaw = 90)))

    scene = sim_client.AddWalker(GrabSim_pb2.WalkerList(walkers = walker_list, scene = scene_id))
    return scene



if __name__ == '__main__':
    args=get_args()
    # camera_matrix = du.get_camera_matrix(
    #     args['frame_width'],
    #     args['frame_height'],
    #     args['fov'])

    scene_manager = SceneManager()
    camera=CameraController(scene_manager)
    map_id =11  # Map ID: 11 for the coffee shop
    scene_manager.Init()
    scene_manager.SetWorld(map_id)
    scene_manager.Reset(scene_id=0)
    time.sleep(6)

    
    # 添加行人
    add_walkers(scene_manager.sim_client,0)
    # 显示语义地图
    # camera.show_image(camera.capture_image(GrabSim_pb2.CameraName.Head_Segment,0))

    mapbuilder=MapBuilder(args)

    # locs=mapbuilder.get_walkers_loc(scene_manager)
    # print(locs)
    # sys.exit()

    # 导航线程
    thread1 = threading.Thread(target=navigate)
    thread1.start()
    # 建图
    

    plt.ion() # enable real-time plotting
    plt.figure(1) # create a plot
    
    

    while not navigate_end :
        rgb,depth,seg =  get_obs(scene_manager.sim_client)
        poses=np.array(scene_manager.get_pose_XYRad())
        depth = np.where(depth >= 599.0, 0.0, depth)
        mp=mapbuilder.update_map(seg,depth,poses)
        x,y=mapbuilder.pos_to_index(poses[0],poses[1])
        vis_map(plt,mp,(x,y,poses[2]))
    

    o3d.visualization.draw_geometries([mapbuilder.seg_pcd_map])
    thread1.join()

