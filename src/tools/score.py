import json
import os


def find_max_dis(json_folder_path):

    # 遍历文件夹中的所有 JSON 文件
    for json_file in os.listdir(json_folder_path):
        if json_file.endswith(".json"):
            file_path = os.path.join(json_folder_path, json_file)
            with open(file_path, "r") as f:
                data = json.load(f)

                # 遍历每个帧的距离值，找到最大的 `top` 和 `bottom` 距离
                for frame, values in data.items():
                    top_dis = values.get("top", 0)
                    bottom_dis = values.get("bottom", 0)

                    # 找到最大 `top` 值
                    if top_dis > max_top_dis:
                        max_top_dis = top_dis
                        max_top_frame = frame

                    # 找到最大 `bottom` 值
                    if bottom_dis > max_bottom_dis:
                        max_bottom_dis = bottom_dis
                        max_bottom_frame = frame

    return max_top_dis, max_top_frame, max_bottom_dis, max_bottom_frame


def find_max_json(file_name):
    max_top_dis = 0
    max_bottom_dis = 0
    Max_dis = 0
    score = 30
    max_top_frame = None
    max_bottom_frame = None
    # Open the file and load the JSON data
    with open(file_name, "r") as file:
        data_dict = json.load(file)
        # 遍历每个帧的距离值，找到最大的 `top` 和 `bottom` 距离
        for frame, values in data_dict.items():
            top_dis = values.get("top", 0)
            bottom_dis = values.get("bottom", 0)

            # 找到最大 `top` 值
            if top_dis > max_top_dis:
                max_top_dis = top_dis
                max_top_frame = frame

            # 找到最大 `bottom` 值
            if bottom_dis > max_bottom_dis:
                max_bottom_dis = bottom_dis
                max_bottom_frame = frame
        Max_dis = max(max_top_dis, max_bottom_dis)
        score *= Max_dis

    return score


# 检查是否已经建立过文件夹
def check_res_dir(res_dir):
    # Check if the directory exists
    if not os.path.exists(res_dir):
        # Create the directory if it does not exist
        os.makedirs(res_dir)
        return False
    else:
        return True


def scan_src_dir(root_dir, res_dir):
    for root, dir, files in os.walk(root_dir):
        if len([f for f in files if f.endswith(".json")]) > 0:
            subres_dir = res_dir + root[25:]
            if check_res_dir(subres_dir) == True:
                print(root[13:] + "已处理")
            else:
                print(root[13:] + "开始处理")
                for f in files:
                    dis_score = find_max_json(root + "/" + f)
                    with open(root[:22] + "round" + root[25:] + "/" + f, "r") as file:
                        data_round = json.load(file)
                    file.close()
                    round_score = 0
                    round_frame = "null"
                    for frame, values in data_round.items():
                        if values >= round_score:
                            round_frame = frame
                            round_score = values
                    score_frame = {}
                    score_frame[float(dis_score + round_score)] = round_frame
                    with open(subres_dir + "/" + f, "w") as json_file:
                        json.dump(score_frame, json_file)
                print("处理完毕")


# 结果存放文件夹
res_dir = "./res/score"
check_res_dir(res_dir)

# 扫描来源文件夹
root_dir = "./res/players/players_dis"
src_dir = scan_src_dir(root_dir, res_dir)
