import random
import math
import sys
import datetime
import pytz

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
    return sorted(list(divs)) # ソートして返す

# --- Helper Function: is_prime (変更なし) ---
def is_prime(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

# --- Main Game Function (Ver.4) ---
def play_game_v4():
    """数当てゲームを実行する関数 (Ver.4: 範囲ゆらぎ、公約数ヒント)"""
    try:
        jst = pytz.timezone('Asia/Tokyo')
        current_time_jst = datetime.datetime.now(jst)
        print(f"ゲーム開始時刻: {current_time_jst.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    except Exception as e:
        print(f"時刻取得エラー: {e}")

    lower_bound = 1
    upper_bound = 1000
    target_number = random.randint(lower_bound, upper_bound)

    max_guesses = 5
    guesses_left = max_guesses
    hint3_range_delta = 50 # ヒント3の初期範囲増減値 (ゆらぎに使う)
    guess_4_value = None

    print("数当てゲームへようこそ！ (Ver.4: 範囲ゆらぎ、公約数ヒント)")
    print(f"{lower_bound}から{upper_bound}までの数字を当ててください。")
    print(f"回答のチャンスは {max_guesses} 回です。")
    print("各回の推測前に、ヒントを1つ使うことができます。")
    print("フィードバックは、4回目の推測後に1回だけ与えられます。")
    # print(f"(デバッグ用: 正解は {target_number})")

    for turn in range(1, max_guesses + 1):
        print("-" * 20)
        print(f"◆ ターン {turn}/{max_guesses} ◆")

        if turn == 5 and guess_4_value is not None:
             print("-" * 10 + " 最終ヒント " + "-" * 10)
             if target_number > guess_4_value:
                 print(f"正解は、あなたの4回目の推測 ({guess_4_value}) より大きいです。")
             else:
                 print(f"正解は、あなたの4回目の推測 ({guess_4_value}) より小さいです。")
             print("-" * 32)

        use_hint = input("推測の前にヒントを使いますか？ (y/n): ").lower().strip()
        if use_hint == 'y':
            print("どのヒントを使いますか？ (1, 2, 3)")
            print("  1: 公約数ヒント") # 名前変更
            print("  2: 素数ヒント")
            print("  3: 範囲ヒント（ゆらぎあり）") # 説明追加
            hint_choice = input("選択: ").strip()

            # === Hint Logic ===
            if hint_choice == '1':
                # ヒント1: 公約数ヒント (LCMから変更)
                if sys.version_info < (3, 5):
                    print("エラー: このヒントには math.gcd が必要です (Python 3.5+)。")
                else:
                    num_cd = -1
                    while num_cd == -1 or num_cd == target_number:
                        num_cd = random.randint(lower_bound, upper_bound)

                    common_divisor_val = math.gcd(target_number, num_cd)

                    if common_divisor_val > 1:
                        all_divs_of_gcd = get_divisors(common_divisor_val)
                        # 1以外の約数リスト
                        possible_hints = [d for d in all_divs_of_gcd if d > 1]
                        if possible_hints:
                            chosen_hint_divisor = random.choice(possible_hints)
                            print(f"ヒント1: {chosen_hint_divisor} は、正解の数と {num_cd} の公約数です。")
                        else: # GCD>1 なのに 1以外の約数がない? (通常発生しないはず)
                             print(f"ヒント1: 正解の数と {num_cd} の最大公約数は {common_divisor_val} です。(内部エラー?)")
                    else: # gcd == 1
                        print(f"ヒント1: 正解の数と {num_cd} は、1以外に公約数を持ちません（互いに素です）。")

            elif hint_choice == '2':
                # ヒント2: 素数ヒント (変更なし)
                if is_prime(target_number):
                    print("ヒント2: 正解の数は素数です。")
                else:
                    print("ヒント2: 正解の数は素数ではありません。")

            elif hint_choice == '3':
                # ヒント3: 範囲ヒント (ゆらぎあり)
                current_delta = hint3_range_delta
                # 目標のウィンドウサイズ (奇数になるように)
                window_size = 2 * current_delta + 1

                # 下限が取りうる最小値と最大値を計算
                min_possible_lower = max(lower_bound, target_number - window_size + 1)
                max_possible_lower = target_number

                # 下限をランダムに決定
                if min_possible_lower >= max_possible_lower:
                     # エッジケースや delta が大きすぎる場合、中央寄りにフォールバック
                     actual_lower = max(lower_bound, target_number - current_delta)
                else:
                     actual_lower = random.randint(min_possible_lower, max_possible_lower)

                # 上限を計算し、全体の範囲内に収める
                actual_upper = min(upper_bound, actual_lower + window_size - 1)

                # (表示前に) 次回のdeltaを計算しておく
                hint3_range_delta = max(10, hint3_range_delta - 20)

                print(f"ヒント3: 正解の数は {actual_lower} から {actual_upper} の間にあります。")
                print(f"（次回の範囲ヒント幅は約 {2 * hint3_range_delta + 1} になります）") # 参考情報

            else:
                print("無効なヒント選択です。ヒントは使用されませんでした。")

        # === Guess Input ===
        while True:
            try:
                guess_str = input(f"数字を推測してください ({lower_bound}-{upper_bound}): ")
                guess = int(guess_str)
                if not (lower_bound <= guess <= upper_bound):
                     print(f"範囲外です。{lower_bound}から{upper_bound}の間で入力してください。")
                     continue
                break
            except ValueError:
                print("無効な入力です。数字を入力してください。")

        # === Check Guess ===
        if guess == target_number:
            print("*" * 30)
            print(f"おめでとうございます！正解です！数字は {target_number} でした。")
            print(f"試行回数 {turn} 回でクリアしました。")
            print("*" * 30)
            return # ゲーム終了

        else:
            # 不正解
            guesses_left -= 1
            print("不正解です。")
            if turn == 4:
                guess_4_value = guess # 4回目の推測値を保存
            if guesses_left == 0:
                # 試行回数終了
                print("-" * 20)
                print("残念！試行回数がなくなりました。")
                print(f"正解の数は {target_number} でした。")
                return # ゲーム終了

# --- Run Game ---
if __name__ == "__main__":
    play_game_v4()