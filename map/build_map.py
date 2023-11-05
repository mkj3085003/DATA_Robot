# This is an implementation of Occupancy Grid Mapping as Presented
# in Chapter 9 of "Probabilistic Robotics" By Sebastian Thrun et al.
# In particular, this is an implementation of Table 9.1 and 9.2


import scipy.io
import scipy.stats
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import map.depth_utils as du
class MapBuilder(object):
    def __init__(self, params):
        self.params = params
        frame_width = params['frame_width']
        frame_height = params['frame_height']
        fov = params['fov']
        self.camera_matrix = du.get_camera_matrix(
            frame_width,
            frame_height,
            fov)
        self.vision_range = params['vision_range']

        self.map_size_cm = params['map_size_cm']
        self.resolution = params['resolution']
        agent_min_z = params['agent_min_z']
        agent_max_z = params['agent_max_z']
        self.z_bins = [agent_min_z, agent_max_z]
        self.du_scale = params['du_scale']
        self.visualize = params['visualize']
        self.obs_threshold = params['obs_threshold']

        self.map = np.zeros((self.map_size_cm // self.resolution,
                             self.map_size_cm // self.resolution,
                             len(self.z_bins) + 1), dtype=np.float32)

        self.agent_height = params['agent_height']
        self.agent_view_angle = params['agent_view_angle']
        return

    def update_map(self, depth, current_pose):
        with np.errstate(invalid="ignore"):
            depth[depth > self.vision_range * self.resolution] = np.NaN
        point_cloud = du.get_point_cloud_from_z(depth, self.camera_matrix,
                                                scale=self.du_scale)

        agent_view = du.transform_camera_view(point_cloud,
                                              self.agent_height,
                                              self.agent_view_angle)

        shift_loc = [self.vision_range * self.resolution // 2, 0, np.pi / 2.0]
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






if __name__ == '__main__':

    # load matlab generated data (located at https://gitlab.magiccvs.byu.edu/superjax/595R/blob/88a577579a75dc744bca7630716211334e04a528/lab6/state_meas_data.mat?)
    data = scipy.io.loadmat('state_meas_data.mat')
    state = data['X']
    meas = data['z']

    # Define the parameters for the map.  (This is a 100x100m map with grid size 1x1m)
    grid_size = 1.0
    map = Map(int(100/grid_size), int(100/grid_size), grid_size)

    plt.ion() # enable real-time plotting
    plt.figure(1) # create a plot



    for i in tqdm(range(len(state.T))):
        map.update_map(state[:,i], meas[:,:,i].T) # update the map

        # Real-Time Plotting 
        # (comment out these next lines to make it run super fast, matplotlib is painfully slow)
        plt.clf()
        pose = state[:,i]
        circle = plt.Circle((pose[1], pose[0]), radius=3.0, fc='y')
        plt.gca().add_patch(circle)
        arrow = pose[0:2] + np.array([3.5, 0]).dot(np.array([[np.cos(pose[2]), np.sin(pose[2])], [-np.sin(pose[2]), np.cos(pose[2])]]))
        plt.plot([pose[1], arrow[1]], [pose[0], arrow[0]])
        plt.imshow(1.0 - 1./(1.+np.exp(map.log_prob_map)), 'Greys')
        plt.pause(0.005)



    # Final Plotting
    plt.ioff()
    plt.clf()
    plt.imshow(1.0 - 1./(1.+np.exp(map.log_prob_map)), 'Greys') # This is probability
    plt.imshow(map.log_prob_map, 'Greys') # log probabilities (looks really cool)
    plt.show()