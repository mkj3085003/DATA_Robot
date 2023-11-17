import DATA_Robot.utils
from DATA_Robot.utils.JointController import JointController
from DATA_Robot.utils.NavigationController import NavigationController
from DATA_Robot.utils.CameraController import CameraController
import GrabSim_pb2
import cv2
import numpy as np
from DATA_Robot.VLM_container.sobel_number_detect import ReadNumber
import time

class Conditioner():
    def __init__(self, scene_manager) -> None:
        self.work_state = False
        self.temperature = 25
        # 开关\加\减、111
        # 原来的
        self.key = [(300.00, -142.4999, 109.0), (300.00, -139.999, 109.0), (300.00, -137.0, 109.0)]
        self.delta_collision = 0.3
        self.scene_manager=scene_manager
        self.joint = JointController(self.scene_manager)
        self.nav = NavigationController(self.scene_manager)
        self.nav_threshhold = 3

    def get_temp_vision(self):
        camera = CameraController(self.scene_manager)
        cam_data = camera.capture_image(GrabSim_pb2.CameraName.Chest_Color)
        # camera.show_image(cam_data)

        img_data = cam_data.images[0]
        np_img = np.frombuffer(img_data.data, dtype=img_data.dtype).reshape(
            (img_data.height, img_data.width, img_data.channels))
        """cv数字识别"""
        numreader = ReadNumber()
        numreader.get_template()
        numreader.preprocess_image(np_img)
        num_see = numreader.detect_digits()
        if num_see:
            self.temperature = num_see
            print("----I see air condition 's temprature: ", self.temperature, "℃ ----")
            return self.temperature

    def press_buttom(self, key_id):
        # 按上开关
        # print(f"按下按键{key_id}开始")
        self.joint.reset_joints()
        x, y, z = self.key[key_id]
        """都用左手"""
        finger_value = [-6, 0, 45, 45, 45, 0, 0, 0, 0, 0]
        self.joint.rotate_fingers(finger_value)
        self.joint.ik_control_left_hand(x, y, z + self.delta_collision)
        time.sleep(3.0)
        """左边2个用左手,右边用右手"""
        # 收回手臂防止二次触碰
        """都用左手"""
        self.joint.ik_control_left_hand( \
            x, y, z - 2 * self.delta_collision)
        time.sleep(3.0)

        # print(f"按下按键{key_id}结束")
        self.joint.reset_joints()
        time.sleep(3)
        return True

    def turn_on_container(self):
        # 按上开关
        if self.work_state == False:
            if self.press_buttom(0):
                self.work_state = True
            self.get_temp_vision()
            print(f"####打开空调,温度为{self.temperature}℃")
        else:
            print("####空调已经为开启状态")
        return True

    def turn_off_container(self):
        # 按上开关
        if self.work_state == True:
            if self.press_buttom(0):
                self.work_state = True
            print("####空调为打开状态，现已关闭")
        else:
            print("####空调已经为关闭状态")
        return True

    def Turn_up_temperature(self, temp=1):
        # 调高温度
        print("--------------调高温度开始执行--------------")
        for i in range(temp):
            self.turn_on_container()
            self.press_buttom(1)
        # joint.reset_joints()
        print(f"-------------调高温度{temp}℃-------------")
        self.temperature += temp
        return True
        # 可以加视觉数字检测判断温度

    def Turn_down_temperature(self, temp=1):
        # 降低温度
        print("--------------降低温度开始执行--------------")
        for i in range(temp):
            self.turn_on_container()
            self.press_buttom(2)
        # joint.reset_joints()
        print(f"-------------降低温度{temp}℃-------------")
        self.temperature -= temp
        return True
        # 可以加视觉数字检测判断温度

    def set_temperature(self, temp):
        if temp < self.temperature:
            print("----I think temperature now is", self.temperature)
            while self.temperature != temp:
                # 通过视觉反馈调整
                # delta=self.get_temp_vision()-temp
                delta = self.temperature - temp
                self.Turn_down_temperature(delta)
                self.joint.reset_joints()
                time.sleep(3)
                self.get_temp_vision()

        elif temp > self.temperature:
            print("----I think temperature now is", self.temperature, " ----")
            while self.temperature != temp:
                delta = temp - self.temperature
                self.Turn_up_temperature(delta)
                self.joint.reset_joints()
                time.sleep(3)
                self.get_temp_vision()
        else:
            print(f"####already in {temp} ℃")