class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed_x = 5
        self.speed_y = -5

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def bounce(self):
        self.speed_y = -self.speed_y

    def reset_position(self, x, y):
        self.x = x
        self.y = y

    def check_collision(self, paddle):
        if (self.x + self.radius > paddle.x and
            self.x - self.radius < paddle.x + paddle.width and
            self.y + self.radius > paddle.y and
            self.y - self.radius < paddle.y + paddle.height):
            self.bounce()

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)