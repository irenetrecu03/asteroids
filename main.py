import pygame
import math
import random

# Initialize
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")
clock = pygame.time.Clock()

# Assets
background = pygame.image.load("assets/space-background.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

spaceship = pygame.image.load("assets/spaceship.png").convert_alpha()
spaceship = pygame.transform.scale(spaceship, (50, 50))

asteroid_img = pygame.image.load("assets/asteroid.png").convert_alpha()

WHITE = (255, 255, 255)

# Ship class
class Ship:
    def __init__(self, image):
        self.img = image
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 0
        self.vel_x = 0
        self.vel_y = 0

    def rotate(self, direction):
        self.angle += direction * 5

    def thrust(self):
        rad = math.radians(self.angle - 90)
        self.vel_x += math.cos(rad) * 0.2
        self.vel_y += math.sin(rad) * 0.2

    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.x %= WIDTH
        self.y %= HEIGHT
        self.vel_x *= 0.9
        self.vel_y *= 0.9

    def draw(self):
        rotated_image = pygame.transform.rotate(self.img, -self.angle)
        rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, rect.topleft)

# Bullet class
class Bullet:
    def __init__(self, x, y, angle):
        rad = math.radians(angle)
        self.x = x
        self.y = y
        self.vel_x = math.cos(rad) * 5
        self.vel_y = math.sin(rad) * 5

    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 2)

# Asteroid class
class Asteroid:
    def __init__(self, image):
        self.size = random.randint(15, 40)
        self.img = pygame.transform.scale(image, (self.size*2, self.size*2))
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        speed = random.uniform(1.5, 2.0)
        angle = random.uniform(0, 2 * math.pi)
        self.vel_x = math.cos(angle) * speed
        self.vel_y = math.sin(angle) * speed

    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self):
        rect = self.img.get_rect(center=(self.x, self.y))
        screen.blit(self.img, rect.topleft)

# Game setup
ship = Ship(spaceship)
bullets = []
asteroids = [Asteroid(asteroid_img) for _ in range(5)]

GAMEOVER = False
RESTART_KEY = pygame.K_RETURN

running = True
while running:
    clock.tick(60)
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if not GAMEOVER:
        # Input
        if keys[pygame.K_LEFT]:
            ship.rotate(-1)
        if keys[pygame.K_RIGHT]:
            ship.rotate(1)
        if keys[pygame.K_UP]:
            ship.thrust()
        if keys[pygame.K_SPACE]:
            if len(bullets) < 5:
                bullets.append(Bullet(ship.x, ship.y, ship.angle - 90))

        # Update
        ship.move()
        for bullet in bullets[:]:
            bullet.move()
            if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
                bullets.remove(bullet)

        for asteroid in asteroids:
            asteroid.move()

        # Collision check
        for asteroid in asteroids:
            dist = math.hypot(ship.x - asteroid.x, ship.y - asteroid.y)
            if dist < 25 + asteroid.size:
                GAMEOVER = True
                break

    # Draw
    ship.draw()
    for bullet in bullets:
        bullet.draw()
    for asteroid in asteroids:
        asteroid.draw()

    if GAMEOVER:
        font = pygame.font.SysFont("monospace", 60, bold=True)
        text = font.render("GAME OVER", True, (255, 0, 0))
        rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text, rect)

        small_font = pygame.font.SysFont("monospace", 30)
        restart_text = small_font.render("Press Enter to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_rect)

        if keys[RESTART_KEY]:
            # RESET GAME
            GAMEOVER = False
            ship = Ship(spaceship)
            bullets = []
            asteroids = [Asteroid(asteroid_img) for _ in range(5)]

    pygame.display.flip()

pygame.quit()
