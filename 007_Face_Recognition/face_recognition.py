import cv2
import numpy as np

# Haar Cascadeの分類器をロード
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

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
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # 検出した顔を矩形で囲む
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # フレームを表示
    cv2.imshow('Face Recognition', frame)

    # 'q'キーで終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# リソースを解放
cap.release()
cv2.destroyAllWindows()