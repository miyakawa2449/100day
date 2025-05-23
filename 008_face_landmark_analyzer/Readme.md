# Face Landmark Analyzer

このプロジェクトは、ノートパソコンのカメラを使用してリアルタイムで顔を検出し、顔のランドマーク（特徴点）を取得して描画するPythonアプリケーションです。`dlib`ライブラリを使用して顔のランドマークを取得し、OpenCVを使用して映像に描画します。また、特徴量（目の距離、顔の幅、鼻の長さ）を計算して映像上に表示します。

---

## 特徴
- ノートパソコンのカメラを使用してリアルタイムで顔を検出。
- 顔のランドマーク（68個の特徴点）を取得。
- ランドマークを映像に描画。
- 特徴量（目の距離、顔の幅、鼻の長さ）を計算して表示。
- ランドマークをグラフとしてプロット。

---

## 必要な環境
- Python 3.7以上
- 以下のPythonライブラリ：
  - `opencv-python`
  - `dlib`
  - `numpy`
  - `matplotlib`

---

## セットアップ

### 1. 必要なライブラリのインストール
以下のコマンドを使用して必要なライブラリをインストールしてください。

```bash
pip install opencv-python dlib numpy matplotlib
```

### 2. モデルファイルの準備
`shape_predictor_68_face_landmarks.dat`というdlibのランドマーク予測モデルが必要です。以下のリンクからダウンロードしてください：

- [shape_predictor_68_face_landmarks.dat.bz2](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)

ダウンロード後、解凍してプロジェクトフォルダに配置してください。

---

## 実行方法
1. このリポジトリをクローンまたはダウンロードします。
2. ターミナルでプロジェクトフォルダに移動します。
3. 以下のコマンドを実行してアプリケーションを起動します：

```bash
python face_landmark_analyzer.py
```

4. カメラが起動し、リアルタイムで顔のランドマークが描画されます。
5. `q`キーを押すとアプリケーションが終了します。

---

## コードの概要

### 顔検出とランドマークの取得
- `dlib.get_frontal_face_detector()`を使用して顔を検出します。
- `dlib.shape_predictor()`を使用して68個の顔のランドマークを取得します。

### ランドマークの描画
- OpenCVの`cv2.circle()`を使用して、ランドマークを緑色の円として描画します。

### 特徴量の計算
- 目の距離、顔の幅、鼻の長さを計算し、映像上に表示します。

### ランドマークのプロット
- `matplotlib`を使用して、ランドマークをグラフとしてプロットします。

---

## 注意事項
- このプログラムは、`shape_predictor_68_face_landmarks.dat`がプロジェクトフォルダに存在しない場合、エラーを出して終了します。
- カメラが正常に動作していることを確認してください。

---

## 今後の拡張
- ランドマークデータをCSVファイルに保存。
- 複数の顔を同時に処理。
- 個人認識のための特徴量分析や分類モデルの構築。

---

## ライセンス
このプロジェクトはMITライセンスの下で公開されています。