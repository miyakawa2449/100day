import random

class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]  # 3x3のボード
        self.current_player = 'X'  # デフォルトでプレイヤーが先攻
        self.winner = None

    def display_board(self):
        print("\n")
        for i in range(3):
            print(" | ".join(self.board[i * 3:(i + 1) * 3]))
            if i < 2:
                print("-" * 9)
        print("\n")

    def make_move(self, position):
        if self.board[position] == ' ':
            self.board[position] = self.current_player
            self.check_winner()
            self.current_player = 'O' if self.current_player == 'X' else 'X'
        else:
            print("その位置はすでに埋まっています。別の位置を選んでください。")

    def check_winner(self):
        winning_combinations = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # 横
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # 縦
            (0, 4, 8), (2, 4, 6)              # 斜め
        ]
        for combo in winning_combinations:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != ' ':
                self.winner = self.board[combo[0]]
                return

    def is_draw(self):
        return ' ' not in self.board and self.winner is None

    def reset_game(self):
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'
        self.winner = None

    def computer_move(self):
        # ミニマックスアルゴリズムを使用して最適な手を選ぶ
        best_score = float('-inf')
        best_move = None
        for i in range(9):
            if self.board[i] == ' ':
                self.board[i] = 'O'  # コンピュータの手を仮定
                score = self.minimax(False)
                self.board[i] = ' '  # 元に戻す
                if score > best_score:
                    best_score = score
                    best_move = i
        self.make_move(best_move)

    def minimax(self, is_maximizing):
        if self.winner == 'X':
            return -1  # プレイヤーが勝つ場合
        elif self.winner == 'O':
            return 1  # コンピュータが勝つ場合
        elif self.is_draw():
            return 0  # 引き分けの場合

        if is_maximizing:
            best_score = float('-inf')
            for i in range(9):
                if self.board[i] == ' ':
                    self.board[i] = 'O'
                    self.check_winner()
                    score = self.minimax(False)
                    self.board[i] = ' '
                    self.winner = None
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(9):
                if self.board[i] == ' ':
                    self.board[i] = 'X'
                    self.check_winner()
                    score = self.minimax(True)
                    self.board[i] = ' '
                    self.winner = None
                    best_score = min(score, best_score)
            return best_score

def main():
    game = TicTacToe()
    print("三目並べゲームへようこそ！")
    print("ボードの位置は以下のように番号で指定します：")
    print("0 | 1 | 2\n---------\n3 | 4 | 5\n---------\n6 | 7 | 8\n")

    # プレイヤーが先攻か後攻を選択
    while True:
        choice = input("先攻（X）か後攻（O）を選んでください: ").upper()
        if choice in ['X', 'O']:
            game.current_player = choice
            break
        else:
            print("無効な入力です。'X' または 'O' を入力してください。")

    while True:
        game.display_board()

        if game.current_player == 'X':
            try:
                position = int(input("あなたのターンです。位置を選んでください (0-8): "))
                if position < 0 or position > 8:
                    print("無効な入力です。0から8の数字を入力してください。")
                    continue
                game.make_move(position)
            except ValueError:
                print("無効な入力です。数字を入力してください。")
        else:
            print("コンピュータのターンです...")
            game.computer_move()

        if game.winner:
            game.display_board()
            print(f"ゲーム終了！勝者は {game.winner} です！")
            break
        elif game.is_draw():
            game.display_board()
            print("ゲーム終了！引き分けです！")
            break

    # リセットオプション
    while True:
        reset = input("もう一度プレイしますか？ (y/n): ").lower()
        if reset == 'y':
            game.reset_game()
            main()  # 再帰的にゲームを再スタート
            break
        elif reset == 'n':
            print("ゲームを終了します。ありがとうございました！")
            break
        else:
            print("無効な入力です。'y' または 'n' を入力してください。")

if __name__ == "__main__":
    main()