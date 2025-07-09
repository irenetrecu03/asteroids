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
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 4)

# Asteroid class
class Asteroid:
    def __init__(self, image):
        self.size = random.randint(15, 40)
        self.img = pygame.transform.scale(image, (self.size*2, self.size*2))

        # calculate score of the asteroid based on size
        self.score = 10 if self.size < 20 else 20 if (20 < self.size < 30) else 50

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

    def break_apart(self):
        new_asteroids = []
        if self.size > 30:
            for _ in range(2):
                a = Asteroid(asteroid_img)
                a.size = random.randint(21, 30)
                a.img = pygame.transform.scale(asteroid_img, (a.size * 2, a.size * 2))
                a.x, a.y = self.x, self.y
                new_asteroids.append(a)
        elif 20 < self.size <= 30:
            for _ in range(2):
                a = Asteroid(asteroid_img)
                a.size = random.randint(15, 20)
                a.img = pygame.transform.scale(asteroid_img, (a.size * 2, a.size * 2))
                a.x, a.y = self.x, self.y
                new_asteroids.append(a)
        return new_asteroids

    def draw(self):
        rect = self.img.get_rect(center=(self.x, self.y))
        screen.blit(self.img, rect.topleft)

# Game setup
NUM_ASTEROIDS = 7
ship = Ship(spaceship)
bullets = []
asteroids = [Asteroid(asteroid_img) for _ in range(NUM_ASTEROIDS)]

GAMEOVER = False
RESTART_KEY = pygame.K_RETURN

# initialise player's score
SCORE = 0

running = True
while running:
    clock.tick(60)
    screen.blit(background, (0, 0))

    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # fire one bullet when pressing space
            if event.key == pygame.K_SPACE and not GAMEOVER:
                if len(bullets) < 5:
                    bullets.append(Bullet(ship.x, ship.y, ship.angle - 90))
            # restart game after failing and pressing Enter
            elif event.key == RESTART_KEY and GAMEOVER:
                # Reset game
                GAMEOVER = False
                ship = Ship(spaceship)
                bullets = []
                asteroids = [Asteroid(asteroid_img) for _ in range(NUM_ASTEROIDS)]
                SCORE = 0

    if not GAMEOVER:
        if keys[pygame.K_LEFT]: ship.rotate(-1) # rotate ship to the left
        if keys[pygame.K_RIGHT]: ship.rotate(1) # rotate ship to the right
        if keys[pygame.K_UP]: ship.thrust() # move ship forward

        # Update
        ship.move()
        for bullet in bullets[:]:
            bullet.move()
            # remove out-of-bounds bullets
            if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
                bullets.remove(bullet)

        for ast_idx, asteroid in enumerate(asteroids[:]):
            asteroid.move()

            # bullet-asteroid collision check
            for bullet_idx, bullet in enumerate(bullets[:]):
                dist_bullet_asteroid = math.hypot(asteroid.x - bullet.x, asteroid.y - bullet.y)
                if dist_bullet_asteroid < 20 + asteroid.size:
                    SCORE += asteroid.score
                    del asteroids[ast_idx]
                    del bullets[bullet_idx]
                    new_asteroids = asteroid.break_apart()
                    asteroids.extend(new_asteroids)
                    break

            # ship-asteroid collision check
            dist_ship_asteroid = math.hypot(ship.x - asteroid.x, ship.y - asteroid.y)
            if dist_ship_asteroid < 25 + asteroid.size:
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

    score_font = pygame.font.SysFont("monospace", 30)
    score_text = score_font.render(f"Score: {SCORE}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

pygame.quit()
