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

    def control_one_pedestrian_autowalk(self, walker_id, autowalker, walker_speed=200, scene_id=0):

        control = GrabSim_pb2.WalkerControls.WControl(id=walker_id, autowalk=autowalker, speed=walker_speed)
        # Control the pedestrian's movement
        scene = self.scene_manager.sim_client.ControlWalkers(GrabSim_pb2.WalkerControls(controls=[control], scene=scene_id))
        # time.sleep(10)  # Wait for the pedestrian to move
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
            walker_id, start_x, start_y, start_yaw = data[1]
            walker = GrabSim_pb2.WalkerList.Walker(
                id=walker_id,
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

    '''
    根据任务类型，执行对应的子任务，返回当前子任务执行情况
    '''
    def control_robot_action(self, type=0, action=0, message="你好",scene_id=0,):
        scene = self.scene_manager.sim_client.ControlRobot(
            GrabSim_pb2.ControlInfo(scene=scene_id, type=type, action=action, content=message))
        if (str(scene.info).find("Action Success") > -1):
            # print(scene.info)
            return True
        else:
            # print(scene.info)
            return False

    def talk_walkers(self, walker_name, content, scene_id=0):
        # print('------------------talk_walkers----------------------')
        talk_content = walker_name + ":" + content
        self.control_robot_action(0, 3, talk_content, scene_id)





if __name__ == '__main__':
    # Create an instance of the SceneManager class
    scene_manager = SceneManager()

    map_id = 11  # 地图编号

    scene_num = 1  # 场景数量

    print('------------ 初始化加载场景 ------------')
    scene_manager.Init()
    scene_manager.AcquireAvailableMaps()
    scene_manager.SetWorld(map_id, scene_num)
    time.sleep(5.0)

    for i in range(scene_num):
        print('------------ 场景操作 ------------')
        scene_manager.Observe(i)
        scene_manager.Reset(i)

    # Pass the scene_manager to the PedestrianController constructor
    pedestrian_controller = PedestrianController(scene_manager)
    # pedestrian_controller.add_one_pedestrian(0, 0, 0, 0)
    # result_scene = pedestrian_controller.control_one_pedestrian(0, 0,200, 180)
    pedestrian_data=[[0, -1200.420198059731, -500.6178305390472, 51.67637862904141], [1, -180.15647559396007, -250.03489222288317, 87.35462065866324], [2, 304.23662121767586, -891.6092498194478, 329.60193800181213], [3, -695.3583991207915, -771.7062866327284, 350.4718304807018], [4, 658.5813878624913, -938.6067864761408, 212.74588855465814], [5, 210.29150407593852, -291.81155229172873, 86.5104009495514], [6, -445.091329503715, -375.35292079394685, 96.0720471295291]]
    result_scene = pedestrian_controller.add_multiple_pedestrians(pedestrian_data, scene_id=0)
    print("Pedestrian Control result:", result_scene.info)
    walkers=pedestrian_controller.get_walkers()
    print(walkers)
    pedestrian_controller.talk_walkers(0, "您好，我想要一杯卡布奇诺", scene_id=0)

