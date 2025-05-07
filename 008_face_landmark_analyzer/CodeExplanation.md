# 顔ランドマーク解析プログラムの解説

このプログラムは、ノートパソコンのカメラを使用してリアルタイムで顔を検出し、顔のランドマーク（特徴点）を取得して描画するPythonアプリケーションです。`dlib`ライブラリを使用して顔のランドマークを取得し、OpenCVを使用して映像に描画します。また、特徴量を計算して映像上に表示します。

---

## 特徴
- ノートパソコンのカメラを使用してリアルタイムで顔を検出。
- 顔のランドマーク（68個の特徴点）を取得。
- ランドマークを映像に描画。
- 特徴量（目の距離、顔の幅、鼻の長さ）を計算して表示。
- ランドマークをグラフとしてプロット。

---

## コードの解説

### 1. 必要なライブラリのインポート
```python
import os
import cv2
import dlib
import numpy as np
import matplotlib.pyplot as plt
```
- **`os`**: ファイルの存在確認やパス操作に使用。
- **`cv2`**: OpenCVライブラリ。カメラ操作や画像処理に使用。
- **`dlib`**: 顔検出とランドマーク予測に使用。
- **`numpy`**: 数値データの操作に使用。
- **`matplotlib.pyplot`**: ランドマークをグラフとしてプロットするために使用。

---

### 2. モデルファイルのパス指定と存在確認
```python
model_path = "shape_predictor_68_face_landmarks.dat"
if not os.path.exists(model_path):
    print(f"モデルファイルが見つかりません: {model_path}")
    exit()
```
- **`model_path`**: 顔のランドマークを予測するためのモデルファイル（`shape_predictor_68_face_landmarks.dat`）のパスを指定。
- **`os.path.exists`**: モデルファイルが存在するか確認。存在しない場合はエラーメッセージを表示してプログラムを終了。

---

### 3. 顔検出器とランドマーク予測モデルのロード
```python
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(model_path)
```
- **`dlib.get_frontal_face_detector`**: 顔検出器を初期化。
- **`dlib.shape_predictor`**: ランドマーク予測モデルをロード。

---

### 4. カメラの起動
```python
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("カメラを開けませんでした。")
    exit()

print("カメラを起動しました。'q'キーを押して終了します。")
```
- **`cv2.VideoCapture(0)`**: ノートパソコンのカメラを起動。
- **`cap.isOpened()`**: カメラが正常に起動したか確認。起動できない場合はエラーメッセージを表示して終了。

---

### 5. 特徴量を計算する関数
```python
def calculate_distance(p1_tuple, p2_tuple):
    """2点間のユークリッド距離を計算 (タプル入力版)"""
    p1 = np.array(p1_tuple)
    p2 = np.array(p2_tuple)
    return np.linalg.norm(p1 - p2)
```
- **`calculate_distance`**: 2点間のユークリッド距離を計算する関数。特徴量の計算に使用。

---

### 6. メインループ
```python
while True:
    ret, frame = cap.read()
    if not ret:
        print("フレームを取得できませんでした。")
        break
```
- **`cap.read()`**: カメラからフレームを取得。
- **`ret`**: フレームが正常に取得できたかを示すフラグ。取得できない場合はループを終了。

---

### 7. グレースケール変換と顔の検出
```python
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
faces = detector(gray)
```
- **`cv2.cvtColor`**: フレームをグレースケールに変換。顔検出の精度を向上させるために使用。
- **`detector(gray)`**: グレースケール画像から顔を検出。検出された顔領域をリストとして返す。

---

### 8. ランドマークの取得と描画
```python
for face_idx, face in enumerate(faces):
    landmarks = predictor(gray, face)
    landmark_points = []
    for n in range(68):
        x = landmarks.part(n).x
        y = landmarks.part(n).y
        landmark_points.append((x, y))
        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
```
- **`predictor(gray, face)`**: 検出された顔領域に対して68個のランドマークを予測。
- **`landmarks.part(n)`**: 各ランドマークの座標を取得。
- **`cv2.circle`**: ランドマークを緑色の小さな円として描画。

---

### 9. 特徴量の計算と表示
```python
left_eye_outer = landmark_points[36]
right_eye_outer = landmark_points[45]
eye_distance = calculate_distance(left_eye_outer, right_eye_outer)

jaw_left = landmark_points[0]
jaw_right = landmark_points[16]
face_width = calculate_distance(jaw_left, jaw_right)

nose_bridge = landmark_points[27]
nose_tip = landmark_points[30]
nose_length = calculate_distance(nose_bridge, nose_tip)

feature_texts.append(f"Face {face_idx+1} EyeDist: {eye_distance:.2f}")
feature_texts.append(f"Face {face_idx+1} FaceWidth: {face_width:.2f}")
feature_texts.append(f"Face {face_idx+1} NoseLength: {nose_length:.2f}")
```
- **目の距離**: 左目外側（36番）と右目外側（45番）の距離を計算。
- **顔の幅**: 顎の左端（0番）と右端（16番）の距離を計算。
- **鼻の長さ**: 鼻梁上部（27番）と鼻先（30番）の距離を計算。
- **`cv2.putText`**: 計算した特徴量を映像上に描画。

---

### 10. Matplotlibによるグラフの更新
```python
ax.clear()
ax.scatter(landmark_array[:, 0], landmark_array[:, 1], c=[color], s=10)
fig.canvas.draw()
fig.canvas.flush_events()
```
- **`ax.clear()`**: 前のフレームのグラフをクリア。
- **`ax.scatter`**: ランドマークをグラフとしてプロット。
- **`fig.canvas.draw()`**: グラフを更新。

---

### 11. フレームの表示と終了条件
```python
cv2.imshow('Face Landmark Analyzer', frame)
if cv2.waitKey(1) & 0xFF == ord('q'):
    break
```
- **`cv2.imshow`**: ランドマークが描画されたフレームをウィンドウに表示。
- **`cv2.waitKey(1)`**: キーボード入力を待機。`q`キーが押された場合にループを終了。

---

### 12. リソースの解放
```python
cap.release()
cv2.destroyAllWindows()
plt.ioff()
```
- **`cap.release()`**: カメラリソースを解放。
- **`cv2.destroyAllWindows()`**: OpenCVで開いたすべてのウィンドウを閉じる。
- **`plt.ioff()`**: Matplotlibのインタラクティブモードをオフ。

---

## プログラムの流れ
1. 必要なライブラリをインポート。
2. モデルファイルをロードし、カメラを起動。
3. カメラからフレームを取得し、顔を検出。
4. 検出された顔に対してランドマークを予測し、描画。
5. 特徴量を計算して映像上に表示。
6. ランドマークをグラフとしてプロット。
7. `q`キーが押されるまでリアルタイムで処理を繰り返す。
8. 処理終了後、リソースを解放。

---

## 次のステップ
- ランドマークデータをCSVファイルに保存。
- 複数の顔を同時に処理。
- 個人認識のための特徴量分析や分類モデルの構築。