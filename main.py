import pygame
import math
import random

# Initialize
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")
clock = pygame.time.Clock()

# image by Kai Pilger
background = pygame.image.load("assets/space-background.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# image by manshagraphicss
spaceship = pygame.image.load("assets/spaceship.png").convert_alpha()
spaceship = pygame.transform.scale(spaceship, (50, 50))

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Ship class
class Ship:
    def __init__(self, image):
        self.img = image
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 0
        self.speed = 0

        self.vel_x = 0
        self.vel_y = 0
        # self.dir_x = 0
        # self.dir_y = -1

    def rotate(self, direction):
        self.angle += direction * 5  # degrees

    def thrust(self):
        rad = math.radians(self.angle - 90)
        self.vel_x += math.cos(rad) * 0.2
        self.vel_y += math.sin(rad) * 0.2

    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y

        # Screen wrap-around
        self.x %= WIDTH
        self.y %= HEIGHT
        self.vel_x *= 0.9
        self.vel_y *= 0.9

    def draw(self):
        # rotate the image
        rotated_image = pygame.transform.rotate(self.img, -self.angle)  # negative because pygame y-axis is inverted
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
ship = Ship(spaceship)
bullets = []
asteroids = [Asteroid() for _ in range(5)]

running = True
while running:
    clock.tick(60)  # 60 FPS
    screen.blit(background, (0, 0))

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
