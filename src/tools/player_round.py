import json
import os


def check_values_from_file(file_name):
    round_log = {}
    # Open the file and load the JSON data
    with open(file_name, "r") as file:
        data_dict = json.load(file)

    frame_cnt = 0
    round_cnt = 0
    start_frame = -1
    end_frame = -1
    # Iterate over the dictionary and check the values
    for key, value in data_dict.items():
        if value == 0:
            frame_cnt += 1
        elif value == 1:
            if frame_cnt >= 100:
                round_log[str(start_frame) + "-" + str(end_frame)] = round_cnt
                round_cnt = 1
                start_frame = key
                end_frame = key
                continue

            round_cnt += 1
            frame_cnt = 0
            if start_frame == -1:
                start_frame = key
            end_frame = key
        else:
            continue
    if str(start_frame) + "-" + str(end_frame) not in round_log.keys():
        round_log[str(start_frame) + "-" + str(end_frame)] = round_cnt
    return round_log


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
            subres_dir = res_dir + root[16:]
            if check_res_dir(subres_dir) == True:
                print(root[17:] + "已处理")
            else:
                print(root[17:] + "开始处理")
                for f in files:
                    round_log = check_values_from_file(root + "/" + f)
                    with open(subres_dir + "/" + f, "w") as json_file:
                        json.dump(round_log, json_file)
                print("处理完毕")


# 结果存放文件夹
res_dir = "./res/players/players_round"
check_res_dir(res_dir)

# 扫描来源文件夹
root_dir = "./res/ball/event"
src_dir = scan_src_dir(root_dir, res_dir)
