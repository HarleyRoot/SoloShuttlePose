import json
import os
import cv2


def extract_frames(input_video, output_video, start_end):
    # 打开输入视频
    cap = cv2.VideoCapture(input_video)

    # 获取视频的帧率
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 获取总帧数

    # 定义编码并创建VideoWriter对象
    # fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    out = cv2.VideoWriter(output_video, fourcc, int(fps / 1), (width, height))

    # 初始化帧计数器
    count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 增加帧计数器
        count += 1

        # 检查当前帧是否在所需范围内
        for start, end in start_end:
            if start <= count <= end:
                out.write(frame)
    # 完成后释放所有内容
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    return frame_count


def check_values_from_file(file_name):
    # Open the file and load the JSON data
    with open(file_name, "r") as file:
        data_dict = json.load(file)

    score = 0.0
    frame = ""
    # Iterate over the dictionary and check the values
    for s, f in data_dict.items():
        score = float(s)
        frame = f
    return score, frame


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
            subres_dir = res_dir + root[11:]
            if check_res_dir(subres_dir) == True:
                print(root[11:] + "已处理")
            else:
                print(root[11:] + "开始处理")
                score_frame = {}
                for f in files:
                    score, frame = check_values_from_file(root + "/" + f)
                    score_frame[score] = frame
                score_frame = dict(
                    sorted(score_frame.items(), key=lambda item: item[0], reverse=True)
                )
                video_number = max(int(len(score_frame) * 0.30), 1)
                count = 0
                start_end = []
                for score, frame in score_frame.items():
                    if count >= video_number:
                        break
                    count += 1
                    pos = frame.find("-")
                    start_end.append((int(frame[:pos]), int(frame[pos + 1 :])))

                input_video = "./videos/" + root[12:] + ".mp4"
                output_video = subres_dir + "/" + root[12:] + ".mp4"
                extract_frames(input_video, output_video, start_end) 
                print("处理完毕")


# 结果存放文件夹
res_dir = "./res/high_light"
check_res_dir(res_dir)

# 扫描来源文件夹
root_dir = "./res/score"
src_dir = scan_src_dir(root_dir, res_dir)
