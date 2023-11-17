# import os
# import sys
#
# sys.path.append('./')
# sys.path.append('../')
#
# def run_task(task_number):
#     if task_number == 1:
#         os.system("python task4_scene.py")  # 替换为你的任务1文件名或路径
#     elif task_number == 2:
#         sub_task = input("请选择任务2的子任务 (a/b): ")
#         if sub_task.lower() == 'a':
#             os.system("python task2_scene1.py")  # 替换为你的任务2场景一文件名或路径
#         elif sub_task.lower() == 'b':
#             os.system("python task2_scene2.py")  # 替换为你的任务2场景二文件名或路径
#         else:
#             print("无效的选择")
#     elif task_number == 3:
#         os.system("python task3_scene.py")  # 替换为你的任务3文件名或路径
#     elif task_number == 4:
#         os.system("python task4_scene.py")  # 替换为你的任务4文件名或路径
#     else:
#         print("无效的选择")
#
#
# print("选择要展示的任务:")
# print("1. 展示: 环境主动探索和记忆")
# print("2. 展示：视觉语言导航")
# print("3. 展示: 具身多轮对话")
# print("4. 展示: 视觉语言操作")
#
# selected_task = int(input("输入任务编号: "))
#
# run_task(selected_task)
