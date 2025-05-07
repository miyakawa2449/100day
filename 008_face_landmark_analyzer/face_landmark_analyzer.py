import os
import cv2
import dlib
import numpy as np
import matplotlib.pyplot as plt

# shape_predictor_68_face_landmarks.datのパスを指定
model_path = "shape_predictor_68_face_landmarks.dat"
if not os.path.exists(model_path):
    print(f"モデルファイルが見つかりません: {model_path}")
    exit()

# dlibの顔検出器とランドマーク予測モデルをロード
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(model_path)

# ノートパソコンのカメラを起動
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("カメラを開けませんでした。")
    exit()

print("カメラを起動しました。'q'キーを押して終了します。")

while True:
    # カメラからフレームを取得
    ret, frame = cap.read()
    if not ret:
        print("フレームを取得できませんでした。")
        break

    # グレースケールに変換
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 顔を検出
    faces = detector(gray)

    for face in faces:
        # 顔のランドマークを取得
        landmarks = predictor(gray, face)

        # ランドマークを数値化してリストに格納
        landmark_points = []
        for n in range(68):  # 68個のランドマーク
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            landmark_points.append((x, y))
            # ランドマークを描画
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        # ランドマークをNumPy配列に変換
        landmark_array = np.array(landmark_points)

        # ランドマークをプロット（例: グラフ表示）
        plt.scatter(landmark_array[:, 0], -landmark_array[:, 1], c='blue', s=10)
        plt.title("Face Landmarks")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.show()

    # フレームを表示
    cv2.imshow('Face Landmark Analyzer', frame)

    # 'q'キーで終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# リソースを解放
cap.release()
cv2.destroyAllWindows()