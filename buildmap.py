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
import torch

navigate_end =False

test_point_cloud=False

def get_args():
    parser = argparse.ArgumentParser(
        description='MO-VLN')

    # General Arguments
    parser.add_argument('--seed', type=int, default=1,
                        help='random seed (default: 1)')
    parser.add_argument('--auto_gpu_config', type=int, default=0)
    parser.add_argument('--total_num_scenes', type=str, default="1")
    parser.add_argument('-n', '--num_processes', type=int, default=1,
                        help="""how many training processes to use (default:5)
                                Overridden when auto_gpu_config=1
                                and training on gpus""")
    parser.add_argument('--num_processes_per_gpu', type=int, default=0)
    parser.add_argument('--num_processes_on_first_gpu', type=int, default=1)
    parser.add_argument('--eval', type=int, default=1,
                        help='0: Train, 1: Evaluate (default: 0)')
    parser.add_argument('--num_training_frames', type=int, default=10000000,
                        help='total number of training frames')
    parser.add_argument('--num_eval_episodes', type=int, default=200,
                        help="number of test episodes per scene")
    parser.add_argument('--num_train_episodes', type=int, default=10000,
                        help="""number of train episodes per scene
                                before loading the next scene""")
    parser.add_argument('--no_cuda', action='store_true', default=False,
                        help='disables CUDA training')
    parser.add_argument("--sim_gpu_id", type=int, default=0,
                        help="gpu id on which scenes are loaded")
    parser.add_argument("--sem_gpu_id", type=int, default=0,
                        help="""gpu id for semantic model,
                                -1: same as sim gpu, -2: cpu""")

    # Logging, loading models, visualization


    # Environment, dataset and episode specifications

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
    parser.add_argument('--forward_cm', type=float, default=20,
                        help="Agent forward in cm")
    parser.add_argument('--q', type=float, default=0.3,
                        help="Minimum depth for depth sensor in meters")
    parser.add_argument('--max_depth', type=float, default=6.0,
                        help="Maximum depth for depth sensor in meters")
    parser.add_argument('--success_dist', type=float, default=3.0,
                        help="success distance threshold in meters")
    parser.add_argument('--floor_thr', type=int, default=50,
                        help="floor threshold in cm")
    parser.add_argument('--min_d', type=float, default=1.5,
                        help="min distance to goal during training in meters")
    parser.add_argument('--max_d', type=float, default=100.0,
                        help="max distance to goal during training in meters")
    parser.add_argument('--version', type=str, default="v2",
                        help="dataset version, v1: single process (0410); v2: newest")
    parser.add_argument('--map_id', type=int, default=3,
                        help="3: Starbucks; 4: TG; 5: NursingRoom")

    # Model Hyperparameters
    parser.add_argument('--agent', type=str, default="sem_exp")
    parser.add_argument('--lr', type=float, default=2.5e-5,
                        help='learning rate (default: 2.5e-5)')
    parser.add_argument('--global_hidden_size', type=int, default=256,
                        help='global_hidden_size')
    parser.add_argument('--eps', type=float, default=1e-5,
                        help='RL Optimizer epsilon (default: 1e-5)')
    parser.add_argument('--alpha', type=float, default=0.99,
                        help='RL Optimizer alpha (default: 0.99)')
    parser.add_argument('--gamma', type=float, default=0.99,
                        help='discount factor for rewards (default: 0.99)')
    parser.add_argument('--use_gae', action='store_true', default=False,
                        help='use generalized advantage estimation')
    parser.add_argument('--tau', type=float, default=0.95,
                        help='gae parameter (default: 0.95)')
    parser.add_argument('--entropy_coef', type=float, default=0.001,
                        help='entropy term coefficient (default: 0.01)')
    parser.add_argument('--value_loss_coef', type=float, default=0.5,
                        help='value loss coefficient (default: 0.5)')
    parser.add_argument('--max_grad_norm', type=float, default=0.5,
                        help='max norm of gradients (default: 0.5)')
    parser.add_argument('--num_global_steps', type=int, default=20,
                        help='number of forward steps in A2C (default: 5)')
    parser.add_argument('--ppo_epoch', type=int, default=4,
                        help='number of ppo epochs (default: 4)')
    parser.add_argument('--num_mini_batch', type=str, default="auto",
                        help='number of batches for ppo (default: 32)')
    parser.add_argument('--clip_param', type=float, default=0.2,
                        help='ppo clip parameter (default: 0.2)')
    parser.add_argument('--use_recurrent_global', type=int, default=0,
                        help='use a recurrent global policy')
    parser.add_argument('--num_local_steps', type=int, default=30,
                        help="""Number of steps the local policy
                                between each global step""")
    parser.add_argument('--reward_coeff', type=float, default=0.1,
                        help="Object goal reward coefficient")
    parser.add_argument('--intrinsic_rew_coeff', type=float, default=0.02,
                        help="intrinsic exploration reward coefficient")
    parser.add_argument('--num_sem_categories', type=float, default=18,
                        help="include navigable area, id: num_sem_categories - 1")
    parser.add_argument('--sem_pred_prob_thr', type=float, default=0.9,
                        help="Semantic prediction confidence threshold")
    parser.add_argument('--categories_file', type=str,
                        default="dataset/objectnav/Starbucks_categories.json")
    parser.add_argument('--det_config_file', type=str,
                        default="/liangxiwen/model/glip_v1/glip_Swin_L.yaml")
    parser.add_argument('--det_weight', type=str,
                        default="/liangxiwen/model/glip_v1/glip_large_model.pth")
    parser.add_argument('--det_thresh', type=float, default=0.5)
    parser.add_argument('--episodes_dir', type=str, default="dataset/objectnav/")
    parser.add_argument('--sem_seg_model_type', type=str, default='glip',
                        help="use different model for detection (glip, grounding_dino)")
    parser.add_argument('--sam_checkpoint', type=str,
                        default="/liangxiwen/model/segment_anything/sam_vit_h_4b8939.pth")
    parser.add_argument('--sam_type', type=str,
                        default="vit_h", help="(vit_h, vit_l, vit_b)")
    parser.add_argument('--task', type=str, default='objectnav',
                        choices=['objectnav', 'reasoning', 'simple', 'vln'])
    parser.add_argument('--reasoning_type', type=str, help='GPT4, chatGPT, vicuna7b, vicuna13b')

    # Mapping
    parser.add_argument('--global_downscaling', type=int, default=2)
    parser.add_argument('--vision_range', type=int, default=600)
    parser.add_argument('--resolution', type=int, default=5)
    parser.add_argument('--du_scale', type=int, default=1)
    parser.add_argument('--map_size_cm', type=int, default=3200)
    parser.add_argument('--cat_pred_threshold', type=float, default=1.0)
    parser.add_argument('--map_pred_threshold', type=float, default=1.0)
    parser.add_argument('--exp_pred_threshold', type=float, default=1.0)
    parser.add_argument('--collision_threshold', type=float, default=0.15)

    #相机俯仰角
    parser.add_argument('--agent_view_angle',type=float, default=-12.0)

    parser.add_argument('--obs_threshold',type=float, default=1.0)
    parser.add_argument('--agent_min_z',type=int, default=-110)
    parser.add_argument('--agent_max_z',type=int, default=70)
    parser.add_argument('--agent_height', type=float, default=0.72,
                        help="agent camera height in metres")
    # parse arguments
    args = parser.parse_args()

    args.cuda = not args.no_cuda and torch.cuda.is_available()


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
    target_y = -10  # Target y-coordinate     #cm?
    yaw = 270
    # Example navigation
    result_scene = navigator.navigate_to_limit(target_x, target_y,yaw,100,100)
    target_x = -50  # Target x-coordinate
    target_y = 0  # Target y-coordinate     #cm?
    yaw = 180
    result_scene = navigator.navigate_to_limit(target_x, target_y,yaw,100,100)
    
    target_x = -50  # Target x-coordinate
    target_y = 500  # Target y-coordinate     #cm?
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






if __name__ == '__main__':
    args=get_args()
    camera_matrix = du.get_camera_matrix(
        args['frame_width'],
        args['frame_height'],
        args['fov'])
    if test_point_cloud:
        color_image = np.array(plt.imread("Head_Color.png"))
        depth_image = np.array(plt.imread("Head_Depth.png"))
        depth_image=(depth_image[:,:,0]).astype(np.float32)*600.0

        depth = np.where(depth_image >= 599.0, 0.0, depth_image)
        # show_pointcloud(color_image,depth,camera_matrix)
        map=MapBuilder(args)
        map.update_map(depth,(247.,        500.,          3.1415926))


    else :
        scene_manager = SceneManager()
        camera=CameraController(scene_manager)
        map_id =11  # Map ID: 3 for the coffee shop
        scene_manager.load_scene(map_id)
        time.sleep(5)
        num_scenes=1
        # 导航线程
        thread1 = threading.Thread(target=navigate)
        thread1.start()
        # 建图
        

        plt.ion() # enable real-time plotting
        plt.figure(1) # create a plot
        mapbuilder=MapBuilder(args)

        
        # camera.save_image(camera.capture_image(GrabSim_pb2.CameraName.Head_Color))

        while True:#not navigate_end :
            rgb,depth,seg =  get_obs(scene_manager.sim_client)
            poses=np.array(scene_manager.get_pose_XYRad())
            depth = np.where(depth >= 599.0, 0.0, depth)
            mp=mapbuilder.update_map(seg,depth,poses)
            x,y=mapbuilder.pos_to_index(poses[0],poses[1])
            vis_map(plt,mp,(x,y,poses[2]))
        

    
    thread1.join()

