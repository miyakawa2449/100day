import os
import cv2
import dlib
import numpy as np
# import matplotlib.pyplot as plt # 認識時には必須ではないが、残しておいてもOK
import sqlite3
import json
from datetime import datetime

# --- データベース関連の設定 ---
DB_NAME = "face_database.db"
active_person_id = None # 人物登録時に使用
active_person_name = "Unknown" # 人物登録時に使用

# --- 顔認識関連のグローバル変数 ---
known_face_data = {}  # {person_id: {"name": "Name", "avg_features": np.array([...])}}
RECOGNITION_THRESHOLD = 25.0 # 認識の閾値（特徴量が増えたため要調整の可能性あり）

def init_db():
    try:
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
    except sqlite3.Error as e:
        print(f"データベース初期化エラー: {e}")
    finally:
        if conn:
            conn.close()

def register_person_dialog():
    global active_person_id, active_person_name
    name = input("登録する人物の名前を入力してください: ")
    if not name:
        print("名前が入力されませんでした。")
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO persons (name) VALUES (?)", (name,))
        conn.commit()
        new_person_id = cursor.lastrowid
        active_person_id = new_person_id
        active_person_name = name
        print(f"人物 '{name}' (ID: {active_person_id}) を登録し、アクティブにしました。")
        load_known_faces_from_db() # 新規登録後、認識データを再読み込み
    except sqlite3.IntegrityError:
        print(f"エラー: 名前 '{name}' は既に登録されています。")
        if conn: # connがNoneでないことを確認
            cursor = conn.cursor() # IntegrityError後もcursorが必要なため再定義
            cursor.execute("SELECT person_id FROM persons WHERE name = ?", (name,))
            result = cursor.fetchone()
            if result:
                active_person_id = result[0]
                active_person_name = name
                print(f"既存の人物 '{name}' (ID: {active_person_id}) をアクティブにしました。")
    except sqlite3.Error as e:
        print(f"データベースエラー (登録処理): {e}")
    except Exception as e:
        print(f"予期せぬエラー (登録処理): {e}")
    finally:
        if conn:
            conn.close()

def save_face_features_to_db(landmarks_list, geo_features_dict):
    global active_person_id, active_person_name
    if active_person_id is None:
        print("特徴量を保存するアクティブな人物が設定されていません。'r'キーで人物を登録/選択してください。")
        return False

    landmarks_json = json.dumps(landmarks_list)
    geometric_features_json = json.dumps(geo_features_dict)

    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO face_features (person_id, landmarks_json, geometric_features_json)
            VALUES (?, ?, ?)
        ''', (active_person_id, landmarks_json, geometric_features_json))
        conn.commit()
        print(f"特徴量を人物ID {active_person_id} ({active_person_name}) として保存しました。")
        load_known_faces_from_db() # データ保存後、認識データを再読み込み
        return True
    except sqlite3.Error as e:
        print(f"データベース保存エラー: {e}")
        return False
    except Exception as e:
        print(f"予期せぬエラー (特徴量保存): {e}")
        return False
    finally:
        if conn:
            conn.close()

def load_known_faces_from_db():
    global known_face_data
    known_face_data = {} # 初期化
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        persons = {}
        cursor.execute("SELECT person_id, name FROM persons")
        for row in cursor.fetchall():
            persons[row[0]] = row[1]

        temp_features = {}
        cursor.execute("SELECT person_id, geometric_features_json FROM face_features")
        for row in cursor.fetchall():
            person_id = row[0]
            if person_id not in temp_features:
                temp_features[person_id] = []
            
            try:
                geo_features = json.loads(row[1])
                # 特徴量ベクトルを固定順序で作成 (この順序は計算時と合わせる必要がある)
                feature_vector = np.array([
                    geo_features.get("eye_distance", 0),
                    geo_features.get("face_width", 0),
                    geo_features.get("nose_length", 0),
                    geo_features.get("mouth_width", 0),
                    geo_features.get("inter_eyebrow_width", 0),
                    geo_features.get("face_height", 0),
                    geo_features.get("upper_lip_thickness", 0),
                    geo_features.get("lower_lip_thickness", 0),
                ])
                temp_features[person_id].append(feature_vector)
            except json.JSONDecodeError:
                print(f"警告: person_id {person_id} の特徴量JSONのパースに失敗しました。")
            except Exception as e:
                print(f"警告: 特徴量ベクトルの作成中にエラー (person_id {person_id}): {e}")

        for person_id, feature_vectors in temp_features.items():
            if person_id in persons and len(feature_vectors) > 0:
                avg_feature_vector = np.mean(feature_vectors, axis=0)
                known_face_data[person_id] = {
                    "name": persons[person_id],
                    "avg_features": avg_feature_vector
                }
        print(f"登録済み人物の特徴量をロードしました。{len(known_face_data)} 人分。")

    except sqlite3.Error as e:
        print(f"データベースからの特徴量読み込みエラー: {e}")
    except Exception as e:
        print(f"予期せぬエラー (特徴量読み込み): {e}")
    finally:
        if conn:
            conn.close()

def recognize_face(current_features_vector):
    if not known_face_data:
        return "Unknown", 0.0

    min_distance = float('inf')
    recognized_person_id = None

    for person_id, data in known_face_data.items():
        # 特徴量ベクトルの次元数が一致するか確認 (念のため)
        if current_features_vector.shape == data["avg_features"].shape:
            distance = np.linalg.norm(current_features_vector - data["avg_features"])
            if distance < min_distance:
                min_distance = distance
                recognized_person_id = person_id
        else:
            # print(f"警告: ID {person_id} の保存済み特徴量と現在の特徴量の次元が不一致です。") # デバッグ用
            pass # 不一致の場合は比較しない
            
    if recognized_person_id is not None and min_distance < RECOGNITION_THRESHOLD:
        return known_face_data[recognized_person_id]["name"], min_distance
    else:
        return "Unknown", min_distance

def calculate_distance(p1_tuple, p2_tuple):
    try:
        p1 = np.array(p1_tuple)
        p2 = np.array(p2_tuple)
        return np.linalg.norm(p1 - p2)
    except Exception as e:
        print(f"距離計算エラー: p1={p1_tuple}, p2={p2_tuple}, error={e}")
        return 0 # エラー時は0を返すか、例外を再スローする

# --- メイン処理 ---
if __name__ == '__main__':
    init_db()
    load_known_faces_from_db()

    model_path = "shape_predictor_68_face_landmarks.dat"
    if not os.path.exists(model_path):
        print(f"エラー: モデルファイルが見つかりません: {model_path}")
        print("モデルファイルをスクリプトと同じディレクトリにダウンロードしてください。")
        exit()

    try:
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(model_path)
    except RuntimeError as e: # dlibのモデルロードエラーはRuntimeErrorなど
        print(f"エラー: dlibの初期化に失敗しました。モデルファイルが破損しているか、互換性がない可能性があります。詳細: {e}")
        exit()
    except Exception as e:
        print(f"エラー: dlib関連の予期せぬエラー: {e}")
        exit()


    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("エラー: カメラを開けませんでした。インデックスを確認するか、他のアプリケーションがカメラを使用していないか確認してください。")
        exit()

    print("カメラを起動しました。'q':終了, 's':特徴量保存, 'r':人物登録/選択")
    print(f"現在のアクティブユーザー(保存用): {active_person_name} (ID: {active_person_id})")
    print(f"認識閾値: {RECOGNITION_THRESHOLD} (特徴量が変更されたため、この値は調整が必要かもしれません)")

    frame_message = ""
    message_display_time = 0
    save_trigger_flag = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("エラー: カメラからフレームを取得できませんでした。")
            break

        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)
        except Exception as e:
            print(f"フレーム処理エラー (cvtColor or detector): {e}")
            cv2.imshow('Face Landmark Analyzer & Recognizer', frame) # エラーがあっても表示は試みる
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            continue # 次のフレームへ

        info_text_save = f"Save User: {active_person_name} (ID: {active_person_id if active_person_id else 'N/A'})"
        cv2.putText(frame, info_text_save, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, "'q':Quit, 's':SaveFeat, 'r':Register", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

        for face_idx, face in enumerate(faces):
            try:
                cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), (0, 0, 255), 2)

                landmarks = predictor(gray, face)
                landmark_points = []
                for n in range(68):
                    x = landmarks.part(n).x
                    y = landmarks.part(n).y
                    landmark_points.append((x, y))
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

                current_face_geometric_features_dict = {}
                if len(landmark_points) == 68:
                    # --- 既存の幾何学的特徴量の計算 ---
                    left_eye_outer = landmark_points[36]
                    right_eye_outer = landmark_points[45]
                    current_face_geometric_features_dict["eye_distance"] = calculate_distance(left_eye_outer, right_eye_outer)

                    jaw_left = landmark_points[0]
                    jaw_right = landmark_points[16]
                    current_face_geometric_features_dict["face_width"] = calculate_distance(jaw_left, jaw_right)

                    nose_bridge_pt = landmark_points[27] # 鼻梁の点を明確に
                    nose_tip_pt = landmark_points[30]   # 鼻の先端の点を明確に
                    current_face_geometric_features_dict["nose_length"] = calculate_distance(nose_bridge_pt, nose_tip_pt)

                    # --- 追加の幾何学的特徴量の計算 ---
                    mouth_left_pt = landmark_points[48]
                    mouth_right_pt = landmark_points[54]
                    current_face_geometric_features_dict["mouth_width"] = calculate_distance(mouth_left_pt, mouth_right_pt)

                    left_eyebrow_inner_pt = landmark_points[21]
                    right_eyebrow_inner_pt = landmark_points[22]
                    current_face_geometric_features_dict["inter_eyebrow_width"] = calculate_distance(left_eyebrow_inner_pt, right_eyebrow_inner_pt)
                    
                    chin_bottom_pt = landmark_points[8]
                    # nose_bridge_pt は上で定義済み
                    current_face_geometric_features_dict["face_height"] = calculate_distance(chin_bottom_pt, nose_bridge_pt)

                    upper_lip_top_center_pt = landmark_points[51]
                    upper_lip_bottom_center_pt = landmark_points[62]
                    current_face_geometric_features_dict["upper_lip_thickness"] = calculate_distance(upper_lip_top_center_pt, upper_lip_bottom_center_pt)

                    lower_lip_top_center_pt = landmark_points[66]
                    lower_lip_bottom_center_pt = landmark_points[57]
                    current_face_geometric_features_dict["lower_lip_thickness"] = calculate_distance(lower_lip_top_center_pt, lower_lip_bottom_center_pt)
                    
                    # --- 現在の顔の特徴量ベクトルを作成 (認識用) ---
                    # この順序は load_known_faces_from_db と合わせる必要がある
                    current_feature_vector_for_recognition = np.array([
                        current_face_geometric_features_dict.get("eye_distance", 0),
                        current_face_geometric_features_dict.get("face_width", 0),
                        current_face_geometric_features_dict.get("nose_length", 0),
                        current_face_geometric_features_dict.get("mouth_width", 0),
                        current_face_geometric_features_dict.get("inter_eyebrow_width", 0),
                        current_face_geometric_features_dict.get("face_height", 0),
                        current_face_geometric_features_dict.get("upper_lip_thickness", 0),
                        current_face_geometric_features_dict.get("lower_lip_thickness", 0),
                    ])

                    recognized_name, distance = recognize_face(current_feature_vector_for_recognition)
                    
                    text_to_display = f"{recognized_name} ({distance:.2f})"
                    text_color = (0, 255, 0) if recognized_name != "Unknown" else (0,0,255)
                    cv2.putText(frame, text_to_display, (face.left(), face.top() - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color , 2)

                if face_idx == 0 and save_trigger_flag:
                    if current_face_geometric_features_dict:
                        if save_face_features_to_db(landmark_points, current_face_geometric_features_dict):
                            frame_message = f"Saved for {active_person_name}"
                        else:
                            frame_message = "Save failed. Check console."
                    else:
                        frame_message = "Features not calculated."
                    message_display_time = 60 # 少し長めに表示
                    save_trigger_flag = False
            
            except Exception as e:
                print(f"顔処理ループ内でエラー (face_idx {face_idx}): {e}")
                # この顔の処理はスキップして次に進む

        if message_display_time > 0:
            msg_color = (0, 255, 0) if "Saved" in frame_message else (0,0,255)
            if "failed" in frame_message or "not calculated" in frame_message or "No face" in frame_message:
                msg_color = (0,0,255)
            cv2.putText(frame, frame_message, (10, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, msg_color, 2)
            message_display_time -= 1

        cv2.imshow('Face Landmark Analyzer & Recognizer', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("終了します。")
            break
        elif key == ord('s'):
            if faces: # 顔が検出されている場合のみトリガー
                save_trigger_flag = True
                print("特徴量保存キー押下。次のフレームで最初の顔の特徴量を保存試行します。")
            else:
                frame_message = "No face detected to save features."
                message_display_time = 60
                print("特徴量保存キーが押されましたが、顔が検出されていません。")
        elif key == ord('r'):
            print("人物登録/選択キーが押されました。コンソールで名前を入力してください。")
            register_person_dialog()
            print(f"現在のアクティブユーザー(保存用): {active_person_name} (ID: {active_person_id})")


    cap.release()
    cv2.destroyAllWindows()
    print("リソースを解放し、ウィンドウを閉じました。")