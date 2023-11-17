import time
import numpy as np
import GrabSim_pb2
from DATA_Robot.utils.SceneManager import SceneManager
from DATA_Robot.utils.CameraController import CameraController
from DATA_Robot.utils.NavigationController import NavigationController
from map.MapBuilder import MapBuilder
import map.depth_utils as du
import argparse
import sys

navigate_end =False

test_point_cloud=False

def get_args():
    parser = argparse.ArgumentParser(
        description='MO-VLN')



    parser.add_argument('-fw', '--frame_width', type=int, default=640,
                        help='Frame width (default:160)')
    parser.add_argument('-fh', '--frame_height', type=int, default=480,
                        help='Frame height (default:120)')

    parser.add_argument('--camera_height', type=float, default=0,
                        help="agent camera height in cm")
    parser.add_argument('--fov', type=float, default=80.5,
                        help="horizontal field of view in degrees")
    parser.add_argument('--turn_angle', type=float, default=15,
                        help="Agent turn angle in degrees")

    parser.add_argument('--q', type=float, default=0.3,
                        help="Minimum depth for depth sensor in meters")
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
    parser.add_argument('--agent_max_z',type=int, default=70)
    parser.add_argument('--agent_height', type=float, default=0.72,
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
    target_x = 247  # Target x-coordinate
    target_y = -10  # Target y-coordinate    
    yaw = 270
    
    result_scene = navigator.navigate_to_limit(target_x, target_y,yaw,100,100)
    target_x = -50  # Target x-coordinate
    target_y = 0  # Target y-coordinate     
    yaw = 180
    result_scene = navigator.navigate_to_limit(target_x, target_y,yaw,100,100)
    
    target_x = -50  # Target x-coordinate
    target_y = 500  # Target y-coordinate   
    yaw = 180
    result_scene = navigator.navigate_to_limit(target_x, target_y,yaw,100,100)
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
    camera_matrix = du.get_camera_matrix(
        args['frame_width'],
        args['frame_height'],
        args['fov'])

    scene_manager = SceneManager()
    camera=CameraController(scene_manager)
    map_id =11  # Map ID: 11 for the coffee shop
    scene_manager.load_scene(map_id)
    num_scenes=1
    scene_manager.reset_scene(scene_id=0)
    time.sleep(6)

    
    # 添加行人
    add_walkers(scene_manager.sim_client,0)
    # 显示语义地图
    # camera.show_image(camera.capture_image(GrabSim_pb2.CameraName.Head_Segment,0))

    mapbuilder=MapBuilder(args)
    mapbuilder.get_walkers_loc(scene_manager)



    
    sys.exit()
    # 导航线程
    thread1 = threading.Thread(target=navigate)
    #thread1.start()
    # 建图
    

    plt.ion() # enable real-time plotting
    plt.figure(1) # create a plot
    

    
    

    while True:#not navigate_end :
        rgb,depth,seg =  get_obs(scene_manager.sim_client)
        poses=np.array(scene_manager.get_pose_XYRad())
        depth = np.where(depth >= 599.0, 0.0, depth)
        mp=mapbuilder.update_map(seg,depth,poses)
        x,y=mapbuilder.pos_to_index(poses[0],poses[1])
        vis_map(plt,mp,(x,y,poses[2]))
    

    
    thread1.join()

