import numpy as np
import map.depth_utils as du
import map.rotation_utils as ru
import open3d as o3d
import matplotlib.pyplot as plt
from map.pcd_process import *
import GrabSim_pb2

class MapBuilder(object):
    def pos_to_index(self,x,y):
        return int((x+self.map_size_cm/2)//self.resolution),int((y+(self.map_size_cm-700)/2)//self.resolution)
        
    def __init__(self, params):
        self.params = params
        frame_width = params['frame_width']#640
        frame_height = params['frame_height']#480
        self.fov = params['fov']
        self.camera_matrix = du.get_camera_matrix(
            frame_width,
            frame_height,
            self.fov)
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
        self.seg_pcd_map = o3d.geometry.PointCloud()

        self.agent_height = params['agent_height']
        self.agent_view_angle = params['agent_view_angle']
        self.count=0
        self.log_prob_map = np.zeros_like(self.map) # 
        # Log-Probabilities to add or remove from the map 
        self.l_occ = np.log(0.65/0.35)
        self.l_free = np.log(0.35/0.65)
        return
    
    '''
    input : scene_manager
    usage : get walkers' loc in current view
    return : list of walkers' centers in world space (x,y)
    '''
    def get_walkers_loc(self,scene_manager,visualize=False):
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

        cluster_centers = cluster_and_get_center(pcd, eps=30, min_points=8,vis=visualize)
        if len(cluster_centers)==0:
            return np.array([])
        return cluster_centers[:,[0,2]]

    def getViewMap(self,x,y,yaw):

        maxDepth = self.vision_range//self.resolution  # 最大观测深度
        ix, iy = self.pos_to_index(x, y)
        viewMap = np.zeros_like(self.map,dtype=np.int8)  # 创建与地图相同形状的零矩阵

        yaw_rad = yaw 
        fov_rad = np.radians(self.fov)
        print((yaw_rad,fov_rad))

        # 扇形区域的角度范围
        start_angle = yaw_rad - fov_rad / 2
        end_angle = yaw_rad + fov_rad / 2
        # 确定正方形边界
        square_size = 2 * maxDepth  # 正方形边界大小为最大观测深度的两倍
        min_i = max(0, ix - square_size // 2)
        max_i = min(viewMap.shape[0], ix + square_size // 2)
        min_j = max(0, iy - square_size // 2)
        max_j = min(viewMap.shape[1], iy + square_size // 2)

        # 填充相机可观测到的区域
        for i in range(min_i, max_i):
            for j in range(min_j, max_j):
                # 计算当前位置与机器人位置的角度和距离
                angle_to_point = np.arctan2(j - iy, i - ix)
                distance_to_point_2 = (i - ix) ** 2 + (j - iy) ** 2

                # 判断当前位置是否在相机视野范围内且在最大观测深度内
                if start_angle <= angle_to_point <= end_angle and distance_to_point_2 <= maxDepth**2:
                    viewMap[i, j] = 1  # 观测到的区域标记为1（或者你需要的其他数值）

        plt.imshow(viewMap, cmap='gray')
        plt.title('Visualization of ViewMap')
        plt.colorbar(label='Observability')
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.show()
        return viewMap



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
        # 获取语义点云，去除天花板、地板、行人
        point_seg ,point_cloud = get_point_cloud_of_view_and_remove(new_seg,depth,self.camera_matrix,5)

        agent_view = du.transform_camera_view(point_cloud,
                                              self.agent_height,
                                              self.agent_view_angle)

        # viz_3d(point_cloud)
        geocentric_pc = du.transform_pose(agent_view, current_pose)
        
        # viz_segment_3d(point_seg,geocentric_pc)
        cur_point_cloud = o3d.geometry.PointCloud()
        cur_point_cloud.points = o3d.utility.Vector3dVector(geocentric_pc)
        cur_point_cloud.colors = o3d.utility.Vector3dVector(point_seg)
        self.seg_pcd_map+=cur_point_cloud
        # self.seg_pcd_map = self.seg_pcd_map.voxel_down_sample(voxel_size=self.resolution)
        

        # if self.count%5==0:
        #     o3d.visualization.draw_geometries([self.seg_pcd_map])
        # self.count+=1

        


        cur_grid_map=self.to_2d_grid_map(geocentric_pc,self.agent_min_z,self.agent_max_z)

        # vmap=self.getViewMap(current_pose[0],current_pose[1],current_pose[2])
        # free_mask = vmap&(cur_grid_map<=1)
        # occ_mask = vmap&(cur_grid_map>1)

        # # Adjust the cells appropriately
        # self.log_prob_map[occ_mask] += self.l_occ
        # self.log_prob_map[free_mask] += self.l_free

        # cur_grid_map=np.where(cur_grid_map>0,max(cur_grid_map-4,0),0)
        self.map = self.map + cur_grid_map


        return self.map


    def reset_map(self, map_size):
        self.map_size_cm = map_size

        self.map = np.zeros((self.map_size_cm // self.resolution,
                             self.map_size_cm // self.resolution), dtype=np.float32)

    def get_map(self):
        return self.map
