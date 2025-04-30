import pygame
import sys

# --- 定数 ---
# 画面サイズ
WIDTH = 520 # マスサイズ * マス数 + 余白など
HEIGHT = 600 # スコア表示などのため縦長に
# 盤面
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // (COLS + 1) # マスの一辺のサイズ (左右に少し余白をもたせる)
BOARD_OFFSET_X = SQUARE_SIZE // 2
BOARD_OFFSET_Y = SQUARE_SIZE // 2

# 色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0) # 有効な手を示す色
RED = (255, 0, 0)

# プレイヤー
EMPTY = 0
BLACK_PLAYER = 1
WHITE_PLAYER = 2

# --- ゲーム盤クラス ---
class Board:
    def __init__(self):
        self.board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        # 初期配置
        self.board[3][3] = WHITE_PLAYER
        self.board[3][4] = BLACK_PLAYER
        self.board[4][3] = BLACK_PLAYER
        self.board[4][4] = WHITE_PLAYER
        self.black_score = 2
        self.white_score = 2

    def draw_squares(self, screen):
        """盤面のマス目を描画"""
        screen.fill(GREEN)
        for row in range(ROWS):
            for col in range(COLS):
                pygame.draw.rect(screen, BLACK, (BOARD_OFFSET_X + col * SQUARE_SIZE, BOARD_OFFSET_Y + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 1)

    def draw_pieces(self, screen):
        """盤面の石を描画"""
        radius = SQUARE_SIZE // 2 - 5
        for row in range(ROWS):
            for col in range(COLS):
                center_x = BOARD_OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = BOARD_OFFSET_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2
                if self.board[row][col] == BLACK_PLAYER:
                    pygame.draw.circle(screen, BLACK, (center_x, center_y), radius)
                elif self.board[row][col] == WHITE_PLAYER:
                    pygame.draw.circle(screen, WHITE, (center_x, center_y), radius)

    def is_valid_move(self, player, row, col):
        """(row, col) が player にとって有効な手か判定し、ひっくり返せる石のリストを返す"""
        if not (0 <= row < ROWS and 0 <= col < COLS and self.board[row][col] == EMPTY):
            return [] # マス外か、既に石がある場合は無効

        opponent = WHITE_PLAYER if player == BLACK_PLAYER else BLACK_PLAYER
        tiles_to_flip = []

        # 8方向をチェック
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            temp_flip = []
            r, c = row + dr, col + dc

            # 1. 隣が相手の石か？
            if 0 <= r < ROWS and 0 <= c < COLS and self.board[r][c] == opponent:
                temp_flip.append((r, c))
                r += dr
                c += dc
                # 2. その先に相手の石が続くか？
                while 0 <= r < ROWS and 0 <= c < COLS and self.board[r][c] == opponent:
                    temp_flip.append((r, c))
                    r += dr
                    c += dc
                # 3. 最後に自分の石があるか？
                if 0 <= r < ROWS and 0 <= c < COLS and self.board[r][c] == player:
                    tiles_to_flip.extend(temp_flip) # ひっくり返すリストに追加

        return tiles_to_flip # ひっくり返せる石がなければ空リストが返る

    def get_valid_moves(self, player):
        """player が打てる全ての有効な手のリストを返す"""
        valid_moves = {} # { (row, col): [flip_list], ... }
        for r in range(ROWS):
            for c in range(COLS):
                flip_list = self.is_valid_move(player, r, c)
                if flip_list: # 空リストでなければ有効な手
                    valid_moves[(r, c)] = flip_list
        return valid_moves

    def make_move(self, player, row, col, tiles_to_flip):
        """石を置き、指定された石をひっくり返す"""
        if not tiles_to_flip and self.board[row][col] != EMPTY: # is_valid_move でチェック済みのはずだが念のため
             print(f"エラー: 無効な手が make_move に渡されました: ({row}, {col})")
             return False

        self.board[row][col] = player
        for r_flip, c_flip in tiles_to_flip:
            self.board[r_flip][c_flip] = player
        self.update_score()
        return True

    def update_score(self):
        """現在のスコアを計算し更新"""
        self.black_score = 0
        self.white_score = 0
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c] == BLACK_PLAYER:
                    self.black_score += 1
                elif self.board[r][c] == WHITE_PLAYER:
                    self.white_score += 1

    def get_score(self):
        return self.black_score, self.white_score

# --- ゲーム管理クラス ---
class OthelloGame:
    def __init__(self, screen):
        self.screen = screen
        self.board = Board()
        self.current_player = BLACK_PLAYER # 黒から開始
        self.valid_moves = self.board.get_valid_moves(self.current_player)
        self.game_over = False
        self.winner = None
        self.font = pygame.font.SysFont("sansserif", 30)
        self.small_font = pygame.font.SysFont("sansserif", 20)
        pygame.font.init() # フォントモジュールを初期化 (念のため)
        # 日本語対応フォントを指定
        font_name = "Noto Serif CJK JP" # ここをシステムで見つかったフォント名に置き換える
        try:
            self.font = pygame.font.SysFont(font_name, 20)
            self.small_font = pygame.font.SysFont(font_name, 10)
            print(f"フォント '{font_name}' をロードしました。") # 確認用
        except Exception as e:
             print(f"警告: フォント '{font_name}' のロードに失敗しました。デフォルトフォントを使用します。エラー: {e}")
             # フォールバックとしてデフォルトを使う (文字化けする可能性あり)
             self.font = pygame.font.Font(None, 20)
             self.small_font = pygame.font.Font(None, 10)

    def switch_player(self):
        """プレイヤーを交代する"""
        self.current_player = WHITE_PLAYER if self.current_player == BLACK_PLAYER else BLACK_PLAYER
        self.valid_moves = self.board.get_valid_moves(self.current_player)

        # --- パスとゲーム終了判定 ---
        if not self.valid_moves: # 新しいプレイヤーに有効な手がない場合
            opponent = WHITE_PLAYER if self.current_player == BLACK_PLAYER else BLACK_PLAYER
            opponent_valid_moves = self.board.get_valid_moves(opponent)
            if not opponent_valid_moves: # 相手にも有効な手がない場合 -> ゲーム終了
                self.game_over = True
                b_score, w_score = self.board.get_score()
                if b_score > w_score:
                    self.winner = BLACK_PLAYER
                elif w_score > b_score:
                    self.winner = WHITE_PLAYER
                else:
                    self.winner = EMPTY # 引き分け
            else:
                # パス: 相手にターンを戻す（実際には何もしないで次のループで判定させる）
                print(f"{'黒' if self.current_player == BLACK_PLAYER else '白'} のパス。相手のターンです。")
                # Note: 実際にはもう一度 switch_player() を呼ぶか、
                #       次のループで相手が操作できるように current_player を戻す必要がある。
                #       ここでは簡単化のため、メッセージ表示のみ。次のクリック判定へ。
                #       より正確には、パスしたら自動で相手のvalid_movesを再計算すべき。
                #       今回は単純化し、パス表示後、相手がクリックするのを待つ形に。
                self.current_player = opponent # 相手に戻す
                self.valid_moves = opponent_valid_moves


    def handle_click(self, pos):
        """クリックイベントを処理"""
        if self.game_over:
            return

        # 画面座標から盤面座標へ変換
        col = (pos[0] - BOARD_OFFSET_X) // SQUARE_SIZE
        row = (pos[1] - BOARD_OFFSET_Y) // SQUARE_SIZE

        if (row, col) in self.valid_moves:
            tiles_to_flip = self.valid_moves[(row, col)]
            if self.board.make_move(self.current_player, row, col, tiles_to_flip):
                self.switch_player()


    def draw_valid_moves(self):
        """有効な手を小さな円で表示"""
        radius = SQUARE_SIZE // 8
        for r, c in self.valid_moves.keys():
             center_x = BOARD_OFFSET_X + c * SQUARE_SIZE + SQUARE_SIZE // 2
             center_y = BOARD_OFFSET_Y + r * SQUARE_SIZE + SQUARE_SIZE // 2
             pygame.draw.circle(self.screen, GOLD, (center_x, center_y), radius)

    def draw_status(self):
        """スコア、ターン、結果などを描画"""
        b_score, w_score = self.board.get_score()
        score_text = f"黒: {b_score}  白: {w_score}"
        score_surf = self.font.render(score_text, True, BLACK)
        score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.screen.blit(score_surf, score_rect)

        if not self.game_over:
            turn_text = f"ターン: {'黒' if self.current_player == BLACK_PLAYER else '白'}"
            turn_surf = self.font.render(turn_text, True, BLACK if self.current_player == BLACK_PLAYER else WHITE)
            turn_rect = turn_surf.get_rect(center=(WIDTH // 2, HEIGHT - 30))
            # 背景色を設定して文字を見やすくする（オプション）
            text_bg_rect = turn_rect.inflate(10, 5) # 少し大きめの背景矩形
            pygame.draw.rect(self.screen, GRAY, text_bg_rect, border_radius=5)
            self.screen.blit(turn_surf, turn_rect)

            # パスに関する注意書き (簡易版)
            pass_info = "打てる場所がない場合は自動でパスにはなりません (相手がクリックしてください)"
            pass_surf = self.small_font.render(pass_info, True, RED)
            pass_rect = pass_surf.get_rect(center=(WIDTH // 2, HEIGHT - 10))
            # self.screen.blit(pass_surf, pass_rect) # 必要ならコメント解除


        else:
            result_text = ""
            if self.winner == BLACK_PLAYER:
                result_text = "黒の勝ち！"
            elif self.winner == WHITE_PLAYER:
                result_text = "白の勝ち！"
            else:
                result_text = "引き分け"
            result_surf = self.font.render(result_text, True, RED)
            result_rect = result_surf.get_rect(center=(WIDTH // 2, HEIGHT - 30))
            self.screen.blit(result_surf, result_rect)

    def run(self):
        """メインループを実行"""
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            # 描画処理
            self.board.draw_squares(self.screen)
            self.board.draw_pieces(self.screen)
            if not self.game_over:
                 self.draw_valid_moves()
            self.draw_status()

            # 画面更新
            pygame.display.flip()
            clock.tick(60) # FPS

        pygame.quit()
        sys.exit()

# --- メイン処理 ---
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("シンプルオセロ")
    game = OthelloGame(screen)
    game.run()