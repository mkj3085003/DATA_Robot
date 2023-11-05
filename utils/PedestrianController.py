import GrabSim_pb2
import time

from .SceneManager import SceneManager
class PedestrianController:
    def __init__(self, scene_manager):
        # Set up the gRPC channel and client
        self.scene_manager = scene_manager

    def add_one_pedestrian(self, walker_id, start_x, start_y, start_yaw, scene_id=0):
        # Define the starting pose of the pedestrian
        pose = GrabSim_pb2.Pose(X=start_x, Y=start_y, Yaw=start_yaw)
        # Create a pedestrian with the starting pose
        pedestrian = GrabSim_pb2.WalkerList.Walker(id=walker_id, pose=pose)  # Assuming id=0 for a single pedestrian
        # Add the pedestrian to the scene
        scene = self.scene_manager.sim_client.AddWalker(GrabSim_pb2.WalkerList(walkers=[pedestrian], scene=scene_id))
        return scene

    def control_one_pedestrian(self, walker_id, end_x, end_y, end_yaw, walker_speed=200, scene_id=0):
        # Create a pedestrian control with the target pose
        pose = GrabSim_pb2.Pose(X=end_x, Y=end_y, Yaw=end_yaw)
        control = GrabSim_pb2.WalkerControls.WControl(id=walker_id, autowalk=False, speed=walker_speed, pose=pose)
        # Control the pedestrian's movement
        scene = self.scene_manager.sim_client.ControlWalkers(GrabSim_pb2.WalkerControls(controls=[control], scene=scene_id))
        time.sleep(10)  # Wait for the pedestrian to move
        return scene

    def remove_one_pedestrian(self, walker_id, scene_id=0):
        # Remove the pedestrian from the scene
        scene = self.scene_manager.sim_client.RemoveWalkers(GrabSim_pb2.RemoveList(IDs=[walker_id], scene=scene_id))
        time.sleep(2)  # Wait for the removal
        return scene

    def add_multiple_pedestrians(self, pedestrian_data_list, scene_id=0):
        # Add multiple pedestrians to the scene
        walker_list = []
        for data in enumerate(pedestrian_data_list):
            walker_id,start_x, start_y, start_yaw = data
            walker = GrabSim_pb2.WalkerList.Walker(
                id= walker_id,
                pose=GrabSim_pb2.Pose(X=start_x, Y=start_y, Yaw=start_yaw)
            )
            walker_list.append(walker)
        scene = self.scene_manager.sim_client.AddWalker(GrabSim_pb2.WalkerList(walkers=walker_list, scene=scene_id))
        return scene


    def control_multiple_pedestrians(self, pedestrian_controls, scene_id=0):
        controls = []
        for i, control_data in enumerate(pedestrian_controls):
            walker_id, end_x, end_y, end_yaw, speed, autowalk= control_data
            pose = GrabSim_pb2.Pose(X=end_x, Y=end_y, Yaw=end_yaw)
            control = GrabSim_pb2.WalkerControls.WControl(
                id=walker_id,
                autowalk=autowalk,
                speed=speed,
                pose=pose
            )
            controls.append(control)
        scene = self.scene_manager.sim_client.ControlWalkers(GrabSim_pb2.WalkerControls(controls=controls, scene=scene_id))
        return scene

    def remove_multiple_pedestrians(self, walker_ids, scene_id=0):
        scene = self.scene_manager.sim_client.RemoveWalkers(GrabSim_pb2.RemoveList(IDs=walker_ids, scene=scene_id))
        return scene

    def get_walkers(self, scene_id=0):
        # 获取场景中的行人信息
        s = self.scene_manager.sim_client.Observe(GrabSim_pb2.SceneID(value=scene_id))
        return s.walkers



if __name__ == '__main__':
    print("加载场景信息")
    scene_manager = SceneManager()

    map_id = 3
    scene_num = 1

    scene_manager.load_scene(map_id, scene_num)
    time.sleep(5)

    for i in range(scene_num):
        print(f"------------------ Scene {i} ----------------------")
        scene_manager.reset_scene(i)
        scene_info = scene_manager.get_scene_info(i)
        # print(scene_info)

    # Pass the scene_manager to the PedestrianController constructor
    pedestrian_controller = PedestrianController(scene_manager)
    pedestrian_controller.add_one_pedestrian(0, 0, 0, 0)
    result_scene = pedestrian_controller.control_one_pedestrian(0, 0,200, 180)
    print("Pedestrian Control result:", result_scene.info)
    walkers=pedestrian_controller.get_walkers()
    print(walkers)

