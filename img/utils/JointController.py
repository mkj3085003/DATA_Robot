import GrabSim_pb2
import time

from utils.SceneManager import SceneManager

class JointController:
    def __init__(self, scene_manager):
        # 设置本地端口号，每次通信能够发送数据量大小和接受的数据量大小
        self.scene_manager = scene_manager

    def rotate_joints(self, joint_values, scene_id=0):
        # 遍历关节值列表joint_values中的每一个值
        for value in joint_values:
            # 组装一个活动Action对象，包括（场景id，行动类型是旋转关节，旋转数值是value）
            action = GrabSim_pb2.Action(scene=scene_id, action=GrabSim_pb2.Action.ActionType.RotateJoints, values=value)

            # 调用本地python仿真器对象sim_client的Do方法，向UE端传入每一个行动action对象
            scene = self.scene_manager.sim_client.Do(action)
            "用于关节信息的打印，可以注释掉"
            for i in range(8, 21):  # arm
                print(
                    # 打印与胳膊相关的8-21个关节的，关节名称， 关节角度，                        关节坐标x，                      关节坐标y                   关节坐标z(距离地面高度)
                    f"{scene.joints[i].name}:{scene.joints[i].angle} location:{scene.joints[i].location.X},{scene.joints[i].location.Y},{scene.joints[i].location.Z}"
                )
            print('')
            for i in range(5, 10):  # Right hand
                print(
                    # 打印与右手相关的    手指名称                      手指角度                          手指坐标x                  手指坐标y                          手指坐标z(距离地面高度)
                    f"{scene.fingers[i].name} angle:{scene.fingers[i].angle} location:{scene.fingers[i].location[0].X},{scene.fingers[i].location[0].Y},{scene.fingers[i].location[0].Z}"
                )
            print('----------------------------------------')
            time.sleep(0.03)

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

    joint_controller = JointController(scene_manager)

    #机器人的右手抬起张开
    # joint_values = [[0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 36.0, -39.37, 37.2, -92.4, 4.13, -0.62, 0.4]]
    # 机器人的右手抬起张开
    # joint_values = [[0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 36.0, -39.62, 34.75, -94.80, 3.22, -0.26, 0.85]]
    # 机器人的右手抬起张开
    joint_values = [[0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 32.63, -32.80, 15.15, -110.70, 6.86, 2.36, 0.40]]
    # joint_values = [[0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 28.18, -27.92, 6.75, -115.02, 9.46, 4.28, 1.35]]
    # joint_values = [[0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 4.09, -13.15, -11.97, -107.35, 13.08, 8.58, 3.33]]


    joint_controller.rotate_joints(joint_values)  # 关节控制测试


