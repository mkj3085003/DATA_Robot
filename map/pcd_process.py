import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
import map.rotation_utils as ru


def show_pointcloud(color_raw,depth_raw,camera):
    # create an rgbd image object:
    color = o3d.geometry.Image((color_raw).astype(np.uint8))
    depth=o3d.geometry.Image((depth_raw).astype(np.float32))
    
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(color, depth,depth_scale=100.0,depth_trunc=10, convert_rgb_to_intensity=False)
    # use the rgbd image to create point cloud:

    intrinsic = o3d.camera.PinholeCameraIntrinsic(camera.w, camera.h, camera.fx,camera.fy, camera.cx, camera.cy)
    intrinsic.intrinsic_matrix = [[camera.fx, 0, camera.cx], [0, camera.fy, camera.cy], [0, 0, 1]]
    cam = o3d.camera.PinholeCameraParameters()
    cam.intrinsic = intrinsic
   
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, cam.intrinsic)
    pcd.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])

    # visualize:
    vis = o3d.visualization.Visualizer()
    vis.create_window(width=camera.w,height=camera.h)
    vis.add_geometry(pcd)
    
    ctr = vis.get_view_control()
    ctr.convert_from_pinhole_camera_parameters(cam)
    vis.run()


def get_point_cloud_of_view(color_raw,depth_raw,camera,downscal=5):
    color = o3d.geometry.Image((color_raw).astype(np.uint8))
    depth=o3d.geometry.Image((depth_raw).astype(np.float32))
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(color, depth,depth_scale=1.0,depth_trunc=600, convert_rgb_to_intensity=False)
    intrinsic = o3d.camera.PinholeCameraIntrinsic(camera.w, camera.h, camera.fx,camera.fy, camera.cx, camera.cy)
    intrinsic.intrinsic_matrix = [[camera.fx, 0, camera.cx], [0, camera.fy, camera.cy], [0, 0, 1]]
    cam = o3d.camera.PinholeCameraParameters()
    cam.intrinsic = intrinsic
    
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, cam.intrinsic)
    pcd=pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
 
    # 使用remove_radius_outlier进行滤波
    cl,idx = pcd.remove_radius_outlier(nb_points=5, radius=5)
    pcd=pcd.select_by_index(idx)
    
    return np.asarray(pcd.colors),np.asarray(pcd.points)

def get_point_cloud_of_view(color_raw,depth_raw,camera,downscal=5):
    color = o3d.geometry.Image((color_raw).astype(np.uint8))
    depth=o3d.geometry.Image((depth_raw).astype(np.float32))
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(color, depth,depth_scale=1.0,depth_trunc=600, convert_rgb_to_intensity=False)
    intrinsic = o3d.camera.PinholeCameraIntrinsic(camera.w, camera.h, camera.fx,camera.fy, camera.cx, camera.cy)
    intrinsic.intrinsic_matrix = [[camera.fx, 0, camera.cx], [0, camera.fy, camera.cy], [0, 0, 1]]
    cam = o3d.camera.PinholeCameraParameters()
    cam.intrinsic = intrinsic
    
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, cam.intrinsic)
    pcd=pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
 
    # 使用remove_radius_outlier进行滤波
    cl,idx = pcd.remove_radius_outlier(nb_points=5, radius=5)
    pcd=pcd.select_by_index(idx)
    
    return np.asarray(pcd.colors),np.asarray(pcd.points)

def get_point_cloud_of_view_and_remove(color_raw,depth_raw,camera,downscal=5):
    color = o3d.geometry.Image((color_raw).astype(np.uint8))
    depth=o3d.geometry.Image((depth_raw).astype(np.float32))
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(color, depth,depth_scale=1.0,depth_trunc=600, convert_rgb_to_intensity=False)
    intrinsic = o3d.camera.PinholeCameraIntrinsic(camera.w, camera.h, camera.fx,camera.fy, camera.cx, camera.cy)
    intrinsic.intrinsic_matrix = [[camera.fx, 0, camera.cx], [0, camera.fy, camera.cy], [0, 0, 1]]
    cam = o3d.camera.PinholeCameraParameters()
    cam.intrinsic = intrinsic
    
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, cam.intrinsic)
    pcd=pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
 
    # 使用remove_radius_outlier进行滤波

    cl,idx = pcd.remove_radius_outlier(nb_points=5, radius=5)
    pcd=pcd.select_by_index(idx)
    pcd=remove_pcd_by_id(pcd)
    return np.asarray(pcd.colors),np.asarray(pcd.points)



def viz_3d(point):
    # 可视化点云
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(point)
    coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=20.0, origin=[0, 0, 0])
    o3d.visualization.draw_geometries([point_cloud,coordinate_frame])

def viz_segment_3d(seg,point):
    
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(point)
    point_cloud.colors=o3d.utility.Vector3dVector(seg)
    coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=20.0, origin=[0, 0, 0])
    o3d.io.write_point_cloud("img/point_cloud_people.pcd", point_cloud)
    o3d.visualization.draw_geometries([point_cloud,coordinate_frame])
    


def seg_to_rgb(seg):
    rgb=np.repeat(seg, 3, axis=-1)
    rgb[:,:,1]=((rgb[:,:,0]%10)*139)%255
    rgb[:,:,2]=((rgb[:,:,0]%10)*297)%255
    return rgb



def display_inlier_outlier(cloud, ind):
    inlier_cloud = cloud.select_by_index(ind)
    outlier_cloud = cloud.select_by_index(ind, invert=True)
    # 选中的点为灰色，未选中点为红色
    outlier_cloud.paint_uniform_color([1, 0, 0])
    # 可视化
    o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud])


'''
从点云中提取语义id为target_id的部分
'''
def get_pcd_by_id(pcd,target_id=251):
    color=np.asarray(pcd.colors)
    
    idxs=np.where(color[:, 0]== target_id/255)[0]
    return pcd.select_by_index(idxs)

def remove_pcd_by_id(pcd,remove_list=[251,254,253]):# floor roof wall ginger
    idxs=[]
    # remove_r=[x / 255 for x in remove_list]
    color=np.asarray(pcd.colors)
    for id_ in remove_list:
        idxs.extend(np.where(color[:, 0] == id_/255)[0])
    return pcd.select_by_index(idxs, invert=True)




def cluster_and_get_center(pcd, eps, min_points,vis=False):
    # 使用DBSCAN进行点云密度聚类
    labels = np.array(pcd.cluster_dbscan(eps=eps, min_points=min_points, print_progress=False))

    # 获取聚类的数量
    if(len(labels)==0):
        return np.array([])
        
    num_clusters = labels.max() + 1
    
    if vis:
        # 可视化每个聚类
        colors = plt.cm.rainbow(np.linspace(0, 1, num_clusters))
        clu_list=[]
        for i in range(num_clusters):
            cluster_points = pcd.select_by_index(np.where(labels == i)[0].tolist())
            cluster_points.paint_uniform_color(colors[i][:3])
            clu_list.append(cluster_points)
        o3d.visualization.draw_geometries(clu_list)

    # 计算每个聚类的中心点
    centers = []
    for i in range(num_clusters):
        cluster_points = pcd.select_by_index(np.where(labels == i)[0].tolist())
        center = np.asarray(cluster_points.get_center())
        centers.append(center)
        # print(f"Cluster {i+1} Center: {center}")

    # 返回聚类中心点的数组
    return np.array(centers)






if __name__ == '__main__':
    # 读取点云数据
    pcd = o3d.io.read_point_cloud("../img/point_cloud_people.pcd")


    # 使用remove_radius_outlier进行滤波
    cl,idx = pcd.remove_radius_outlier(nb_points=5, radius=5)


    pcd=pcd.select_by_index(idx)

    pcd=get_pcd_by_id(pcd)
    o3d.visualization.draw_geometries([pcd])


    cluster_centers = cluster_and_get_center(pcd, eps=30, min_points=8,vis=True)
    print("Centers of Clusters:")
    print(cluster_centers)

    # # 可视化处理前后的点云
    # o3d.visualization.draw_geometries([pcd.select_by_index(idx)])