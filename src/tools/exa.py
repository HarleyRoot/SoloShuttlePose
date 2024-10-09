import cv2

# 打开视频文件
video_path = r'D:\PycharmProjects\pythonProject1\SoloShuttlePose-main\videos\44.mp4'
cap = cv2.VideoCapture(video_path)

# 指定要跳转到的帧数
frame_number = 8

# 设置视频的当前帧
cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

# 读取跳转到的帧
ret, frame = cap.read()

if ret:
    cv2.imshow('Frame', frame)
    cv2.waitKey(0)  # 按任意键关闭窗口
else:
    print("无法读取帧")

# 释放视频捕获对象
cap.release()
cv2.destroyAllWindows()