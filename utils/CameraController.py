import time

import matplotlib.pyplot as plt
import numpy as np
import GrabSim_pb2
from utils.SceneManager import SceneManager

class CameraController:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager

    def capture_image(self, camera_name, scene_id=0):
        action = GrabSim_pb2.CameraList(cameras=[camera_name], scene=scene_id)
        img_data = self.scene_manager.sim_client.Capture(action)
        return img_data

    def show_image(self, img_data):
        im = img_data.images[0]
        d = np.frombuffer(im.data, dtype=im.dtype).reshape((im.height, im.width, im.channels))
      
        if 'depth' in im.name.lower():
            plt.imshow(d, cmap="gray",vmin=0,vmax=d.max())
            plt.colorbar()  # 添加颜色条
        else :
            plt.imshow(d)
        plt.show()

    def save_image(self, img_data):
        im = img_data.images[0]
        d = np.frombuffer(im.data, dtype=im.dtype).reshape((im.height, im.width, im.channels))
        if 'depth' in im.name.lower():
            plt.imshow(d, cmap="gray",vmin=0,vmax=600)
            plt.colorbar()  # 添加颜色条
        else :
            plt.imshow(d)
        plt.savefig(im.name+".png")

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

    camera_controller = CameraController(scene_manager)

    # 选择要测试的相机(也可以是一个列表，同时返回多个)
    # camera_name = GrabSim_pb2.CameraName.Head_Color
    # camera_name = GrabSim_pb2.CameraName.Head_Depth
    camera_name = GrabSim_pb2.CameraName.Head_Depth
    # 获取相机图像
    img_data = camera_controller.capture_image(camera_name)

    # 显示图像
    camera_controller.show_image(img_data)
