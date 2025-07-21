from stable_baselines3 import PPO
from reinforcement_learning.asteroids_env import AsteroidsEnv
import os

env = AsteroidsEnv()
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=500_000)

BASE_DIR = os.path.dirname(__file__)  # directory of this script
MODEL_PATH = os.path.join(BASE_DIR, "model", "ppo_asteroids")

model.save(MODEL_PATH)

# obs, _ = env.reset()
# done = False
# while not done:
#     action, _ = model.predict(obs)
#     obs, reward, done, _, _ = env.step(action)
#     env.render()
