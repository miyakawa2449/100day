import sys
import os
import random
import math
import time # 点滅のために time.sleep は使わず QTimer を使う

# PySide6 (Qt for Python) モジュールのインポート
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSpinBox, QMessageBox, QTextEdit
)
from PySide6.QtCore import Qt, QTimer, QDir
from PySide6.QtGui import QFont, QPalette, QColor, QWheelEvent

# サウンド再生のための pygame モジュールのインポート
import pygame

# --- Helper Function: Get Divisors ---
def get_divisors(n):
    """指定された正の整数の全ての正の約数をリストで返す"""
    if n <= 0:
        return []
    divs = set()
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            divs.add(i)
            divs.add(n // i)
    return sorted(list(divs))

# --- Helper Function: is_prime ---
def is_prime(n):
    """素数判定関数"""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

# --- メインアプリケーションクラス ---
class NumberGuessApp(QWidget):
    def __init__(self):
        super().__init__()

        # ゲーム設定値
        self.lower_bound = 1
        self.upper_bound = 1000
        self.max_guesses = 5

        # サウンドファイルのパス設定
        self.sound_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'sounds')
        self.sounds = {} # サウンドオブジェクトを格納する辞書

        # Pygame Mixer の初期化とサウンド読み込み
        self.init_pygame_mixer()
        self.load_sounds()

        # GUIの初期化
        self.init_ui()

        # ゲームの初期化
        self.start_new_game()

    def init_pygame_mixer(self):
        """Pygame Mixerを初期化する"""
        try:
            pygame.mixer.init()
            print("Pygame mixer initialized successfully.")
        except pygame.error as e:
            print(f"Pygame mixer の初期化に失敗しました: {e}")
            QMessageBox.warning(self, "サウンドエラー", f"サウンドシステムの初期化に失敗しました。\n{e}\nサウンドなしで続行します。")

    def load_sounds(self):
        """サウンドファイルを読み込む"""
        if not pygame.mixer.get_init():
             print("Mixer not initialized, skipping sound loading.")
             return

        sound_files = {
            'click': 'click.mp3',
            'judging': 'judging.mp3',
            'correct': 'correct.mp3',
            'incorrect': 'incorrect.mp3'
        }
        for name, filename in sound_files.items():
            path = os.path.join(self.sound_folder, filename)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    print(f"Loaded sound: {filename}")
                except pygame.error as e:
                    print(f"サウンドファイル '{filename}' の読み込みに失敗しました: {e}")
                    self.sounds[name] = None
            else:
                print(f"サウンドファイルが見つかりません: {path}")
                self.sounds[name] = None

    def play_sound(self, name):
        """指定された名前のサウンドを再生する"""
        if pygame.mixer.get_init() and name in self.sounds and self.sounds[name]:
            try:
                self.sounds[name].play()
            except pygame.error as e:
                print(f"サウンド '{name}' の再生エラー: {e}")
        else:
            print(f"Cannot play sound: {name} (Mixer init: {pygame.mixer.get_init()}, Sound loaded: {name in self.sounds and self.sounds[name] is not None})")

    def init_ui(self):
        """GUIウィジェットを作成し配置する"""
        self.setWindowTitle("数当てゲーム GUI版")
        self.setGeometry(100, 100, 500, 450)

        # --- レイアウト設定 ---
        main_layout = QVBoxLayout(self)

        # 上部: 情報表示エリア
        info_layout = QHBoxLayout()
        self.turn_label = QLabel("ターン: 1/5")
        self.guesses_left_label = QLabel(f"残り試行回数: {self.max_guesses}")
        info_layout.addWidget(self.turn_label)
        info_layout.addStretch()
        info_layout.addWidget(self.guesses_left_label)
        main_layout.addLayout(info_layout)

        # 中央: 数字表示と入力
        number_layout = QVBoxLayout()
        number_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # マウスホイールで操作する数字表示ラベル
        self.number_display_label = QLabel("1")
        number_font = QFont()
        number_font.setPointSize(72)
        number_font.setBold(True)
        self.number_display_label.setFont(number_font)
        self.number_display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.number_display_label.setStyleSheet("border: 2px solid lightgray; padding: 10px; background-color: white;")
        self.number_display_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.number_display_label.installEventFilter(self)

        # 数字入力用スピンボックス (補助)
        self.spin_box = QSpinBox()
        self.spin_box.setRange(self.lower_bound, self.upper_bound)
        self.spin_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_box.valueChanged.connect(self.sync_number_display_from_spinbox)

        number_layout.addWidget(self.number_display_label)
        number_layout.addWidget(QLabel("↑ ホイールで変更 / ↓ 直接入力"))
        number_layout.addWidget(self.spin_box)
        main_layout.addLayout(number_layout)
        main_layout.addSpacing(20)

        # 中下部: ヒントボタン
        hint_layout = QHBoxLayout()
        self.hint_button_1 = QPushButton("公約数ヒント (1)")
        self.hint_button_2 = QPushButton("素数ヒント (2)")
        self.hint_button_3 = QPushButton("範囲ヒント (3)")
        self.hint_button_1.clicked.connect(lambda: self.show_hint(1))
        self.hint_button_2.clicked.connect(lambda: self.show_hint(2))
        self.hint_button_3.clicked.connect(lambda: self.show_hint(3))
        hint_layout.addWidget(self.hint_button_1)
        hint_layout.addWidget(self.hint_button_2)
        hint_layout.addWidget(self.hint_button_3)
        main_layout.addLayout(hint_layout)

        # 下部: 判定/新しいゲームボタンとメッセージ表示
        self.judge_button = QPushButton("判定") # 初期テキスト
        self.judge_button.setFixedHeight(40)
        # 初期接続は start_new_game で行う
        main_layout.addWidget(self.judge_button)

        self.message_box = QTextEdit()
        self.message_box.setReadOnly(True)
        self.message_box.setFixedHeight(80)
        main_layout.addWidget(self.message_box)

        # 点滅用タイマー
        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self.flash_number)
        self.flash_count = 0
        self.original_number_style = self.number_display_label.styleSheet()

        self.setLayout(main_layout)

    # --- イベントフィルター (マウスホイール用) ---
    def eventFilter(self, obj, event):
        if obj == self.number_display_label and event.type() == QWheelEvent.Type.Wheel:
            self.handle_wheel_event(event)
            return True
        return super().eventFilter(obj, event)

    def handle_wheel_event(self, event: QWheelEvent):
        """マウスホイールイベントを処理して数字を更新する"""
        # ゲーム終了後でもホイール操作は可能にする（新しいゲームの準備のため）
        # if not self.judge_button.isEnabled():
        #     return

        current_value = int(self.number_display_label.text())
        delta = event.angleDelta().y()

        if delta > 0:
            current_value += 1
        elif delta < 0:
            current_value -= 1

        current_value = max(self.lower_bound, min(self.upper_bound, current_value))

        self.number_display_label.setText(str(current_value))
        self.spin_box.blockSignals(True)
        self.spin_box.setValue(current_value)
        self.spin_box.blockSignals(False)

    def sync_number_display_from_spinbox(self, value):
        """スピンボックスの値が変更されたときにラベル表示を同期する"""
        # ゲーム終了後でもスピンボックス操作は可能にする
        # if not self.judge_button.isEnabled():
        #      return
        self.number_display_label.setText(str(value))

    # --- ゲームロジックメソッド ---
    def start_new_game(self):
        """新しいゲームを開始する"""
        self.target_number = random.randint(self.lower_bound, self.upper_bound)
        self.guesses_left = self.max_guesses
        self.turn = 1
        self.hint3_range_delta = 50
        self.guess_4_value = None
        self.used_hints_this_turn = False

        # UIリセット
        self.update_ui()
        self.message_box.setText("新しいゲームを開始しました！数字を推測するか、ヒントを使ってください。")
        self.number_display_label.setText(str(self.lower_bound))
        self.spin_box.setValue(self.lower_bound)
        self.enable_controls(True) # 全てのコントロールを有効に
        self.number_display_label.setStyleSheet(self.original_number_style)

        # ★★★ 判定ボタンをリセット ★★★
        self.judge_button.setText("判定")
        try:
            # 既存の接続を全て解除 (安全のため)
            self.judge_button.clicked.disconnect()
        except RuntimeError:
            # まだ接続がない場合はエラーになるので無視
            pass
        # start_judging メソッドを接続
        self.judge_button.clicked.connect(self.start_judging)
        # ★★★★★★★★★★★★★★★★★

        print(f"(デバッグ用: 正解は {self.target_number})")

    def update_ui(self):
        """ターン数や残り試行回数などのUI表示を更新する"""
        self.turn_label.setText(f"ターン: {self.turn}/{self.max_guesses}")
        self.guesses_left_label.setText(f"残り試行回数: {self.guesses_left}")
        # ヒントボタンの状態制御は enable_controls で行う

    def enable_controls(self, enabled):
        """入力コントロールやボタンの有効/無効を切り替える"""
        self.spin_box.setEnabled(enabled)
        # ヒントボタンは、有効状態かつまだヒントを使っていない場合のみ有効
        hint_enabled = enabled and not self.used_hints_this_turn
        self.hint_button_1.setEnabled(hint_enabled)
        self.hint_button_2.setEnabled(hint_enabled)
        self.hint_button_3.setEnabled(hint_enabled)
        # 判定ボタンは常に有効にしておき、状態に応じてテキストと動作を変える
        self.judge_button.setEnabled(True) # ★ 常に有効に変更

    def show_hint(self, hint_type):
        """選択されたヒントを表示する"""
        if self.used_hints_this_turn:
            self.message_box.append("このターンでは既にヒントを使用しました。")
            return
        # ゲーム終了後はヒントを使えないようにする
        if self.judge_button.text() == "新しいゲーム":
             self.message_box.append("ゲームは終了しています。")
             return

        self.play_sound('click')
        self.used_hints_this_turn = True
        # ヒントボタンを無効化
        self.hint_button_1.setEnabled(False)
        self.hint_button_2.setEnabled(False)
        self.hint_button_3.setEnabled(False)

        hint_text = f"ヒント {hint_type}: "

        if hint_type == 1:
            if sys.version_info < (3, 5):
                hint_text += "このヒントには math.gcd が必要です (Python 3.5+)。"
            else:
                num_cd = -1
                while num_cd == -1 or num_cd == self.target_number:
                    num_cd = random.randint(self.lower_bound, self.upper_bound)
                common_divisor_val = math.gcd(self.target_number, num_cd)
                if common_divisor_val > 1:
                    all_divs_of_gcd = get_divisors(common_divisor_val)
                    possible_hints = [d for d in all_divs_of_gcd if d > 1]
                    if possible_hints:
                        chosen_hint_divisor = random.choice(possible_hints)
                        hint_text += f"{chosen_hint_divisor} は、正解の数と {num_cd} の公約数です。"
                    else:
                         hint_text += f"正解の数と {num_cd} の最大公約数は {common_divisor_val} です。(内部エラー?)"
                else:
                    hint_text += f"正解の数と {num_cd} は、1以外に公約数を持ちません（互いに素です）。"
        elif hint_type == 2:
            if is_prime(self.target_number):
                hint_text += "正解の数は素数です。"
            else:
                hint_text += "正解の数は素数ではありません。"
        elif hint_type == 3:
            current_delta = self.hint3_range_delta
            window_size = 2 * current_delta + 1
            min_possible_lower = max(self.lower_bound, self.target_number - window_size + 1)
            max_possible_lower = self.target_number
            if min_possible_lower >= max_possible_lower:
                 actual_lower = max(self.lower_bound, self.target_number - current_delta)
            else:
                 actual_lower = random.randint(min_possible_lower, max_possible_lower)
            actual_upper = min(self.upper_bound, actual_lower + window_size - 1)
            self.hint3_range_delta = max(10, self.hint3_range_delta - 20)
            hint_text += f"正解の数は {actual_lower} から {actual_upper} の間にあります。"
            hint_text += f"（次回の範囲ヒント幅は約 {2 * self.hint3_range_delta + 1} になります）"

        self.message_box.append(hint_text)

    def start_judging(self):
        """判定ボタンが押されたときの処理（点滅開始）"""
        self.play_sound('click')
        # 判定中はヒントボタンとスピンボックスを無効化
        self.hint_button_1.setEnabled(False)
        self.hint_button_2.setEnabled(False)
        self.hint_button_3.setEnabled(False)
        self.spin_box.setEnabled(False)
        # 判定ボタン自体も一時的に無効化（連打防止）
        self.judge_button.setEnabled(False)
        self.message_box.append("判定中...")
        self.flash_count = 0
        self.flash_timer.start(150)
        self.play_sound('judging')

    def flash_number(self):
        """数字表示を点滅させるタイマーイベント"""
        total_flashes = 20
        if self.flash_count >= total_flashes:
            self.flash_timer.stop()
            if pygame.mixer.get_init() and 'judging' in self.sounds and self.sounds['judging']:
                 self.sounds['judging'].stop()
            self.number_display_label.setStyleSheet(self.original_number_style)
            self.judge_guess() # 点滅終了後に判定処理へ
            return

        if self.flash_count % 2 == 0:
            self.number_display_label.setStyleSheet("border: 2px solid gray; padding: 10px; background-color: yellow; color: black;")
        else:
            self.number_display_label.setStyleSheet("border: 2px solid gray; padding: 10px; background-color: white; color: black;")

        self.flash_count += 1

    def judge_guess(self):
        """推測値を判定し、結果を表示する"""
        guess = int(self.number_display_label.text())
        game_over = False # ゲーム終了フラグ

        if guess == self.target_number:
            # 正解
            self.play_sound('correct')
            self.message_box.append("*" * 20)
            self.message_box.append(f"おめでとうございます！正解です！\n数字は {self.target_number} でした。")
            self.message_box.append(f"試行回数 {self.turn} 回でクリアしました。")
            self.message_box.append("*" * 20)
            QMessageBox.information(self, "クリア！", f"正解！ 数字は {self.target_number} でした！")
            game_over = True
        else:
            # 不正解
            self.play_sound('incorrect')
            self.guesses_left -= 1
            self.message_box.append(f"推測: {guess} -> 不正解です。")

            if self.turn == 4:
                self.guess_4_value = guess

            if self.guesses_left == 0:
                # ゲームオーバー (試行回数切れ)
                self.message_box.append("-" * 20)
                self.message_box.append("残念！試行回数がなくなりました。")
                self.message_box.append(f"正解の数は {self.target_number} でした。")
                QMessageBox.information(self, "ゲームオーバー", f"残念！正解は {self.target_number} でした。")
                game_over = True
            else:
                # 次のターンへ
                self.turn += 1
                self.used_hints_this_turn = False

                if self.turn == 5 and self.guess_4_value is not None:
                    final_hint = "最終ヒント: "
                    if self.target_number > self.guess_4_value:
                        final_hint += f"正解は、4回目の推測 ({self.guess_4_value}) より大きいです。"
                    else:
                        final_hint += f"正解は、4回目の推測 ({self.guess_4_value}) より小さいです。"
                    self.message_box.append(final_hint)

                self.update_ui()
                # 次のターンの操作を許可 (判定ボタンも含む)
                self.enable_controls(True)

        # ★★★ ゲーム終了時の処理 ★★★
        if game_over:
            self.enable_controls(False) # ヒントとスピンボックスを無効化
            self.judge_button.setText("新しいゲーム") # ボタンテキスト変更
            try:
                # 既存の接続を解除
                self.judge_button.clicked.disconnect()
            except RuntimeError:
                pass # 接続がない場合は無視
            # start_new_game を接続
            self.judge_button.clicked.connect(self.start_new_game)
            self.judge_button.setEnabled(True) # 新しいゲームボタンは有効にする
        # ★★★★★★★★★★★★★★★★★

    # --- ウィンドウを閉じる処理 ---
    def closeEvent(self, event):
        """ウィンドウが閉じられるときに Pygame Mixer を終了する"""
        if pygame.mixer.get_init():
            pygame.mixer.quit()
            print("Pygame mixer quit.")
        event.accept()

# --- アプリケーション実行 ---
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # ★★★ アプリケーション全体のフォントを設定 ★★★
    font = QFont("Noto Serif CJK JP", 10)
    app.setFont(font)
    # ★★★★★★★★★★★★★★★★★★★★★★★★★

    game_app = NumberGuessApp()
    game_app.show()
    sys.exit(app.exec())