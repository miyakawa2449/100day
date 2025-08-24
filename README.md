# 100日コーディングチャレンジ（前半：Day 001-015）

このリポジトリは、100日間のコーディングチャレンジの前半部分（15日分）をまとめたものです。初めてのプロジェクトだったため試行錯誤の跡も見られますが、Pythonを使った様々な分野への挑戦記録となっています。

## 📋 プロジェクト概要

各ディレクトリが1日分のプロジェクトに対応しており、ゲーム開発から始まり、AI・機械学習、コンピュータビジョン、そして最新のAI画像生成まで、幅広い技術領域をカバーしています。

## 🚀 プロジェクト一覧

### ゲーム開発編（Day 1-2, 5-6）
| Day | 実施日 | プロジェクト名 | 説明 | 主要技術 |
|-----|--------|--------------|------|---------|
| 001 | 2024-04-30 | [Othello](./001Day_Othello) | オセロ（リバーシ）ゲーム。AIとの対戦機能付き | Pygame |
| 002 | 2024-05-01 | [NumberGuess](./002DayNumberGues) | 数当てゲーム（1-1000）。GUI・音声効果・マウスホイール操作対応 | Pygame, Tkinter |
| 005 | 2024-05-04 | [Breakout](./005Day_Breakout) | ブロック崩しゲーム。サウンドエフェクト・日本語フォント対応 | Pygame |
| 006 | 2024-05-05 | [Tic-Tac-Toe](./006_Tic-Tac-Toe) | 三目並べ。ミニマックスアルゴリズムによる強力なAI対戦相手 | Python標準ライブラリ |

### AI・自然言語処理編（Day 3-4）
| Day | 実施日 | プロジェクト名 | 説明 | 主要技術 |
|-----|--------|--------------|------|---------|
| 003 | 2024-05-02 | [Llama3-8B-Youko](./003Llama3-8B-Youko) | ローカルLLMを使用したチャットボット（Flask版） | Flask, Transformers |
| 004 | 2024-05-03 | [Llama3 Colab](./004_llama3_8b_Youko_Colab) | Google Colab上で動作するLLMチャットボット | Flask, ngrok |

### コンピュータビジョン編（Day 7-11）
| Day | 実施日 | プロジェクト名 | 説明 | 主要技術 |
|-----|--------|--------------|------|---------|
| 007 | 2024-05-06 | [Face Recognition](./007_Face_Recognition) | リアルタイム顔検出システム | OpenCV, Haar Cascade |
| 008 | 2024-05-07 | [Face Landmark Analyzer](./008_face_landmark_analyzer) | 顔の68点ランドマーク検出と幾何学的特徴分析 | OpenCV, dlib |
| 009 | 2024-05-08 | [Face Memory](./009_face_memory) | 顔認識システム（データベース保存機能付き） | OpenCV, dlib, SQLite |
| 010 | 2024-05-09 | [Face Recognition v2](./010_face_Recognition) | 改良版顔認識システム | OpenCV, dlib, SQLite |
| 011 | 2024-05-10 | [Face Recognition v3](./011_face_Recognition) | 高度な幾何学的特徴を使用した顔認識システム | OpenCV, dlib, SQLite |

### AI画像生成編（Day 12-15）
| Day | 実施日 | プロジェクト名 | 説明 | 主要技術 |
|-----|--------|--------------|------|---------|
| 012 | 2024-05-11 | [AI Illustrator](./012_AI_Illustrator) | Stability AI APIを使用した画像生成 | Stability AI API |
| 013 | 2024-05-12 | [Stability AI](./013_Stability_AI) | 日本語プロンプト対応画像生成（翻訳機能付き） | OpenAI API, Stability AI |
| 014 | 2024-05-13 | [Stability AI Local](./014_Staibility_AI_Local) | ローカルStable Diffusion WebUIを使用した画像スタイル変換 | SD WebUI API |
| 015 | 2024-05-14 | [Stable Diffusion](./015_stable_diffusion) | 高機能画像スタイル変換Streamlitアプリ | Streamlit, SD WebUI |

## 🛠️ 使用技術

### プログラミング言語
- Python 3.7+

### 主要フレームワーク・ライブラリ
- **ゲーム開発**: Pygame
- **Web開発**: Flask, Streamlit
- **コンピュータビジョン**: OpenCV, dlib
- **機械学習・AI**: Hugging Face Transformers, OpenAI API, Stability AI API
- **データベース**: SQLite
- **その他**: NumPy, Pillow, Matplotlib, requests

## 📁 プロジェクト構成

```
100day/
├── 001Day_Othello/         # オセロゲーム
├── 002DayNumberGues/       # 数当てゲーム
├── 003Llama3-8B-Youko/     # LLMチャットボット
├── ...
├── 015_stable_diffusion/   # 画像スタイル変換アプリ
├── CLAUDE.md              # Claude Code用ガイド
└── README.md              # このファイル
```

## 🚀 始め方

各プロジェクトには個別のREADMEファイルがあります。基本的な実行手順：

1. プロジェクトディレクトリに移動
```bash
cd [プロジェクトディレクトリ]
```

2. 必要な依存関係をインストール
```bash
pip install -r requirements.txt  # ある場合
# または個別にインストール
```

3. プログラムを実行
```bash
python main.py  # または各プロジェクト固有のファイル名
```

## 💡 学習の軌跡

このチャレンジを通じて学んだこと：

1. **基礎力の構築**（Day 1-6）: Pythonでのゲーム開発とGUIプログラミング
2. **AI技術への挑戦**（Day 3-4）: 大規模言語モデルの活用
3. **コンピュータビジョンの探求**（Day 7-11）: 顔認識技術の段階的な実装
4. **最新AI技術の応用**（Day 12-15）: 画像生成AIの実践的活用

## 🔗 100日チャレンジ関連プロジェクト

この前半戦（Day 001-015）の後、さらなる学習を続けました：

### 中期（Day 016-056）
| プロジェクト | 説明 | 主要技術 |
|-------------|------|---------|
| [mini-blog](https://github.com/miyakawa2449/mini-blog) | ミニマルなブログシステムの構築 | Web開発, データベース |
| [AudioOpt](https://github.com/miyakawa2449/AudioOpt) | 音声処理の最適化システム | 音声処理, Python |
| [Python_Audio_dataset](https://github.com/miyakawa2449/Python_Audio_dataset) | 音声データセット処理ツール | データ処理, 音声解析 |
| [Audio-Pipeline-Integrated](https://github.com/miyakawa2449/Audio-Pipeline-Integrated) | 統合音声処理パイプライン | システム統合, 音声処理 |

### 後期（Day 057-100）
| プロジェクト | 説明 | 主要技術 |
|-------------|------|---------|
| [daily-python-projects](https://github.com/miyakawa2449/daily-python-projects) | 日々のPythonプロジェクト集（57-100日目） | 総合的なPython開発 |

### 学習の進化
- **前半（001-015）**: 基礎技術の習得とプロトタイピング
- **中期（016-056）**: 実用的なWebアプリケーションと音声処理への特化
- **後期（057-100）**: より洗練されたプロジェクト設計と総合力の向上

## 🔍 特記事項

- 初めてのプロジェクトのため、コードの品質にばらつきがあります
- 多くのプロジェクトに日本語のドキュメントが含まれています
- 後半のプロジェクトほど、エラーハンドリングやコード構造が改善されています
- 各プロジェクトは独立して動作します

## 📝 ライセンス

各プロジェクトのライセンスについては、個別のREADMEを参照してください。

## 🤝 貢献

これは個人的な学習プロジェクトですが、改善提案やフィードバックは歓迎します。

---

**注**: これは100日チャレンジの前半部分（Day 001-015）です。各ディレクトリ内の詳細なドキュメントも合わせてご参照ください。