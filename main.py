import pygame
import math
import random

# Initialize
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Ship class
class Ship:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 0
        self.speed = 0

        self.vel_x = 0
        self.vel_y = 0

    def rotate(self, direction):
        self.angle += direction * 5  # degrees

    def thrust(self):
        rad = math.radians(self.angle)
        self.vel_x += math.cos(rad) * 0.2
        self.vel_y += math.sin(rad) * 0.2

    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y

        # Screen wrap-around
        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self):
        rad = math.radians(self.angle)
        point1 = (self.x + math.cos(rad) * 20, self.y + math.sin(rad) * 20)
        rad_left = math.radians(self.angle + 140)
        rad_right = math.radians(self.angle - 140)
        point2 = (self.x + math.cos(rad_left) * 20, self.y + math.sin(rad_left) * 20)
        point3 = (self.x + math.cos(rad_right) * 20, self.y + math.sin(rad_right) * 20)

        pygame.draw.polygon(screen, WHITE, [point1, point2, point3])

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
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vel_x = random.uniform(-1.5, 1.5)
        self.vel_y = random.uniform(-1.5, 1.5)
        self.size = random.randint(15, 40)

    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)

# Game setup
ship = Ship()
bullets = []
asteroids = [Asteroid() for _ in range(5)]

running = True
while running:
    clock.tick(60)  # 60 FPS
    screen.fill(BLACK)

    # Input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        ship.rotate(-1)
    if keys[pygame.K_RIGHT]:
        ship.rotate(1)
    if keys[pygame.K_UP]:
        ship.thrust()
    if keys[pygame.K_SPACE]:
        if len(bullets) < 5:  # limit bullets
            bullets.append(Bullet(ship.x, ship.y, ship.angle))

    # Update
    ship.move()
    for bullet in bullets[:]:
        bullet.move()
        if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
            bullets.remove(bullet)

    for asteroid in asteroids:
        asteroid.move()

    # Draw
    ship.draw()
    for bullet in bullets:
        bullet.draw()
    for asteroid in asteroids:
        asteroid.draw()

    pygame.display.flip()

pygame.quit()
