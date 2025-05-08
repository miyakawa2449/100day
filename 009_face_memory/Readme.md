# Face Memory System

このプロジェクトは、顔のランドマークを検出し、特徴量をデータベースに保存するシステムです。SQLite データベースを使用して、人物情報と顔の特徴量を管理します。

## 機能

- 顔のランドマーク検出 (dlib を使用)
- 幾何学的特徴量の計算 (例: 目の距離、顔の幅、鼻の長さ)
- SQLite データベースへの人物情報と特徴量の保存
- カメラ映像をリアルタイムで処理

## 必要な環境

- Python 3.8 以上
- 必要なライブラリ:
  - `opencv-python`
  - `dlib`
  - `numpy`
  - `matplotlib`

## セットアップ

1. 仮想環境を作成して有効化します。

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. 必要なライブラリをインストールします。

   ```bash
   pip install opencv-python dlib numpy matplotlib
   ```

3. `shape_predictor_68_face_landmarks.dat` モデルファイルをダウンロードします。

   - dlib モデルファイルのダウンロード
     -　[shape_predictor_68_face_landmarks.dat.bz2](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2) 
   - ダウンロード後、解凍してプロジェクトフォルダに配置してください。

4. データベースを初期化します。

   プログラムを初めて実行すると、`face_database.db` が自動的に作成されます。

## 使用方法

1. プログラムを実行します。

   ```bash
   python main.py
   ```

2. キー操作:
   - `r`: 新しい人物を登録します。コンソールに名前を入力してください。
   - `s`: 検出された顔の特徴量を保存します。
   - `q`: プログラムを終了します。

3. カメラ映像に表示される情報:
   - 登録された人物の名前と ID
   - 検出された顔のランドマークと特徴量

## データベース構造

- **`persons` テーブル**: 登録された人物情報を管理
  - `person_id`: ユニークな ID
  - `name`: 名前
  - `created_at`: 登録日時

- **`face_features` テーブル**: 顔の特徴量を保存
  - `feature_id`: ユニークな ID
  - `person_id`: 登録された人物の ID
  - `landmarks_json`: 顔のランドマーク座標 (JSON 形式)
  - `geometric_features_json`: 幾何学的特徴量 (JSON 形式)
  - `detected_at`: 保存日時

## 注意事項

- カメラが正しく接続されていることを確認してください。
- `shape_predictor_68_face_landmarks.dat` ファイルがプロジェクトフォルダに存在する必要があります。

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 貢献

バグ報告や機能提案は歓迎します！プルリクエストを送ってください。