class Brick:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hit = False

    def draw(self, surface):
        if not self.is_hit:
            pygame.draw.rect(surface, (255, 0, 0), self.rect)

    def check_collision(self, ball):
        if self.rect.colliderect(ball.rect) and not self.is_hit:
            self.is_hit = True
            ball.reverse_direction()
            return True
        return False