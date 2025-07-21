import gymnasium as gym
from gymnasium import spaces
import numpy as np
import math
import random

WIDTH, HEIGHT = 800, 600

class AsteroidsEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(self, render_mode=None, max_asteroids=7):
        super().__init__()

        self.render_mode = render_mode
        self.max_asteroids = max_asteroids
        self.ship_radius = 25

        # Actions: [left, right, thrust, shoot] → binary
        self.action_space = spaces.MultiBinary(4)

        # Observations: ship (x,y,vx,vy,angle,lives) + asteroids
        obs_dim = 6 + self.max_asteroids * 5
        self.observation_space = spaces.Box(0, 1, (obs_dim,), np.float32)

        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.ship = {
            'x': WIDTH // 2,
            'y': HEIGHT // 2,
            'vx': 0,
            'vy': 0,
            'angle': 0,
            'lives': 3,
            'invulnerable': 0,
        }
        self.bullets = []
        self.asteroids = [self._spawn_asteroid() for _ in range(self.max_asteroids)]
        self.done = False
        self.score = 0

        return self._get_obs(), {}

    def step(self, action):
        reward = -0.01
        if self.done:
            return self._get_obs(), reward, True, False, {}

        if action[0]: self.ship['angle'] -= 5
        if action[1]: self.ship['angle'] += 5
        if action[2]: self._thrust()
        if action[3] and len(self.bullets) < 5:
            self.bullets.append(self._fire_bullet())

        # Ship update
        self.ship['x'] = (self.ship['x'] + self.ship['vx']) % WIDTH
        self.ship['y'] = (self.ship['y'] + self.ship['vy']) % HEIGHT
        self.ship['vx'] *= 0.9
        self.ship['vy'] *= 0.9
        if self.ship['invulnerable'] > 0:
            self.ship['invulnerable'] -= 1

        # Bullets update
        for b in self.bullets[:]:
            b['x'] += b['vx']
            b['y'] += b['vy']
            if not (0 <= b['x'] <= WIDTH and 0 <= b['y'] <= HEIGHT):
                self.bullets.remove(b)

        # Asteroids update
        for asteroid in self.asteroids:
            asteroid['x'] = (asteroid['x'] + asteroid['vx']) % WIDTH
            asteroid['y'] = (asteroid['y'] + asteroid['vy']) % HEIGHT

        # Bullet–asteroid collisions
        for b in self.bullets[:]:
            for a in self.asteroids[:]:
                if self._dist(b, a) < a['size']:
                    self.bullets.remove(b)
                    self.asteroids.remove(a)
                    self.score += a['score']
                    reward += a['score'] / 10
                    self.asteroids.extend(self._break_apart(a))
                    break

        # Ship–asteroid collisions
        if self.ship['invulnerable'] == 0:
            for a in self.asteroids:
                if self._dist(self.ship, a) < self.ship_radius + a['size']:
                    self.ship['lives'] -= 1
                    reward -= 50
                    if self.ship['lives'] <= 0:
                        self.done = True
                        reward -= 100
                    else:
                        self.ship['x'], self.ship['y'] = WIDTH//2, HEIGHT//2
                        self.ship['vx'], self.ship['vy'] = 0,0
                        self.ship['invulnerable'] = 120
                        self.bullets.clear()
                    break

        obs = self._get_obs()
        terminated = self.done
        truncated = False
        info = {}

        return obs, reward, terminated, truncated, info

    def render(self, mode="human"):
        if mode != "human": return
        import pygame
        if not hasattr(self, 'screen'):
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            self.clock = pygame.time.Clock()

        self.screen.fill((0, 0, 0))
        WHITE = (255, 255, 255)

        # ship
        if self.ship['invulnerable'] == 0 or (self.ship['invulnerable'] // 10) % 2 == 0:
            x, y, angle = self.ship['x'], self.ship['y'], self.ship['angle']
            rad = math.radians(angle)
            tip = (x + math.cos(rad) * 20, y + math.sin(rad) * 20)
            left = (x + math.cos(rad + 2.5) * 20, y + math.sin(rad + 2.5) * 20)
            right = (x + math.cos(rad - 2.5) * 20, y + math.sin(rad - 2.5) * 20)
            pygame.draw.polygon(self.screen, WHITE, [tip, left, right])

        # bullets
        for b in self.bullets:
            pygame.draw.circle(self.screen, WHITE, (int(b['x']), int(b['y'])), 2)

        # asteroids
        for a in self.asteroids:
            pygame.draw.circle(self.screen, WHITE, (int(a['x']), int(a['y'])), int(a['size']))

        pygame.display.flip()
        self.clock.tick(60)

    def close(self):
        if hasattr(self, 'screen'):
            import pygame
            pygame.quit()

    # ===== helpers ======

    def _get_obs(self):
        s = self.ship
        obs = [
            s['x'] / WIDTH, s['y'] / HEIGHT,
            (s['vx']+5)/10, (s['vy']+5)/10,
            s['angle'] / 360,
            s['lives'] / 3
        ]
        for i in range(self.max_asteroids):
            if i < len(self.asteroids):
                a = self.asteroids[i]
                obs.extend([
                    a['x'] / WIDTH, a['y'] / HEIGHT,
                    (a['vx']+5)/10, (a['vy']+5)/10,
                    a['size'] / 40
                ])
            else:
                obs.extend([0,0,0,0,0])
        return np.array(obs, dtype=np.float32)

    def _thrust(self):
        rad = math.radians(self.ship['angle'] - 90)
        self.ship['vx'] += math.cos(rad) * 0.2
        self.ship['vy'] += math.sin(rad) * 0.2

    def _fire_bullet(self):
        rad = math.radians(self.ship['angle'] - 90)
        return {
            'x': self.ship['x'],
            'y': self.ship['y'],
            'vx': math.cos(rad) * 5,
            'vy': math.sin(rad) * 5,
        }

    def _spawn_asteroid(self):
        size = random.randint(15,40)
        if size > 30:
            speed = random.uniform(1.5, 2.0)
        elif 20 < size <= 30:
            speed = random.uniform(2.0, 2.5)
        else:
            speed = random.uniform(2.5, 3.0)

        x, y = random.randint(0,WIDTH), random.randint(0,HEIGHT)
        angle = random.uniform(0, 2*math.pi)
        vx, vy = math.cos(angle)*speed, math.sin(angle)*speed
        score = 10 if size<20 else 20 if size<30 else 50
        return {'x':x, 'y':y, 'vx':vx, 'vy':vy, 'size':size, 'score':score}

    def _break_apart(self, asteroid):
        children = []
        if asteroid['size'] > 30:
            for _ in range(2):
                a = self._spawn_asteroid()
                a['size'] = random.randint(21,30)
                a['x'],a['y']=asteroid['x'],asteroid['y']
                a['score']=20
                children.append(a)
        elif 20 < asteroid['size'] <= 30:
            for _ in range(2):
                a = self._spawn_asteroid()
                a['size'] = random.randint(15,20)
                a['x'],a['y']=asteroid['x'],asteroid['y']
                a['score']=10
                children.append(a)
        return children

    def _dist(self, o1, o2):
        return math.hypot(o1['x']-o2['x'], o1['y']-o2['y'])
