class Paddle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = 10

    def move_left(self):
        self.rect.x -= self.speed
        if self.rect.x < 0:
            self.rect.x = 0

    def move_right(self):
        self.rect.x += self.speed
        if self.rect.x > (SCREEN_WIDTH - self.rect.width):
            self.rect.x = SCREEN_WIDTH - self.rect.width

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)