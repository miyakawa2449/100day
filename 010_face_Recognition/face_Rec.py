import os
import cv2
import dlib
import numpy as np
import matplotlib.pyplot as plt # 認識時には必須ではないが、残しておいてもOK
import sqlite3
import json
from datetime import datetime

# --- データベース関連の設定 ---
DB_NAME = "face_database.db"
active_person_id = None # 人物登録時に使用
active_person_name = "Unknown" # 人物登録時に使用

# --- 顔認識関連のグローバル変数 ---
known_face_data = {}  # {person_id: {"name": "Name", "avg_features": np.array([...])}}
RECOGNITION_THRESHOLD = 15.0 # 認識の閾値（要調整）

def init_db():
    # (昨日と同じなので省略)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS persons (
            person_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
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
    # (昨日と同じなので省略)
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
        load_known_faces_from_db() # 新規登録後、認識データを再読み込み
    except sqlite3.IntegrityError:
        print(f"エラー: 名前 '{name}' は既に登録されています。")
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
    # (昨日と同じなので省略、ただし成功時に認識データ再読み込みを追加しても良い)
    global active_person_id
    if active_person_id is None:
        print("特徴量を保存するアクティブな人物が設定されていません。'r'キーで人物を登録/選択してください。")
        return False

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
        load_known_faces_from_db() # データ保存後、認識データを再読み込み
        return True
    except Exception as e:
        print(f"データベース保存エラー: {e}")
        return False
    finally:
        conn.close()


def load_known_faces_from_db():
    """データベースから登録済みの顔特徴量を読み込み、平均特徴量を計算する"""
    global known_face_data
    known_face_data = {} # 初期化
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        # personsテーブルからIDと名前を取得
        persons = {}
        cursor.execute("SELECT person_id, name FROM persons")
        for row in cursor.fetchall():
            persons[row[0]] = row[1]

        # face_featuresテーブルから特徴量を取得
        temp_features = {} # {person_id: [ [feat_vec1], [feat_vec2], ... ]}
        cursor.execute("SELECT person_id, geometric_features_json FROM face_features")
        for row in cursor.fetchall():
            person_id = row[0]
            if person_id not in temp_features:
                temp_features[person_id] = []
            
            try:
                geo_features = json.loads(row[1])
                # 特徴量ベクトルを固定順序で作成 (例: eye_dist, face_width, nose_length)
                # この順序は計算時と合わせる必要がある
                feature_vector = np.array([
                    geo_features.get("eye_distance", 0),
                    geo_features.get("face_width", 0),
                    geo_features.get("nose_length", 0)
                ])
                temp_features[person_id].append(feature_vector)
            except json.JSONDecodeError:
                print(f"警告: person_id {person_id} の特徴量JSONのパースに失敗しました。")
            except Exception as e:
                print(f"警告: 特徴量ベクトルの作成中にエラー: {e}")


        # 各人物の平均特徴量ベクトルを計算
        for person_id, feature_vectors in temp_features.items():
            if person_id in persons and len(feature_vectors) > 0:
                avg_feature_vector = np.mean(feature_vectors, axis=0)
                known_face_data[person_id] = {
                    "name": persons[person_id],
                    "avg_features": avg_feature_vector
                }
        print(f"登録済み人物の特徴量をロードしました。{len(known_face_data)} 人分。")
        # print(known_face_data) # デバッグ用

    except Exception as e:
        print(f"データベースからの特徴量読み込みエラー: {e}")
    finally:
        conn.close()

def recognize_face(current_features_vector):
    """現在の顔の特徴量と登録済みの顔を比較して名前を返す"""
    if not known_face_data:
        return "Unknown", 0.0 # 比較対象がなければ不明

    min_distance = float('inf')
    recognized_person_id = None

    for person_id, data in known_face_data.items():
        distance = np.linalg.norm(current_features_vector - data["avg_features"])
        if distance < min_distance:
            min_distance = distance
            recognized_person_id = person_id
            
    if recognized_person_id is not None and min_distance < RECOGNITION_THRESHOLD:
        return known_face_data[recognized_person_id]["name"], min_distance
    else:
        return "Unknown", min_distance


# --- メイン処理 ---
if __name__ == '__main__':
    init_db()
    load_known_faces_from_db() # 起動時にロード

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
    print(f"現在のアクティブユーザー(保存用): {active_person_name} (ID: {active_person_id})")
    print(f"認識閾値: {RECOGNITION_THRESHOLD}")

    # Matplotlibのウィンドウは認識時には必須ではないのでコメントアウトしても良い
    # plt.ion()
    # fig, ax = plt.subplots()

    def calculate_distance(p1_tuple, p2_tuple):
        p1 = np.array(p1_tuple)
        p2 = np.array(p2_tuple)
        return np.linalg.norm(p1 - p2)

    frame_message = ""
    message_display_time = 0
    save_trigger_flag = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        # Matplotlib関連のクリア処理 (もし使う場合)
        # ax.clear()
        # ax.set_title("Face Landmarks") ...

        info_text_save = f"Save User: {active_person_name} (ID: {active_person_id if active_person_id else 'N/A'})"
        cv2.putText(frame, info_text_save, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, "'q':Quit, 's':SaveFeat, 'r':Register", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

        for face_idx, face in enumerate(faces):
            cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), (0, 0, 255), 2)

            landmarks = predictor(gray, face)
            landmark_points = []
            for n in range(68):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                landmark_points.append((x, y))
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1) # ランドマーク描画

            # landmark_array = np.array(landmark_points) # Matplotlib用
            # ax.scatter(...) # Matplotlib用

            current_face_geometric_features_dict = {}
            if len(landmark_points) == 68:
                # --- 幾何学的特徴量の計算 ---
                # (昨日と同じ計算ロジック)
                left_eye_outer = landmark_points[36]
                right_eye_outer = landmark_points[45]
                eye_distance = calculate_distance(left_eye_outer, right_eye_outer)
                current_face_geometric_features_dict["eye_distance"] = eye_distance

                jaw_left = landmark_points[0]
                jaw_right = landmark_points[16]
                face_width = calculate_distance(jaw_left, jaw_right)
                current_face_geometric_features_dict["face_width"] = face_width

                nose_bridge = landmark_points[27]
                nose_tip = landmark_points[30]
                nose_length = calculate_distance(nose_bridge, nose_tip)
                current_face_geometric_features_dict["nose_length"] = nose_length
                
                # --- 現在の顔の特徴量ベクトルを作成 (認識用) ---
                current_feature_vector_for_recognition = np.array([
                    current_face_geometric_features_dict.get("eye_distance", 0),
                    current_face_geometric_features_dict.get("face_width", 0),
                    current_face_geometric_features_dict.get("nose_length", 0)
                ])

                # --- 顔認識処理 ---
                recognized_name, distance = recognize_face(current_feature_vector_for_recognition)
                
                # 認識結果をフレームに描画
                text_to_display = f"{recognized_name} ({distance:.2f})"
                cv2.putText(frame, text_to_display, (face.left(), face.top() - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if recognized_name != "Unknown" else (0,0,255) , 2)

            # 's'キーでの保存処理 (最初の顔のみ)
            if face_idx == 0 and save_trigger_flag:
                if current_face_geometric_features_dict: # 特徴量が計算されていれば
                    if save_face_features_to_db(landmark_points, current_face_geometric_features_dict):
                        frame_message = f"Saved for {active_person_name}"
                    else:
                        frame_message = "Save failed. Register user ('r')."
                else:
                    frame_message = "Features not calculated."
                message_display_time = 30
                save_trigger_flag = False

        # Matplotlibの更新 (もし使う場合)
        # ax.set_ylim(frame.shape[0], 0) ...
        # fig.canvas.draw()
        # fig.canvas.flush_events()

        if message_display_time > 0:
            cv2.putText(frame, frame_message, (10, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if "Saved" in frame_message else (0,0,255), 2)
            message_display_time -= 1

        cv2.imshow('Face Landmark Analyzer & Recognizer', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('s'):
            if faces:
                save_trigger_flag = True
                print("Save key pressed. Will attempt to save data for the first detected face.")
            else:
                frame_message = "No face detected to save."
                message_display_time = 30
        elif key == ord('r'):
            print("Register key pressed. Please input name in the console.")
            register_person_dialog()
            # print(f"Current active user (for saving): {active_person_name} (ID: {active_person_id})")


    cap.release()
    cv2.destroyAllWindows()
    # plt.ioff() # Matplotlib用
    # plt.show() # Matplotlib用