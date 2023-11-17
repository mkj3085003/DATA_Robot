import numpy as np
import DATA_Robot.map.depth_utils as du
import DATA_Robot.map.rotation_utils as ru
import open3d as o3d
import matplotlib.pyplot as plt
from DATA_Robot.map.pcd_process import *
import GrabSim_pb2

class MapBuilder(object):
    def pos_to_index(self,x,y):
        return int((x+self.map_size_cm/2)//self.resolution),int((y+self.map_size_cm/2)//self.resolution)
        
    def __init__(self, params):
        self.params = params
        frame_width = params['frame_width']#640
        frame_height = params['frame_height']#480
        fov = params['fov']
        self.camera_matrix = du.get_camera_matrix(
            frame_width,
            frame_height,
            fov)
        self.vision_range = params['vision_range']#600(?

        self.map_size_cm = params['map_size_cm']#2400
        self.resolution = params['resolution']#5
        
        self.agent_min_z = params['agent_min_z']#10
        self.agent_max_z = params['agent_max_z']#180
        self.z_bins = [self.agent_min_z, self.agent_max_z]
        self.du_scale = params['du_scale']#1
      
        self.obs_threshold = params['obs_threshold']

        #2400//5=480
        self.map = np.zeros((self.map_size_cm // self.resolution,
                             self.map_size_cm // self.resolution), dtype=np.float32)

        self.agent_height = params['agent_height']
        self.agent_view_angle = params['agent_view_angle']
        return
    
    '''
    input : scene_manager
    usage : get walkers' loc in current view
    return : list of walkers' centers in world space (x,y)
    '''
    def get_walkers_loc(self,scene_manager):
        stub=scene_manager.sim_client
        current_pose=np.array(scene_manager.get_pose_XYRad())
        images=[] 
        images= stub.Capture(GrabSim_pb2.CameraList(scene=0, cameras=[  \
            GrabSim_pb2.CameraName.Head_Depth, \
            GrabSim_pb2.CameraName.Head_Segment ])).images
        
        depth = np.frombuffer(images[0].data, dtype=images[0].dtype).reshape(
            (images[0].height, images[0].width, images[0].channels))
        seg = np.frombuffer(images[1].data, dtype=images[1].dtype).reshape(
            (images[1].height, images[1].width, images[1].channels))
        
        colors=seg_to_rgb(seg)
        
        point_seg ,point_cloud = get_point_cloud_of_view(colors,depth,self.camera_matrix)
    
        agent_view = du.transform_camera_view(point_cloud,
                                              self.agent_height,
                                              self.agent_view_angle)
        geocentric_pc = du.transform_pose(agent_view, current_pose)

        point_cloud = o3d.geometry.PointCloud()
        point_cloud.points = o3d.utility.Vector3dVector(geocentric_pc)
        point_cloud.colors=o3d.utility.Vector3dVector(point_seg)
        
        pcd=get_pcd_by_id(point_cloud,251)#行人

        # o3d.visualization.draw_geometries([pcd])
        cluster_centers = cluster_and_get_center(pcd, eps=30, min_points=8,vis=False)
        return cluster_centers[:,[0,1]]




    # def to_3d_grid_map(self,points,z_min_cm,z_max_cm):
    #     M   =  self.map_size//self.resolution
    #     H   =  (z_max_cm-z_min_cm)//self.resolution
    #     grid_map=np.zeros((M, M, H+1), dtype=np.int)
    #     for point in points:
    #         x, z, y = point
    #         grid_x,grid_y =self.pos_to_index(x,y)
    #         grid_z = (z-z_min_cm)//self.resolution

    #         # 确保点在 grid map 范围内
    #         if 0 <= grid_x < M and 0 <= grid_y < M and 0 <= grid_z <= H:
    #             grid_map[grid_x, grid_y, grid_z] += 1
    #     return grid_map



    def to_2d_grid_map(self,points,z_min_cm,z_max_cm):
        M   =  self.map_size_cm//self.resolution
        H   =  (z_max_cm-z_min_cm)//self.resolution
        grid_map=np.zeros((M, M))
        for point in points:
            x, z,y = point
            grid_x,grid_y =self.pos_to_index(x,y)
            grid_z = (z-z_min_cm)//self.resolution

            # 确保点在 grid map 范围内
            if 0 <= grid_x < M and 0 <= grid_y < M and 0 <= grid_z <= H:
                grid_map[grid_x, grid_y] += 1
        return grid_map



    def update_map(self,seg, depth, current_pose):
       

        #  将seg数组映射到颜色
        new_seg=seg_to_rgb(seg)
       # point_cloud = get_point_cloud_of_view(np.ones(shape=(depth.shape[0],depth.shape[1],3)),depth,self.camera_matrix,5)
        point_seg ,point_cloud = get_point_cloud_of_view(new_seg,depth,self.camera_matrix,5)
     
        agent_view = du.transform_camera_view(point_cloud,
                                              self.agent_height,
                                              self.agent_view_angle)

        # viz_3d(point_cloud)
        geocentric_pc = du.transform_pose(agent_view, current_pose)
        
        # viz_segment_3d(point_seg,geocentric_pc)


        cur_grid_map=self.to_2d_grid_map(geocentric_pc,self.agent_min_z,self.agent_max_z)



        # cur_grid_map=np.where(cur_grid_map>0,max(cur_grid_map-4,0),0)
        self.map = self.map + cur_grid_map


        return self.map


    def reset_map(self, map_size):
        self.map_size_cm = map_size

        self.map = np.zeros((self.map_size_cm // self.resolution,
                             self.map_size_cm // self.resolution), dtype=np.float32)

    def get_map(self):
        return self.map
