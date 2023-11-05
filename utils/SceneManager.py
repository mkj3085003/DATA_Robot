import sys
import time
import grpc

import GrabSim_pb2_grpc
import GrabSim_pb2

class SceneManager:
    def __init__(self):
        # Set up the gRPC channel and client
        self.channel = grpc.insecure_channel('localhost:30001', options=[
            ('grpc.max_send_message_length', 1024 * 1024 * 1024),
            ('grpc.max_receive_message_length', 1024 * 1024 * 1024)
        ])
        self.sim_client = GrabSim_pb2_grpc.GrabSimStub(self.channel)

    def load_scene(self, map_id=0, scene_num=1):
        # Scene initialization
        initworld = self.sim_client.Init(GrabSim_pb2.NUL())

        # Print available maps and their sizes
        print(self.sim_client.AcquireAvailableMaps(GrabSim_pb2.NUL()))

        # Load the specified scene
        initworld = self.sim_client.SetWorld(GrabSim_pb2.BatchMap(count=scene_num, mapID=map_id))

    def reset_scene(self, scene_id=0):
        # Reset the specified scene
        scene = self.sim_client.Reset(GrabSim_pb2.ResetParams(scene=scene_id))

    def get_scene_info(self, scene_id=0):
        # Get environment information for the specified scene
        scene = self.sim_client.Observe(GrabSim_pb2.SceneID(value=scene_id))
        return scene
    
    def show_env_info(self,scene_id=0):
        scene = self.sim_client.Observe(GrabSim_pb2.SceneID(value=scene_id))
        print('------------------show_env_info----------------------')
        print(
            f"location:{[scene.location.X, scene.location.Y]}, rotation:{scene.rotation.Yaw}\n",
            f"joints number:{len(scene.joints)}, fingers number:{len(scene.fingers)}\n", f"objects number: {len(scene.objects)}\n"
            f"rotation:{scene.rotation}, timestep:{scene.timestep}\n"
            f"timestamp:{scene.timestamp}, collision:{scene.collision}, info:{scene.info}")

    '''
    return robot pose
    (X, Y,Yaw(deg))         
    '''
    def get_pose_XYDeg(self,scene_id=0):
        scene =  self.sim_client.Observe(GrabSim_pb2.SceneID(value=scene_id))
        return scene.location.X,scene.location.Y,(scene.rotation.Yaw)
    '''
    return robot pose 
    (X, Y,Yaw(deg))         
    '''
    def get_pose_XYRad(self,scene_id=0):
        scene =  self.sim_client.Observe(GrabSim_pb2.SceneID(value=scene_id))
        return scene.location.X,scene.location.Y,(scene.rotation.Yaw)*3.1415926/180.0


# if __name__ == '__main__':
#     # Create an instance of the SceneManager class
#     scene_manager = SceneManager()
#
#     map_id = 3  # Map ID: 3 for the coffee shop
#     scene_num = 1  # Number of scenes to load
#
#     scene_manager.load_scene(map_id, scene_num)
#     time.sleep(5)
#
#     for i in range(scene_num):
#         print(f"------------------ Scene {i} ----------------------")
#         scene_manager.reset_scene(i)
#         scene_info = scene_manager.get_scene_info(i)
#         print(scene_info)  # You can access various scene information from the 'scene_info' object