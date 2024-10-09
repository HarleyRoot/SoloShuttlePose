# import torch
# import torchvision
# from tqdm import tqdm
import os
import sys
import numpy as np
# import cv2
# import numpy as np
# from pathlib import Path
# from argparse import ArgumentParser

sys.path.append("src/models")
sys.path.append("src/tools")

# from TrackNet import TrackNet
from utils import extract_numbers, write_json, read_json
# from denoise import smooth
# from event_detection import event_detect
# import logging
# import traceback

# # from yolov5 detect.py
# FILE = Path(__file__).resolve()
# ROOT = FILE.parents[0]  # YOLOv5 root directory
# if str(ROOT) not in sys.path:
#     sys.path.append(str(ROOT))  # add ROOT to PATH
# ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative


def PlayerDist(video_path, result_path): # ( ___.mp4, /res)

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

  # 计算球员重心
  # 初始化列表用于存储击球帧的坐标
  hit_player1_positions = []
  hit_player2_positions = []
  player1_length = []
  player2_length = []
  # joint_names 列表
  joint_names = [
      "nose", "left_eye", "right_eye", "left_ear", "right_ear",
      "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
      "left_wrist", "right_wrist", "left_hip", "right_hip",
      "left_knee", "right_knee", "left_ankle", "right_ankle"
  ]

  # left_knee 和 left_ankle 的索引
  left_knee_index = joint_names.index("left_knee")
  left_ankle_index = joint_names.index("left_ankle")

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

        # 计算重心：取 top 和 bottom 的平均值
        top_center = np.mean(top_points, axis=0)
        bottom_center = np.mean(bottom_points, axis=0)
        center_of_mass = (top_center + bottom_center) / 2
        hit_player1_positions.append(top_center)
        hit_player2_positions.append(bottom_center)

        # 输出每一帧的重心坐标
        print(f"Top Center: {top_center}, Bottom Center: {bottom_center}")

        # 确保获取左膝和左脚踝的坐标
        if len(top_points) > max(left_knee_index, left_ankle_index):
          left_knee_position1 = top_points[left_knee_index]
          left_ankle_position1 = top_points[left_ankle_index]
          leg_length1 = np.linalg.norm(left_knee_position1 - left_ankle_position1)  # 计算长度
          player1_length.append(leg_length1)

          print(
              f"Left Knee Position: {left_knee_position1}, Left Ankle Position: {left_ankle_position1}, Leg Length: {leg_length1}")
        else:
          print(f"Error: Bottom points array too short in frame {frame_id}")
        # 确保获取左膝和左脚踝的坐标
        if len(bottom_points) > max(left_knee_index, left_ankle_index):
          left_knee_position2 = bottom_points[left_knee_index]  # 从 bottom 中获取左膝的位置
          left_ankle_position2 = bottom_points[left_ankle_index]  # 从 bottom 中获取左脚踝的位置
          leg_length2 = np.linalg.norm(left_knee_position2 - left_ankle_position2)  # 计算长度
          player2_length.append(leg_length2)

          print(f"Left Knee Position: {left_knee_position2}, Left Ankle Position: {left_ankle_position2}, Leg Length: {leg_length2}")
        else:
          print(f"Error: Bottom points array too short in frame {frame_id}")
      except KeyError as e:
          print(f"KeyError: {e} in frame {frame_id}")
      except Exception as e:
          print(f"Error: {e} in frame {frame_id}")
  print("------hit_frames:")
  print(hit_frames)
  player_distance=[]

  # 计算并输出连续击球帧之间的距离
  for i in range(1, len(hit_player1_positions)):
    distance1 = np.linalg.norm(hit_player1_positions[i] - hit_player1_positions[i - 1])  # 欧几里得距离
    distance2 = np.linalg.norm(hit_player2_positions[i] - hit_player2_positions[i - 1])  # 欧几里得距离
    print(f"player1:Distance between hit frame {i - 1} and hit frame {hit_frames[i-1]}: {distance1}")
    print(f"player2:Distance between hit frame {i - 1} and hit frame {hit_frames[i-1]}: {distance2}")
    print("相对身位：")
    print(f"player1:Distance between hit frame {i - 1} and hit frame {hit_frames[i-1]}: {distance1/player1_length[i]}")
    print(f"player2:Distance between hit frame {i - 1} and hit frame {hit_frames[i-1]}: {distance2/player2_length[i]}")
    player_distance.append(distance1/player1_length[i])
    player_distance.append(distance2/player2_length[i])
  
  # 将对应击球帧的距离写入json文件

  dis_path = os.path.join(result_path, f"players/players_dis/{orivi_name}")
  os.makedirs(dis_path, exist_ok=True)
  print("dis_path: "+dis_path)
  cnt=0
  for i in range(len(ball.items())):
    print("here is i: "+str(i))
    distance_dict={}
    if i in hit_frames:
      if i == hit_frames[0]:
        distance_dict={f"{i}":{"hit":1,"top":0,"bottom":0}}
      else:
        distance_dict={f"{i}":{"hit":1,"top":player_distance[cnt*2],"bottom":player_distance[cnt*2+1]}}
        cnt+=1
    else:
      distance_dict={f"{i}":{"hit":0,"top":0,"bottom":0}}
    print(distance_dict)
    write_json(distance_dict, video_name, f"{dis_path}")




#
# PlayerDist(r'../../res/videos/44/44_0-171.mp4', r'../../res')