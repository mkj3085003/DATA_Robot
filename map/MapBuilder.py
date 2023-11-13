import numpy as np
import map.depth_utils as du
import map.rotation_utils as ru
import open3d as o3d
import matplotlib.pyplot as plt
def show_pointcloud(color_raw,depth_raw,camera):
    # create an rgbd image object:
    color = o3d.geometry.Image((color_raw).astype(np.uint8))
    depth=o3d.geometry.Image((depth_raw).astype(np.float32))
    
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(color, depth,depth_scale=100.0,depth_trunc=10, convert_rgb_to_intensity=False)
    # use the rgbd image to create point cloud:

    intrinsic = o3d.camera.PinholeCameraIntrinsic(camera.w, camera.h, camera.fx,camera.fy, camera.cx, camera.cy)
    intrinsic.intrinsic_matrix = [[camera.fx, 0, camera.cx], [0, camera.fy, camera.cy], [0, 0, 1]]
    cam = o3d.camera.PinholeCameraParameters()
    cam.intrinsic = intrinsic
   
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, cam.intrinsic)
    pcd.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])

    # visualize:
    vis = o3d.visualization.Visualizer()
    vis.create_window(width=camera.w,height=camera.h)
    vis.add_geometry(pcd)
    
    ctr = vis.get_view_control()
    ctr.convert_from_pinhole_camera_parameters(cam)
    
    vis.run()

def get_point_cloud_of_view(color_raw,depth_raw,camera,downscal):
    color = o3d.geometry.Image((color_raw).astype(np.uint8))
    depth=o3d.geometry.Image((depth_raw).astype(np.float32))
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(color, depth,depth_scale=1.0,depth_trunc=600, convert_rgb_to_intensity=False)
    intrinsic = o3d.camera.PinholeCameraIntrinsic(camera.w, camera.h, camera.fx,camera.fy, camera.cx, camera.cy)
    intrinsic.intrinsic_matrix = [[camera.fx, 0, camera.cx], [0, camera.fy, camera.cy], [0, 0, 1]]
    cam = o3d.camera.PinholeCameraParameters()
    cam.intrinsic = intrinsic
    
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, cam.intrinsic)
    # pcd=o3d.geometry.voxel_down_sample(pcd,downscal)    #下采样cm
    pcd=pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])

    return np.asarray(pcd.colors),np.asarray(pcd.points)


def viz_3d(point):
    # 可视化点云
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(point)
    coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=20.0, origin=[0, 0, 0])
    o3d.visualization.draw_geometries([point_cloud,coordinate_frame])


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
    


    def to_3d_grid_map(self,points,z_min_cm,z_max_cm):
        M   =  self.map_size//self.resolution
        H   =  (z_max_cm-z_min_cm)//self.resolution
        grid_map=np.zeros((M, M, H+1), dtype=np.int)
        for point in points:
            x, z, y = point
            grid_x,grid_y =self.pos_to_index(x,y)
            grid_z = (z-z_min_cm)//self.resolution

            # 确保点在 grid map 范围内
            if 0 <= grid_x < M and 0 <= grid_y < M and 0 <= grid_z <= H:
                grid_map[grid_x, grid_y, grid_z] += 1
        return grid_map



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
        new_seg = np.repeat(seg, 3, axis=2)
     
       # point_cloud = get_point_cloud_of_view(np.ones(shape=(depth.shape[0],depth.shape[1],3)),depth,self.camera_matrix,5)
        point_seg ,point_cloud = get_point_cloud_of_view(new_seg,depth,self.camera_matrix,5)
     
        agent_view = du.transform_camera_view(point_cloud,
                                              self.agent_height,
                                              self.agent_view_angle)

        # viz_3d(point_cloud)
        geocentric_pc = du.transform_pose(agent_view, current_pose)
        # for i in range(len(geocentric_pc)):
        #     if geocentric_pc[i][1]>70 or geocentric_pc[i][1]<-120:
        #         geocentric_pc[i]=np.zeros((1,3))
        # viz_3d(geocentric_pc)
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
