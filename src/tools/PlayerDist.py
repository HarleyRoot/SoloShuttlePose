import os
import sys
import numpy as np

sys.path.append("src/models")
sys.path.append("src/tools")

from utils import extract_numbers, write_json, read_json
import json

class PlayerAnalysis:
    def __init__(self):
        # Define joint pair constants for measurements
        self.HEIGHT_PAIRS = [
            (0, 16),  # nose to right ankle
            (0, 15),  # nose to left ankle
            (5, 15),  # left shoulder to left ankle
            (6, 16)   # right shoulder to right ankle
        ]
        self.WIDTH_PAIRS = [
            (5, 6),   # shoulder width
            (11, 12), # hip width
            (13, 14), # knee width
            (15, 16)  # ankle width
        ]
        self.TORSO_PAIRS = [
            (5, 11),  # left shoulder to left hip
            (6, 12)   # right shoulder to right hip
        ]
    
    def calculate_segment_length(self, keypoints, start_idx, end_idx):
        """计算两个关键点之间的距离"""
        if keypoints[start_idx] is None or keypoints[end_idx] is None:
            return 0
        return np.linalg.norm(keypoints[start_idx] - keypoints[end_idx])

    def estimate_body_scale(self, keypoints):
        """
        估算身体的高度、宽度和躯干长度
        参数:
        keypoints: numpy.ndarray, 形状为(17, 2)的关键点坐标数组
        返回:
        tuple: (height, width, torso_length) 估计的身高、体宽和躯干长度
        """
        # 计算多个高度估计值
        heights = [self.calculate_segment_length(keypoints, start, end) 
                  for start, end in self.HEIGHT_PAIRS]
        heights = [h for h in heights if h > 0]

        # 计算多个宽度估计值
        widths = [self.calculate_segment_length(keypoints, start, end) 
                 for start, end in self.WIDTH_PAIRS]
        widths = [w for w in widths if w > 0]

        # 计算躯干长度
        torso_lengths = [self.calculate_segment_length(keypoints, start, end) 
                        for start, end in self.TORSO_PAIRS]
        torso_lengths = [t for t in torso_lengths if t > 0]

        # 使用中位数作为最终估计值，提高鲁棒性
        height = np.median(heights) if heights else 0
        width = np.median(widths) if widths else 0
        torso_length = np.median(torso_lengths) if torso_lengths else 0

        return height, width, torso_length

    def estimate_scale_factor(self, keypoints, reference_height=None):
        """
        估算当前帧相对于参考高度的缩放因子
        参数:
        keypoints: numpy.ndarray, 形状为(17, 2)的关键点坐标数组
        reference_height: float, 可选的参考身高
        返回:
        float: 缩放因子
        """
        current_height, _, _ = self.estimate_body_scale(keypoints)
        if reference_height is None or current_height == 0:
            return 1.0
        return reference_height / current_height

def write_json_new(frames_data, filename, save_dir):
    """
    写入JSON文件，如果文件已存在则覆盖
    参数:
    frames_data: 所有帧的数据字典
    filename: 文件名
    save_dir: 保存目录
    """
    # 确保目录存在
    os.makedirs(save_dir, exist_ok=True)
    
    # 构建完整的文件路径
    file_path = os.path.join(save_dir, f"{filename}.json")
    
    # 如果文件已存在，则删除
    if os.path.exists(file_path):
        os.remove(file_path)
        
    # 写入所有数据
    with open(file_path, 'w') as f:
        json.dump(frames_data, f)

def PlayerDist(video_path, result_path):
    player_analysis = PlayerAnalysis()
    
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    orivi_name, start_frame = extract_numbers(video_name)
    print("video_name: " + video_name)
    print("orivi_name: " + orivi_name)

    # 读取球的json文件
    ball_save_dir = os.path.join(f"{result_path}/ball", f"event")
    ball_json_path = f"{ball_save_dir}/{orivi_name}/{video_name}.json"
    print("ball_json_path: " + ball_json_path)
    ball = read_json(ball_json_path)
    print("read ball: ")
    print(ball)

    # 读取球员的关节坐标文件
    player_save_dir = os.path.join(f"{result_path}/players", f"player_kp")
    player_json_path = f"{player_save_dir}/{orivi_name}.json"
    print("player_json_path: " + player_json_path)
    player = read_json(player_json_path)
    print("read player: ")
    print(player)

    # 初始化列表
    hit_player1_positions = []
    hit_player2_positions = []
    player1_scales = []
    player2_scales = []
    hit_frames = []

    # joint_names 列表
    joint_names = [
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle"
    ]

    # 遍历每一帧
    for frame_id, player_data in player.items():
        if frame_id in ball and ball[frame_id] == 1:  # 检查是否为击球帧
            print(f"Frame: {frame_id}")
            hit_frames.append(int(frame_id))
            
            try:
                top_points = np.array(player_data['top'])
                bottom_points = np.array(player_data['bottom'])

                # 计算重心和身体比例
                top_center = np.mean(top_points, axis=0)
                bottom_center = np.mean(bottom_points, axis=0)
                
                # 估算两个球员的身体比例
                top_height, _, _ = player_analysis.estimate_body_scale(top_points)
                bottom_height, _, _ = player_analysis.estimate_body_scale(bottom_points)
                
                hit_player1_positions.append(top_center)
                hit_player2_positions.append(bottom_center)
                player1_scales.append(top_height)
                player2_scales.append(bottom_height)

                print(f"Top Center: {top_center}, Bottom Center: {bottom_center}")
                print(f"Top Height: {top_height}, Bottom Height: {bottom_height}")
                
            except KeyError as e:
                print(f"KeyError: {e} in frame {frame_id}")
            except Exception as e:
                print(f"Error: {e} in frame {frame_id}")

    print("------hit_frames:")
    print(hit_frames)
    player_distance = []

    # 计算并输出连续击球帧之间的距离，使用身体比例进行归一化
    for i in range(1, len(hit_player1_positions)):
        # 计算原始距离
        distance1 = np.linalg.norm(hit_player1_positions[i] - hit_player1_positions[i - 1])
        distance2 = np.linalg.norm(hit_player2_positions[i] - hit_player2_positions[i - 1])
        
        # 使用身体比例进行归一化
        normalized_distance1 = distance1 / player1_scales[i] if player1_scales[i] > 0 else distance1
        normalized_distance2 = distance2 / player2_scales[i] if player2_scales[i] > 0 else distance2
        
        print(f"player1: Normalized distance between frames {hit_frames[i-1]} and {hit_frames[i]}: {normalized_distance1}")
        print(f"player2: Normalized distance between frames {hit_frames[i-1]} and {hit_frames[i]}: {normalized_distance2}")
        
        player_distance.append(normalized_distance1)
        player_distance.append(normalized_distance2)

    # 将对应击球帧的距离写入json文件
    dis_path = os.path.join(result_path, f"players/players_dis/{orivi_name}")
    os.makedirs(dis_path, exist_ok=True)
    print("dis_path: " + dis_path)
    
    # 收集所有帧的数据
    all_frames_data = {}
    cnt = 0
    for frame_id, hit in ball.items():
        print("here is frame_id: " + str(frame_id))
        if int(frame_id) in hit_frames:
            if int(frame_id) == hit_frames[0]:
                all_frames_data[frame_id] = {"hit": 1, "top": 0, "bottom": 0}
            else:
                all_frames_data[frame_id] = {
                    "hit": 1,
                    "top": player_distance[cnt*2],
                    "bottom": player_distance[cnt*2+1]
                }
                cnt += 1
        else:
            all_frames_data[frame_id] = {"hit": 0, "top": 0, "bottom": 0}
        print(all_frames_data[frame_id])
    
    # 一次性写入所有数据
    write_json_new(all_frames_data, video_name, dis_path)
    
PlayerDist(r'res/videos/h1/h1_120-335.mp4', r'res')