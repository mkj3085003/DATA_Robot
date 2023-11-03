import GrabSim_pb2
import time

from SceneManager import SceneManager


class NavigationController:
    def __init__(self, scene_manager):
        # Use the scene manager's gRPC channel and client
        self.scene_manager = scene_manager

    def navigate_to(self, x, y, yaw,scene_id=0):
        # Get the current scene information from the scene manager
        scene = self.scene_manager.get_scene_info(scene_id)
        # Construct the navigation command
        navigation_command = [x, y, yaw]
        # Execute navigation
        action = GrabSim_pb2.Action(scene=scene_id, action=GrabSim_pb2.Action.ActionType.WalkTo,
                                    values=navigation_command)
        result_scene = self.scene_manager.sim_client.Do(action)
        # Return navigation result
        return result_scene
    def navigate_to_limit(self, x, y, yaw, velocity, distance_limit,scene_id=0):
        # Get the current scene information from the scene manager
        scene = self.scene_manager.get_scene_info(scene_id)
        # Construct the navigation command
        navigation_command = [x, y, yaw, velocity, distance_limit]
        # Execute navigation
        action = GrabSim_pb2.Action(scene=scene_id, action=GrabSim_pb2.Action.ActionType.WalkTo, values=navigation_command)
        result_scene = self.scene_manager.sim_client.Do(action)
        # Return navigation result
        return result_scene

if __name__ == '__main__':
    scene_manager = SceneManager()

    map_id = 3  # Map ID: 3 for the coffee shop
    scene_num = 1  # Number of scenes to load

    scene_manager.load_scene(map_id, scene_num)
    time.sleep(5)

    for i in range(scene_num):
        print(f"------------------ Scene {i} ----------------------")
        scene_manager.reset_scene(i)
        scene_info = scene_manager.get_scene_info(i)
        # print(scene_info)  # You can access various scene information from the 'scene_info' object

    navigator = NavigationController(scene_manager)

    target_x = 247  # Target x-coordinate
    target_y = 0  # Target y-coordinate

    yaw=30
    # Example navigation
    result_scene = navigator.navigate_to_limit(target_x, target_y,yaw,200,100)
    print("Navigation result:", result_scene.info)