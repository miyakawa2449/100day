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

# Matplotlibをインタラクティブモードに設定
plt.ion()
fig, ax = plt.subplots() # FigureとAxesオブジェクトを一度だけ作成
scatter = None # 散布図オブジェクトを保持する変数

# 特徴量を計算する関数の例 (前回提案したもの)
def calculate_distance(p1_tuple, p2_tuple):
    """2点間のユークリッド距離を計算 (タプル入力版)"""
    p1 = np.array(p1_tuple)
    p2 = np.array(p2_tuple)
    return np.linalg.norm(p1 - p2)


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

    # グラフ表示のために現在のフレームの情報をクリア
    ax.clear()
    ax.set_title("Face Landmarks")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    # Y軸の向きを画像座標系に合わせる（任意）
    # ax.invert_yaxis() # Matplotlibのデフォルトは下から上なので、画像と合わせる場合は反転

    # 特徴量テキスト表示用のリスト
    feature_texts = []

    for face_idx, face in enumerate(faces):
        # 顔のランドマークを取得
        landmarks = predictor(gray, face)

        landmark_points = []
        for n in range(68):  # 68個のランドマーク
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            landmark_points.append((x, y))
            # ランドマークをカメラフレームに描画
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        landmark_array = np.array(landmark_points)

        # ランドマークをMatplotlibのグラフにプロット
        # 顔ごとに色を変える場合 (オプション)
        color = plt.cm.viridis(face_idx / len(faces)) if len(faces) > 0 else 'blue'
        ax.scatter(landmark_array[:, 0], landmark_array[:, 1], c=[color], s=10) # Y軸の向きはax.invert_yaxis()で調整

        # --- ここから特徴量の計算と表示の例 ---
        if landmark_array.shape[0] == 68: # 68点全て取得できた場合
            # 1. 目と目の間の距離 (ランドマークのインデックスは0始まり)
            # 左目外側: 36, 右目外側: 45
            left_eye_outer = landmark_points[36]
            right_eye_outer = landmark_points[45]
            eye_distance = calculate_distance(left_eye_outer, right_eye_outer)
            feature_texts.append(f"Face {face_idx+1} EyeDist: {eye_distance:.2f}")

            # 2. 顔の幅 (顎の0番と16番)
            jaw_left = landmark_points[0]
            jaw_right = landmark_points[16]
            face_width = calculate_distance(jaw_left, jaw_right)
            feature_texts.append(f"Face {face_idx+1} FaceWidth: {face_width:.2f}")

            # 3. 鼻の長さ (鼻梁上部27番と鼻先30番)
            nose_bridge = landmark_points[27]
            nose_tip = landmark_points[30]
            nose_length = calculate_distance(nose_bridge, nose_tip)
            feature_texts.append(f"Face {face_idx+1} NoseLength: {nose_length:.2f}")

            # 特徴量をOpenCVのフレームに描画
            cv2.putText(frame, f"Face {face_idx+1}", (face.left(), face.top() - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            for i, text in enumerate(feature_texts[-3:]): # 直近3つの特徴量を表示
                 cv2.putText(frame, text.split(' ')[-1], (face.left(), face.top() + (i+1)*15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,255), 1)


    # Matplotlibのグラフを更新
    # Y軸の範囲を画像の高さに基づいて設定すると見やすくなることがある
    ax.set_ylim(frame.shape[0], 0) # Y軸の上限をフレームの高さ、下限を0 (画像座標系のように)
    ax.set_xlim(0, frame.shape[1]) # X軸の範囲をフレームの幅に
    ax.set_aspect('equal', adjustable='box') # アスペクト比を保持

    fig.canvas.draw()
    fig.canvas.flush_events()

    # フレームを表示
    cv2.imshow('Face Landmark Analyzer', frame)

    # 'q'キーで終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# リソースを解放
cap.release()
cv2.destroyAllWindows()
plt.ioff() # インタラクティブモードをオフ
# plt.show() # スクリプト終了時に最終的なグラフを表示したい場合はコメントアウトを外す