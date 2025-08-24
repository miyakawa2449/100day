# 数当てゲーム (Number Guessing Game)

PySide6とPygameを組み合わせたGUIベースの数当てゲームです。1〜1000の範囲で秘密の数字を当てる戦略的なゲームです。

![数当てゲーム画面](./docs/number_guess_game.png)

## 必要環境

- Python 3.8+
- PySide6 (Qt for Python)
- Pygame (サウンド再生用)

## インストール

```bash
pip install PySide6 pygame
```

## 実行方法

```bash
python numberGuessGUI.py
```

## ゲームの特徴

### 基本仕様
- **範囲**: 1〜1000の数字
- **試行回数**: 最大5回
- **操作方法**: マウスホイール操作 + 直接入力

### 高度なヒントシステム
1. **公約数ヒント**: 正解とランダムな数の公約数情報
2. **素数ヒント**: 正解が素数かどうかの判定
3. **範囲ヒント**: 正解を含む範囲（使用するたびに狭まる）

### UI・UX機能
- **大型数字表示**: 72ptの大きな数字で視認性向上
- **マウスホイール操作**: 直感的な数値変更
- **判定時エフェクト**: 3秒間の点滅アニメーション
- **サウンドフィードバック**: 各アクション（クリック、判定、正解/不正解）に対応

## プロジェクト構成

```
002DayNumberGues/
├── numberGuessGUI.py    # メインプログラム
├── number_guess.py      # コンソール版（参考）
├── gameRulus.md         # ゲームルール詳細
├── docs/                # スクリーンショット
└── assets/
    └── sounds/          # サウンドファイル
        ├── click.mp3
        ├── correct.mp3
        ├── incorrect.mp3
        └── judging.mp3
```

## 技術仕様

### アーキテクチャ
- **GUI**: PySide6 (Qt)
- **サウンド**: Pygame Mixer
- **数学関数**: 標準ライブラリ (math, random)

### 主要クラス・メソッド
- `NumberGuessApp`: メインアプリケーションクラス
- `get_divisors()`: 約数計算（公約数ヒント用）
- `is_prime()`: 素数判定（素数ヒント用）
- `eventFilter()`: マウスホイールイベント処理

### ヒントアルゴリズム
```python
# 公約数ヒント
common_divisor = math.gcd(target, random_number)

# 範囲ヒント（動的サイズ調整）
window_size = 2 * delta + 1
self.hint3_range_delta = max(10, self.hint3_range_delta - 20)
```

## 操作方法

1. **数字選択**: 
   - マウスホイールで大型表示の数字を変更
   - または下部の入力ボックスで直接入力
2. **ヒント使用**: 各ターン1回まで、3種類から選択
3. **判定実行**: 「判定」ボタンで推測を確定
4. **ゲーム継続**: 正解または5回試行でゲーム終了

## ライセンス

このプロジェクトは学習目的で作成されました。

---

**100日コーディングチャレンジ Day 002**