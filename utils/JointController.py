import GrabSim_pb2
import time


from .SceneManager import SceneManager


class JointController:
    def __init__(self, scene_manager):
        # 设置本地端口号，每次通信能够发送数据量大小和接受的数据量大小
        self.scene_manager = scene_manager

    '''
    关节控制
    1、0-3是躯干的4个关节
    2、4-6是脖子和头的3个关节
    3、7-13是左臂的7个关节
    4、14-20是右臂的7个关节
    5、每个关节都有不同的限位,参考限位图合理设置关节角度
    '''

    def rotate_joints(self, action_list,scene_id=0):
        print('------------------rotate_joints----------------------')

        for values in action_list:
            action = GrabSim_pb2.Action(scene=scene_id, action=GrabSim_pb2.Action.ActionType.RotateJoints,values=values)

            scene = self.scene_manager.sim_client.Do(action)

            for i in range(7, 21):  # arm
                print(
                    f"{scene.joints[i].name} angle:{scene.joints[i].angle} location:{scene.joints[i].location.X},{scene.joints[i].location.Y},{scene.joints[i].location.Z}"
                )
            for i in range(0, 10):  # hand
                print(
                    f"{scene.fingers[i].name} angle:{scene.fingers[i].angle} location:{scene.fingers[i].location[0].X},{scene.fingers[i].location[0].Y},{scene.fingers[i].location[0].Z}"
                )
            time.sleep(0.03)

    '''
    重置躯干和双臂关节
    '''
    def reset_joints(self, scene_id=0):
        print('------------------reset_joints----------------------')
        values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        action = GrabSim_pb2.Action(scene=scene_id, action=GrabSim_pb2.Action.ActionType.RotateJoints,values=values)

        scene = self.scene_manager.sim_client.Do(action)

        for i in range(7, 21):  # arm
            print(
                f"{scene.joints[i].name} angle:{scene.joints[i].angle} location:{scene.joints[i].location.X},{scene.joints[i].location.Y},{scene.joints[i].location.Z}"
            )
        for i in range(0, 10):  # hand
            print(
                f"{scene.fingers[i].name} angle:{scene.fingers[i].angle} location:{scene.fingers[i].location[0].X},{scene.fingers[i].location[0].Y},{scene.fingers[i].location[0].Z}"
            )

    '''
    手指控制
    1、0-4是左手指关节
    2、5-9是右手指关节
    3、10根手指的关节限位都是[-6,45]
    4、在抓取物品时,可以根据需要微调关节角度,避免穿模或者手指变形的情况
    finger_value= [-6, 0, 45, 45, 45, -6, 0, 45, 45, 45]
    '''
    def rotate_fingers(self,finger_value,scene_id=0):
        print('------------------rotate_fingers----------------------')

        action = GrabSim_pb2.Action(scene=scene_id, action=GrabSim_pb2.Action.ActionType.Finger, values=finger_value)
        scene = self.scene_manager.sim_client.Do(action)

        for i in range(7, 21):  # arm
            print(
                f"{scene.joints[i].name} angle:{scene.joints[i].angle} location:{scene.joints[i].location.X},{scene.joints[i].location.Y},{scene.joints[i].location.Z}"
            )
        for i in range(0, 10):  # hand
            print(
                f"{scene.fingers[i].name} angle:{scene.fingers[i].angle} location:{scene.fingers[i].location[0].X},{scene.fingers[i].location[0].Y},{scene.fingers[i].location[0].Z}"
            )

    '''
    重置手指关节
    '''

    def reset_fingers(self,scene_id=0):
        print('------------------reset_fingers----------------------')
        values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        action = GrabSim_pb2.Action(scene=scene_id, action=GrabSim_pb2.Action.ActionType.Finger, values=values)
        scene = self.scene_manager.sim_client.Do(action)

        for i in range(7, 21):  # arm
            print(
                f"{scene.joints[i].name} angle:{scene.joints[i].angle} location:{scene.joints[i].location.X},{scene.joints[i].location.Y},{scene.joints[i].location.Z}"
            )
        for i in range(0, 10):  # hand
            print(
                f"{scene.fingers[i].name} angle:{scene.fingers[i].angle} location:{scene.fingers[i].location[0].X},{scene.fingers[i].location[0].Y},{scene.fingers[i].location[0].Z}"
            )

    '''
    IK控制
    handNum=1是左手
    handNum=2是右手
    输入末端位置,IK控制胳膊移动到可达位置
    '''
    def ik_control_left_hand(self,x,y,z,roll = 0, pitch = 0, yaw = 0,scene_id=0):
        print('------------------ik_control_left_hand----------------------')
        # IK控制,左手
        HandPostureObject = [GrabSim_pb2.HandPostureInfos.HandPostureObject(handNum = 1, x = x, y = y, z = z, roll = roll, pitch = pitch, yaw = yaw)]
        self.scene_manager.sim_client.GetIKControlInfos(GrabSim_pb2.HandPostureInfos(scene=scene_id, handPostureObjects=HandPostureObject))

    def ik_control_right_hand(self,x,y,z,roll = 0, pitch = 0, yaw = 0,scene_id=0):
        print('------------------ik_control_right_hand----------------------')
        # IK控制,左手
        HandPostureObject = [GrabSim_pb2.HandPostureInfos.HandPostureObject(handNum = 1, x = x, y = y, z = z, roll = roll, pitch = pitch, yaw = yaw)]
        self.scene_manager.sim_client.GetIKControlInfos(GrabSim_pb2.HandPostureInfos(scene=scene_id, handPostureObjects=HandPostureObject))

    def ik_control_both_hands(self,hand_values,scene_id=0):
        print('------------------ik_control_both_hands----------------------')
        # IK控制,双手
        left_hand_values = hand_values[0]
        right_hand_values = hand_values[1]
        HandPostureObject = [
            GrabSim_pb2.HandPostureInfos.HandPostureObject(handNum=1, x=left_hand_values[0], y=left_hand_values[1], z=left_hand_values[2], roll=left_hand_values[3], pitch=left_hand_values[4], yaw=left_hand_values[5]),
            GrabSim_pb2.HandPostureInfos.HandPostureObject(handNum=2, x=right_hand_values[0], y=right_hand_values[1], z=right_hand_values[2], roll=right_hand_values[3], pitch=right_hand_values[4], yaw=right_hand_values[5])
        ]
        self.scene_manager.sim_client.GetIKControlInfos(GrabSim_pb2.HandPostureInfos(scene=scene_id, handPostureObjects=HandPostureObject))

# if __name__ == '__main__':
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
#         # print(scene_info)  # You can access various scene information from the 'scene_info' object
#
#     joint_controller = JointController(scene_manager)
#
#     #机器人的右手抬起张开
#     # joint_values = [[0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 36.0, -39.37, 37.2, -92.4, 4.13, -0.62, 0.4]]
#     # 机器人的右手抬起张开
#     # joint_values = [[0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 36.0, -39.62, 34.75, -94.80, 3.22, -0.26, 0.85]]
#     # 机器人的右手抬起张开
#     joint_values = [[0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 32.63, -32.80, 15.15, -110.70, 6.86, 2.36, 0.40]]
#     # joint_values = [[0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 28.18, -27.92, 6.75, -115.02, 9.46, 4.28, 1.35]]
#     # joint_values = [[0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 4.09, -13.15, -11.97, -107.35, 13.08, 8.58, 3.33]]
#     action_list = [[0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 36.0, -39.37, 37.2, -92.4, 4.13, -0.62, 0.4],
#                    [0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 36.0, -39.62, 34.75, -94.80, 3.22, -0.26, 0.85],
#                    [0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 32.63, -32.80, 15.15, -110.70, 6.86, 2.36, 0.40],
#                    [0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 28.18, -27.92, 6.75, -115.02, 9.46, 4.28, 1.35],
#                    [0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 4.09, -13.15, -11.97, -107.35, 13.08, 8.58,
#                     3.33]]
#
#     joint_controller.rotate_joints(joint_values)  # 关节控制测试


