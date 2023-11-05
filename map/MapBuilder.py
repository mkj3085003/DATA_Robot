import numpy as np
import map.depth_utils as du

import open3d as o3d
def show_pointcloud(color_raw,depth_raw,camera):
    # create an rgbd image object:
    color = o3d.geometry.Image((color_raw).astype(np.uint8))
    depth=o3d.geometry.Image((depth_raw).astype(np.float32))
    
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(color, depth,depth_scale=100.0,depth_trunc=10, convert_rgb_to_intensity=False)
    # use the rgbd image to create point cloud:
    # 创建相机内参
    # w=640
    # h=480
    # fx=377.982666
    # fy=377.982666
    # cx=319.293274
    # cy=242.534866
    intrinsic = o3d.camera.PinholeCameraIntrinsic(camera.w, camera.h, camera.fx,camera.fy, camera.cx, camera.cy)
    intrinsic.intrinsic_matrix = [[camera.fx, 0, camera.cx], [0, camera.fy, camera.cy], [0, 0, 1]]
    cam = o3d.camera.PinholeCameraParameters()
    cam.intrinsic = intrinsic
   
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, cam.intrinsic)
    pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
    print(np.asarray(pcd.points).shape)
    # print(np.asarray(pcd.points)[100*640+100,:])
    # print(np.asarray(pcd.colors)[100*640+100,:]*255)
    # print(color_raw[100,100,:])
    
    # pcd = pcd.voxel_down_sample(voxel_size=0.1)


    # visualize:
    vis = o3d.visualization.Visualizer()
    vis.create_window(width=camera.w,height=camera.h)
    vis.add_geometry(pcd)
    
    ctr = vis.get_view_control()
    ctr.convert_from_pinhole_camera_parameters(cam)
    
    vis.run()

def get_point_cloud_of_view(color_raw,depth_raw,camera):
    color = o3d.geometry.Image((color_raw).astype(np.uint8))
    depth=o3d.geometry.Image((depth_raw).astype(np.float32))
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(color, depth,depth_scale=100.0,depth_trunc=10, convert_rgb_to_intensity=False)
    intrinsic = o3d.camera.PinholeCameraIntrinsic(camera.w, camera.h, camera.fx,camera.fy, camera.cx, camera.cy)
    intrinsic.intrinsic_matrix = [[camera.fx, 0, camera.cx], [0, camera.fy, camera.cy], [0, 0, 1]]
    cam = o3d.camera.PinholeCameraParameters()
    cam.intrinsic = intrinsic
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, cam.intrinsic)
    pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
    return np.asarray(pcd.points)


class MapBuilder(object):
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
        agent_min_z = params['agent_min_z']#-50
        agent_max_z = params['agent_max_z']#50
        self.z_bins = [agent_min_z, agent_max_z]
        self.du_scale = params['du_scale']#1
        self.visualize = params['visualize']
        self.obs_threshold = params['obs_threshold']

        #2400//5=480
        self.map = np.zeros((self.map_size_cm // self.resolution,
                             self.map_size_cm // self.resolution,
                             len(self.z_bins) + 1), dtype=np.float32)

        self.agent_height = params['agent_height']
        self.agent_view_angle = params['agent_view_angle']
        return

    def update_map(self, depth, current_pose):
        # with np.errstate(invalid="ignore"):
        #     depth[depth > self.vision_range * self.resolution] = np.NaN
        # print(self.camera_matrix)
        point_cloud = get_point_cloud_of_view(depth,np.ones(shape=(depth.shape[0],depth.shape[1],3)),self.camera_matrix)
        
        agent_view = du.transform_camera_view(point_cloud,
                                              self.agent_height,
                                              self.agent_view_angle)

        shift_loc = [self.vision_range * self.resolution // 2, 0, np.pi / 2.0]
        # print(agent_view.shape)
        agent_view_centered = du.transform_pose(agent_view, shift_loc)

        agent_view_flat = du.bin_points(
            agent_view_centered,
            self.vision_range,
            self.z_bins,
            self.resolution)

        agent_view_cropped = agent_view_flat[:, :, 1]
        agent_view_cropped = agent_view_cropped / self.obs_threshold
        agent_view_cropped[agent_view_cropped >= 0.5] = 1.0
        agent_view_cropped[agent_view_cropped < 0.5] = 0.0

        agent_view_explored = agent_view_flat.sum(2)
        agent_view_explored[agent_view_explored > 0] = 1.0

        geocentric_pc = du.transform_pose(agent_view, current_pose)

        geocentric_flat = du.bin_points(
            geocentric_pc,
            self.map.shape[0],
            self.z_bins,
            self.resolution)

        self.map = self.map + geocentric_flat

        map_gt = self.map[:, :, 1] / self.obs_threshold
        map_gt[map_gt >= 0.5] = 1.0
        map_gt[map_gt < 0.5] = 0.0

        explored_gt = self.map.sum(2)
        explored_gt[explored_gt > 1] = 1.0

        return agent_view_cropped, map_gt, agent_view_explored, explored_gt


    def reset_map(self, map_size):
        self.map_size_cm = map_size

        self.map = np.zeros((self.map_size_cm // self.resolution,
                             self.map_size_cm // self.resolution,
                             len(self.z_bins) + 1), dtype=np.float32)

    def get_map(self):
        return self.map
