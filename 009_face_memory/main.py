import os
import cv2
import dlib
import numpy as np
import matplotlib.pyplot as plt
import sqlite3 # 追加
import json    # 追加
from datetime import datetime # 追加

# --- データベース関連の設定 ---
DB_NAME = "face_database.db"
active_person_id = None
active_person_name = "Unknown"

def init_db():
    """データベースとテーブルを初期化する"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # personsテーブル: 人物を登録
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS persons (
            person_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # face_featuresテーブル: 顔の特徴量を保存
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_features (
            feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER,
            landmarks_json TEXT,
            geometric_features_json TEXT,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (person_id) REFERENCES persons (person_id)
        )
    ''')
    conn.commit()
    conn.close()

def register_person_dialog():
    """新しい人物を登録するダイアログ（コンソール入力）"""
    global active_person_id, active_person_name
    name = input("登録する人物の名前を入力してください: ")
    if not name:
        print("名前が入力されませんでした。")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO persons (name) VALUES (?)", (name,))
        conn.commit()
        new_person_id = cursor.lastrowid
        active_person_id = new_person_id
        active_person_name = name
        print(f"人物 '{name}' (ID: {active_person_id}) を登録し、アクティブにしました。")
    except sqlite3.IntegrityError:
        print(f"エラー: 名前 '{name}' は既に登録されています。")
        # 既存の人物をアクティブにするか選択させることも可能
        cursor.execute("SELECT person_id FROM persons WHERE name = ?", (name,))
        result = cursor.fetchone()
        if result:
            active_person_id = result[0]
            active_person_name = name
            print(f"既存の人物 '{name}' (ID: {active_person_id}) をアクティブにしました。")
    except Exception as e:
        print(f"データベースエラー: {e}")
    finally:
        conn.close()

def save_face_features_to_db(landmarks_list, geo_features_dict):
    """顔の特徴量をデータベースに保存する"""
    global active_person_id
    if active_person_id is None:
        print("特徴量を保存するアクティブな人物が設定されていません。'r'キーで人物を登録/選択してください。")
        return False

    print(f"保存対象の人物ID: {active_person_id}, 名前: {active_person_name}")
    print(f"ランドマーク: {landmarks_list}")
    print(f"幾何学的特徴量: {geo_features_dict}")

    landmarks_json = json.dumps(landmarks_list)
    geometric_features_json = json.dumps(geo_features_dict)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO face_features (person_id, landmarks_json, geometric_features_json)
            VALUES (?, ?, ?)
        ''', (active_person_id, landmarks_json, geometric_features_json))
        conn.commit()
        print(f"特徴量を人物ID {active_person_id} ({active_person_name}) として保存しました。")
        return True
    except Exception as e:
        print(f"データベース保存エラー: {e}")
        return False
    finally:
        conn.close()

# --- メイン処理 ---
if __name__ == '__main__': # メインの処理を `if __name__ == '__main__':` ブロックに入れるのが一般的
    init_db() # データベース初期化

    # shape_predictor_68_face_landmarks.datのパスを指定
    model_path = "shape_predictor_68_face_landmarks.dat"
    if not os.path.exists(model_path):
        print(f"モデルファイルが見つかりません: {model_path}")
        exit()

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(model_path)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("カメラを開けませんでした。")
        exit()

    print("カメラを起動しました。'q':終了, 's':特徴量保存, 'r':人物登録/選択")
    print(f"現在のアクティブユーザー: {active_person_name} (ID: {active_person_id})")


    plt.ion()
    fig, ax = plt.subplots()

    def calculate_distance(p1_tuple, p2_tuple):
        p1 = np.array(p1_tuple)
        p2 = np.array(p2_tuple)
        return np.linalg.norm(p1 - p2)

    frame_message = "" # フレームに表示する一時的なメッセージ
    message_display_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("フレームを取得できませんでした。")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        ax.clear()
        ax.set_title("Face Landmarks")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

        # 画面上部に情報を表示
        info_text = f"Active User: {active_person_name} (ID: {active_person_id})"
        cv2.putText(frame, info_text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, "'q':Quit, 's':Save, 'r':Register", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)


        # 検出された各顔に対る処理
        for face_idx, face in enumerate(faces):
            cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), (0, 0, 255), 2) # 顔の矩形

            landmarks = predictor(gray, face)
            landmark_points = []
            for n in range(68):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                landmark_points.append((x, y))
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            landmark_array = np.array(landmark_points)
            color = plt.cm.viridis(face_idx / len(faces)) if len(faces) > 1 else 'blue'
            ax.scatter(landmark_array[:, 0], landmark_array[:, 1], c=[color], s=10)

            current_face_geometric_features = {} # この顔の幾何学的特徴量を格納
            if landmark_array.shape[0] == 68:
                left_eye_outer = landmark_points[36]
                right_eye_outer = landmark_points[45]
                eye_distance = calculate_distance(left_eye_outer, right_eye_outer)
                current_face_geometric_features["eye_distance"] = eye_distance

                jaw_left = landmark_points[0]
                jaw_right = landmark_points[16]
                face_width = calculate_distance(jaw_left, jaw_right)
                current_face_geometric_features["face_width"] = face_width

                nose_bridge = landmark_points[27]
                nose_tip = landmark_points[30]
                nose_length = calculate_distance(nose_bridge, nose_tip)
                current_face_geometric_features["nose_length"] = nose_length

                # 特徴量をOpenCVのフレームに描画 (顔ごとの情報を表示)
                cv2.putText(frame, f"Face {face_idx+1}", (face.left(), face.top() - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                text_y_offset = face.top()
                for i, (key, val) in enumerate(current_face_geometric_features.items()):
                    text_y_offset += 15
                    cv2.putText(frame, f"  {key.replace('_',' ')}: {val:.2f}", (face.left(), text_y_offset),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,255), 1)

            # 's'キーでの保存対象 (最初の顔のみを対象とする例)
            if face_idx == 0 and 'save_trigger' in locals() and save_trigger: # save_triggerはキー入力でTrueに
                if save_face_features_to_db(landmark_points, current_face_geometric_features):
                    frame_message = f"Saved for {active_person_name}"
                else:
                    frame_message = "Save failed. Register user ('r')."
                message_display_time = 30 # 30フレーム表示
                del save_trigger # トリガーを削除


        ax.set_ylim(frame.shape[0], 0)
        ax.set_xlim(0, frame.shape[1])
        ax.set_aspect('equal', adjustable='box')
        fig.canvas.draw()
        fig.canvas.flush_events()

        # 一時メッセージの表示
        if message_display_time > 0:
            cv2.putText(frame, frame_message, (10, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if "Saved" in frame_message else (0,0,255), 2)
            message_display_time -= 1


        cv2.imshow('Face Landmark Analyzer', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('s'):
            if faces: # 顔が検出されている場合のみ
                save_trigger = True # 次のループで最初の顔の情報を保存
                print("Save key pressed. Will attempt to save data for the first detected face.")
            else:
                frame_message = "No face detected to save."
                message_display_time = 30
                print("No face detected to save.")
        elif key == ord('r'):
            # MatplotlibウィンドウやOpenCVウィンドウがアクティブだとinputがうまく機能しないことがあるので注意
            # 一時的にカメラを止めるか、別スレッドでinputを扱うなどの工夫が必要な場合もある
            print("Register key pressed. Please input name in the console.")
            register_person_dialog()
            # 新しいユーザー情報を画面に反映させるために表示を更新
            print(f"Current active user: {active_person_name} (ID: {active_person_id})")


    cap.release()
    cv2.destroyAllWindows()
    plt.ioff()
    # plt.show()