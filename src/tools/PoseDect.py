import numpy as np
import os  
import sys
from utils import extract_numbers, write_json, read_json
sys.path.append("src/models")
sys.path.append("src/tools")


def PoseDect(video_path, result_path):
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    orivi_name, start_frame = extract_numbers(video_name)
    print("video_name: "+video_name)
    print("orivi_name: "+orivi_name)

    # 读取球的json文件
    ball_save_dir= os.path.join(f"{result_path}/ball", f"event")
    ball_json_path=f"{ball_save_dir}/{orivi_name}/{video_name}.json"
    print("ball_json_path: "+ball_json_path)
    ball=read_json(ball_json_path)
    print("read ball: ")
    print(ball)

    # 读取球员的关节坐标文件
    player_save_dir= os.path.join(f"{result_path}/players", f"player_kp")
    player_json_path=f"{player_save_dir}/{orivi_name}.json"
    print("player_json_path: "+player_json_path)
    player=read_json(player_json_path)
    print("read player: ")
    print(player)

    player_top_pose=[]
    player_bottom_pose=[]
    # joint_names 列表
    joint_names = [
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle"
    ]

    # 索引
    left_wrist_index = joint_names.index("left_wrist")
    left_shoulder_index = joint_names.index("left_shoulder")
    left_elbow_index = joint_names.index("left_elbow")
    right_wrist_index = joint_names.index("right_wrist")
    right_shoulder_index = joint_names.index("right_shoulder")
    right_elbow_index = joint_names.index("right_elbow")

    # 击球帧
    hit_frames=[]

    # 遍历每一帧
    for frame_id, player_data in player.items():
        if frame_id in ball and ball[frame_id] == 1:  # 检查是否为击球帧
            print(f"Frame: {frame_id}")
            hit_frames.append(int(frame_id))
            # 获取 top 和 bottom 的点
            try:
                top_points = np.array(player_data['top'])  # 获取 'top' 的坐标点
                bottom_points = np.array(player_data['bottom'])  # 获取 'bottom' 的坐标点
                top_k = 0
                top_left_wrist_position=top_points[left_wrist_index]
                top_left_shoulder_position=top_points[left_shoulder_index]
                top_left_elbow_position=top_points[left_elbow_index]
                top_right_wrist_position=top_points[right_wrist_index]
                top_right_shoulder_position=top_points[right_shoulder_index]
                top_right_elbow_position=top_points[right_elbow_index]
                
                #两个手的点位分别高于两个手臂的点位
                print(top_left_wrist_position, top_right_wrist_position)
                print(top_left_elbow_position, top_right_elbow_position)
                if top_left_wrist_position[1] < top_left_elbow_position[1] and top_right_wrist_position[1] < top_right_elbow_position[1] :
                    print("top1")
                    top_k += 1 

                #两手距离大于肩宽，手臂张开
                print(top_left_shoulder_position, top_right_shoulder_position)
                print(top_left_wrist_position, top_right_wrist_position)
                if abs(top_left_shoulder_position[0]-top_right_shoulder_position[0]) < abs(top_left_wrist_position[0] - top_right_wrist_position[0]):
                    print("top2")
                    top_k += 1
                
                if top_k==2:
                    player_top_pose.append(1)
                else:
                    player_top_pose.append(0)

                bottom_k = 0
                bottom_left_wrist_position=bottom_points[left_wrist_index]
                bottom_left_shoulder_position=bottom_points[left_shoulder_index]
                bottom_left_elbow_position=bottom_points[left_elbow_index]
                bottom_right_wrist_position=bottom_points[right_wrist_index]
                bottom_right_shoulder_position=bottom_points[right_shoulder_index]
                bottom_right_elbow_position=bottom_points[right_elbow_index]
                
                #两个手的点位分别高于两个手臂的点位
                print(bottom_left_wrist_position, bottom_right_wrist_position)
                print(bottom_left_elbow_position, bottom_right_elbow_position)
                if bottom_left_wrist_position[1] < bottom_left_elbow_position[1] and bottom_right_wrist_position[1] < bottom_right_elbow_position[1] :
                    print("bottom1")
                    bottom_k += 1 

                #两手距离大于肩宽，手臂张开
                print(bottom_left_shoulder_position, bottom_right_shoulder_position)
                print(bottom_left_wrist_position, bottom_right_wrist_position)
                if abs(bottom_left_shoulder_position[0]-bottom_right_shoulder_position[0]) < abs(bottom_left_wrist_position[0] - bottom_right_wrist_position[0]):
                    print("bottom2")
                    bottom_k += 1
                
                if bottom_k==2:
                    player_bottom_pose.append(1)
                else:
                    player_bottom_pose.append(0)
            except KeyError as e:
                print(f"KeyError: {e} in frame {frame_id}")
            except Exception as e:
                print(f"Error: {e} in frame {frame_id}")
    print("------hit_frames:")
    print(hit_frames)
    print(player_top_pose)
    print(player_bottom_pose)
    # 将对应击球帧的姿势写入json文件
    pose_path = os.path.join(result_path, f"players/players_pose/{orivi_name}")
    os.makedirs(pose_path, exist_ok=True)
    print("dis_path: "+pose_path)
    cnt=0
    for frame_id, hit in ball.items():
        print("here is frame_id: "+str(frame_id))
        pose_dict={}
        if hit==1:
            print(cnt)
            print(player_top_pose[cnt])
            print(player_bottom_pose[cnt])
            pose_dict={f"{frame_id}":{"hit":1,"top":player_top_pose[cnt],"bottom":player_bottom_pose[cnt]}}
            cnt+=1
        else:
            pose_dict={f"{frame_id}":{"hit":0,"top":0,"bottom":0}}
        # print(pose_dict)
        write_json(pose_dict, video_name, f"{pose_path}")
    


# PoseDect(r'res/videos/h1/h1_120-335.mp4', r'res')
# PoseDect(r'res/videos/h1/h1_648-932.mp4', r'res')