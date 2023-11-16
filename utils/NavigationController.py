import GrabSim_pb2
import time


from .SceneManager import SceneManager



class NavigationController:
    def __init__(self, scene_manager):
        # Use the scene manager's gRPC channel and client
        self.scene_manager = scene_manager

    def navigate_to(self, x, y, yaw,scene_id=0):
        # Construct the navigation command
        navigation_command = [x, y, yaw]
        # Execute navigation
        action = GrabSim_pb2.Action(scene=scene_id, action=GrabSim_pb2.Action.ActionType.WalkTo,
                                    values=navigation_command)
        result_scene = self.scene_manager.sim_client.Do(action)
        # Return navigation result
        return result_scene

    def navigate_to_limit(self, x, y, yaw, velocity, distance_limit,scene_id=0):
        # Construct the navigation command
        navigation_command = [x, y, yaw, velocity, distance_limit]
        # Execute navigation
        action = GrabSim_pb2.Action(scene=scene_id, action=GrabSim_pb2.Action.ActionType.WalkTo, values=navigation_command)
        result_scene = self.scene_manager.sim_client.Do(action)
        # Return navigation result
        return result_scene

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

    navigator = NavigationController(scene_manager)

    target_x = 247  # Target x-coordinate
    target_y = 0  # Target y-coordinate

    yaw = 30
    # Example navigation
    result_scene = navigator.navigate_to_limit(target_x, target_y, yaw, 200, 100)
    print("Navigation result:", result_scene.info)