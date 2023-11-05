import time
import matplotlib.pyplot as plt
import numpy as np
import GrabSim_pb2
from utils.SceneManager import SceneManager
from utils.CameraController import CameraController
from utils.NavigationController import NavigationController
from map.map_builder import Semantic_Mapping
import map.depth_utils as du
import threading
import argparse
import torch

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
    parser.add_argument('--log_interval', type=int, default=10,
                        help="""log interval, one log per n updates
                                (default: 10) """)
    parser.add_argument('--save_interval', type=int, default=1,
                        help="""save interval""")
    parser.add_argument('-d', '--dump_location', type=str, default="./tmp/",
                        help='path to dump models and log (default: ./tmp/)')
    parser.add_argument('--exp_name', type=str, default="exp1",
                        help='experiment name (default: exp1)')
    parser.add_argument('--save_periodic', type=int, default=5000,
                        help='Model save frequency in number of updates')
    parser.add_argument('--load', type=str, default="0",
                        help="""model path to load,
                                0 to not reload (default: 0)""")
    parser.add_argument('-v', '--visualize', type=int, default=0,
                        help="""1: Render the observation and
                                   the predicted semantic map,
                                2: Render the observation with semantic
                                   predictions and the predicted semantic map
                                (default: 0)""")
    parser.add_argument('--print_images', type=int, default=0,
                        help='1: save visualization as images')

    # Environment, dataset and episode specifications
    parser.add_argument('-efw', '--env_frame_width', type=int, default=640,
                        help='Frame width (default:640)')
    parser.add_argument('-efh', '--env_frame_height', type=int, default=480,
                        help='Frame height (default:480)')
    parser.add_argument('-fw', '--frame_width', type=int, default=640,
                        help='Frame width (default:160)')
    parser.add_argument('-fh', '--frame_height', type=int, default=480,
                        help='Frame height (default:120)')
    parser.add_argument('-el', '--max_episode_length', type=int, default=1000,
                        help="""Maximum episode length""")
    parser.add_argument("--task_config", type=str,
                        default="tasks/objectnav_gibson.yaml",
                        help="path to config yaml containing task information")
    parser.add_argument("--split", type=str, default="TG",
                        help="dataset split (train | val | val_mini | TG) ")
    parser.add_argument('--camera_height', type=float, default=0.72,
                        help="agent camera height in metres")
    parser.add_argument('--hfov', type=float, default=80.5,
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
    parser.add_argument('--vision_range', type=int, default=100)
    parser.add_argument('--map_resolution', type=int, default=5)
    parser.add_argument('--du_scale', type=int, default=1)
    parser.add_argument('--map_size_cm', type=int, default=2400)
    parser.add_argument('--cat_pred_threshold', type=float, default=1.0)
    parser.add_argument('--map_pred_threshold', type=float, default=1.0)
    parser.add_argument('--exp_pred_threshold', type=float, default=1.0)
    parser.add_argument('--collision_threshold', type=float, default=0.15)

    # parse arguments
    args = parser.parse_args()

    args.cuda = not args.no_cuda and torch.cuda.is_available()

    if not args.cuda:
        args.sem_gpu_id = -2

    if args.num_mini_batch == "auto":
        args.num_mini_batch = max(args.num_processes // 2, 1)
    else:
        args.num_mini_batch = int(args.num_mini_batch)

    if args.map_id == 3:
        args.split = 'Starbucks'
        args.num_sem_categories = 1#20
        if args.task == 'objectnav':
            args.num_eval_episodes = 19
        elif args.task == 'reasoning':
            args.num_eval_episodes = 45
            args.episodes_dir = 'dataset/reasoning/'
        elif args.task == 'simple':
            args.num_eval_episodes = 95
            args.episodes_dir = 'dataset/simple/'
        elif args.task == 'vln':
            args.num_eval_episodes = 56
            args.episodes_dir = 'dataset/vln/'
        else:
            raise ValueError('Unknown task!')
        args.categories_file = 'dataset/objectnav/Starbucks_categories.json'
        args.max_episode_length = 500

    args.device = torch.device("cpu" )
    return args


def get_obs(stub):
    images=[] 
    images= stub.Capture(GrabSim_pb2.CameraList(scene=0, cameras=[  \
        GrabSim_pb2.CameraName.Head_Depth, GrabSim_pb2.CameraName.Head_Color, \
        GrabSim_pb2.CameraName.Head_Segment ])).images
    depth = np.frombuffer(images[0].data, dtype=images[0].dtype).reshape(
        (images[0].height, images[0].width, images[0].channels))
    rgb = np.frombuffer(images[1].data, dtype=images[1].dtype).reshape(
        (images[1].height, images[1].width, images[1].channels))
    # convert to BGR format
    rgb = rgb[:, :, [2, 1, 0]]
    seg = np.frombuffer(images[2].data, dtype=images[2].dtype).reshape(
        (images[2].height, images[2].width, images[2].channels))
    # self.fx = images[0].parameters.fx
    # self.fy = images[0].parameters.fy
    # self.cx = images[0].parameters.cx
    # self.cy = images[0].parameters.cy
    # self.matrix = np.array(images[0].parameters.matrix).reshape((4, 4)).transpose()
    obs = np.concatenate((rgb, depth,seg), axis=2).transpose(2, 0, 1)
    obs = torch.from_numpy(obs).view(1, 5, 480, 640)
    print(obs.size())
    return obs

def navigate(thread_name):
    print(f"Thread {thread_name} is running")
    navigator = NavigationController(scene_manager)

    target_x = 247  # Target x-coordinate
    target_y = 0  # Target y-coordinate

    yaw=30
    # Example navigation
    result_scene = navigator.navigate_to_limit(target_x, target_y,yaw,200,100)
    print("Navigation result:", result_scene.info)

if __name__ == '__main__':
    scene_manager = SceneManager()
    map_id = 3  # Map ID: 3 for the coffee shop
    scene_manager.load_scene(map_id)
    time.sleep(5)
    num_scenes=1
    # 导航
    thread1 = threading.Thread(target=navigate, args=("Thread 1:navigation",))
    thread1.start()
    # 建图
    args=get_args()
    
    device =args.device
    sem_map_module = Semantic_Mapping(args)
    sem_map_module.eval()
    free_sem_map_module = Semantic_Mapping(args, max_height=20, min_height=-150)
    free_sem_map_module.eval()
    # Predict semantic map from frame 1
        # Predict semantic map from frame 1
    
    poses = torch.tensor([scene_manager.get_robo_pose()], dtype=torch.float32).to(device)
    # Initialize map variables:
    # Full map consists of multiple channels containing the following:
    # 1. Obstacle Map
    # 2. Exploread Area
    # 3. Current Agent Location
    # 4. Past Agent Locations
    # 5,6,7,.. : Semantic Categories
    nc = args.num_sem_categories + 4  # num channels

    # Calculating full and local map sizes
    map_size = args.map_size_cm // args.map_resolution
    full_w, full_h = map_size, map_size
    local_w = int(full_w / args.global_downscaling)
    local_h = int(full_h / args.global_downscaling)

    # Initializing full and local map
    full_map = torch.zeros(num_scenes, nc, full_w, full_h).float().to(device)
    local_map = torch.zeros(num_scenes, nc, local_w,
                            local_h).float().to(device)

    # Initial full and local pose
    full_pose = torch.zeros(num_scenes, 3).float().to(device)
    local_pose = torch.zeros(num_scenes, 3).float().to(device)

    obs=get_obs(scene_manager.sim_client)
    # obs = torch.from_numpy(obs).unsqueeze(0)
    
    
    local_pose2 = local_pose.clone()
    free_local_map = local_map.clone()

    _, local_map, _, local_pose = \
        sem_map_module(obs, poses, local_map, local_pose)
    _, free_local_map, _, _ = \
        free_sem_map_module(obs, poses, free_local_map, local_pose2)


    
    camera=CameraController(scene_manager)
    
    
    
    while(True):
        obs =  get_obs(scene_manager.sim_client)
#        obs = torch.from_numpy(obs).cuda(device).unsqueeze(0)
        #depth=camera.capture_image(GrabSim_pb2.CameraName.Head_Depth)
        poses=torch.tensor(scene_manager.get_robo_pose())
  

        _, local_map, _, local_pose = sem_map_module(obs, poses, local_map, local_pose)
        _, free_local_map, _, _ = free_sem_map_module(obs, poses, free_local_map, local_pose2)
        

