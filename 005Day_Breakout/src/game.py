import os
import pygame

class Game:
    def __init__(self):
        self.running = True
        self.score = 0
        self.lives = 3
        self.bricks = []
        self.paddle = None
        self.ball = None
        self.screen = pygame.display.set_mode((800, 600))  # Initialize screen

        # サウンドの読み込み
        base_path = os.path.join(os.path.dirname(__file__), "assets")
        self.bounce_sound = pygame.mixer.Sound(os.path.join(base_path, "sounds/bounce.wav"))
        self.brick_break_sound = pygame.mixer.Sound(os.path.join(base_path, "sounds/brick_break.wav"))

        # フォントの読み込み
        self.font_path = os.path.join(base_path, "fonts/NotoSansJP-Regular.ttf")
        self.info_font = pygame.font.Font(self.font_path, 20)  # フォントサイズ20

    def initialize(self):
        # パドルの初期化
        self.paddle = pygame.Rect(350, 550, 100, 10)  # x, y, width, height

        # ボールの初期化
        self.ball = pygame.Rect(390, 540, 10, 10)  # x, y, width, height
        self.ball_speed = [4, -4]  # x方向とy方向の速度

        # ブロックの初期化
        self.bricks = []
        for row in range(5):  # 5行
            for col in range(10):  # 10列
                brick = pygame.Rect(10 + col * 78, 10 + row * 30, 70, 20)  # x, y, width, height
                self.bricks.append(brick)

    def update(self):
        # ボールの移動
        self.ball.x += self.ball_speed[0]
        self.ball.y += self.ball_speed[1]

        # 壁との衝突判定
        if self.ball.left <= 0 or self.ball.right >= 800:
            self.ball_speed[0] = -self.ball_speed[0]  # x方向の反転
        if self.ball.top <= 0:
            self.ball_speed[1] = -self.ball_speed[1]  # y方向の反転
        if self.ball.bottom >= 600:
            self.lives -= 1  # ライフを減らす
            self.reset()  # リセット

        # パドルとの衝突判定
        if self.ball.colliderect(self.paddle):
            self.ball_speed[1] = -self.ball_speed[1]  # y方向の反転
            self.bounce_sound.play()  # サウンドを再生

        # ブロックとの衝突判定
        for brick in self.bricks[:]:
            if self.ball.colliderect(brick):
                self.bricks.remove(brick)  # ブロックを削除
                self.ball_speed[1] = -self.ball_speed[1]  # y方向の反転
                self.score += 10  # スコアを加算
                self.brick_break_sound.play()  # サウンドを再生
                break

    def draw(self, screen):
        # パドルを描画
        pygame.draw.rect(screen, (255, 255, 255), self.paddle)

        # ボールを描画
        pygame.draw.ellipse(screen, (255, 255, 255), self.ball)

        # ブロックを描画
        for brick in self.bricks:
            pygame.draw.rect(screen, (255, 0, 0), brick)

        # スコアを描画
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        # ライフを描画
        for i in range(self.lives):  # ライフの数だけ描画
            pygame.draw.rect(screen, (0, 255, 0), (700 + i * 30, 10, 20, 20))  # x, y, width, height

        # OtoLogicの素材利用表記を描画
        info_text = self.info_font.render("パドルの弾く音はOtoLogicの素材を使用している", True, (255, 255, 255))
        screen.blit(info_text, (10, 570))  # 画面下部に表示

    def handle_input(self):
        # Handle user input for paddle movement
        pass

    def reset(self):
        # ボールとパドルを初期位置に戻す
        self.ball.x, self.ball.y = 390, 540
        self.ball_speed = [4, -4]
        self.paddle.x = 350

    def check_game_over(self):
        if self.lives <= 0:  # ライフが0になった場合
            font = pygame.font.Font(None, 72)
            text = font.render("Game Over", True, (255, 0, 0))
            self.screen.blit(text, (300, 250))
            pygame.display.flip()
            pygame.time.wait(3000)  # 3秒間待機
            self.running = False
        elif not self.bricks:  # ブロックがすべて消えた場合
            font = pygame.font.Font(None, 72)
            text = font.render("You Win!", True, (255, 255, 255))
            self.screen.blit(text, (300, 250))
            pygame.display.flip()
            pygame.time.wait(3000)  # 3秒間待機
            self.running = False

    def run(self):
        self.initialize()  # ゲームの初期化
        clock = pygame.time.Clock()  # フレームレート制御用のClockオブジェクトを作成

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # 入力処理
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.paddle.left > 0:
                self.paddle.x -= 5  # 移動速度を 3 に変更
            if keys[pygame.K_RIGHT] and self.paddle.right < 800:
                self.paddle.x += 5  # 移動速度を 3 に変更

            # ゲーム状態の更新
            self.update()
            self.check_game_over()

            # 描画
            self.screen.fill((0, 0, 0))  # 背景を黒で塗りつぶす
            self.draw(self.screen)
            pygame.display.flip()

            # フレームレートを制限 (例: 60FPS)
            clock.tick(60)

def main():
    pygame.init()
    pygame.mixer.init()  # サウンドシステムの初期化
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
