from stable_baselines3 import PPO
from reinforcement_learning.asteroids_env import AsteroidsEnv
import numpy as np
import csv
import os

BASE_DIR = os.path.dirname(__file__)  # directory of this script
MODEL_PATH = os.path.join(BASE_DIR, "model", "ppo_asteroids")
RESULTS_PATH = os.path.join(BASE_DIR, "results", "evaluation_results.csv")

N_EPISODES = 10

# 🎮 Load environment & agent
env = AsteroidsEnv(render_mode="human")
model = PPO.load(MODEL_PATH)

# 📈 Evaluate trained agent
agent_scores = []
for ep in range(N_EPISODES):
    obs, info = env.reset()
    done, score = False, 0
    while not done:
        action, _ = model.predict(obs)
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        score += reward
        env.render()
    agent_scores.append(score)
    print(f"[Agent] Episode {ep+1}: score = {score:.2f}")

print(f"\n[Agent] Average score: {np.mean(agent_scores):.2f} ± {np.std(agent_scores):.2f}\n")

# 🤖 Evaluate random policy
random_scores = []
for ep in range(N_EPISODES):
    obs, info = env.reset()
    done, score = False, 0
    while not done:
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        score += reward
    random_scores.append(score)
    print(f"[Random] Episode {ep+1}: score = {score:.2f}")

print(f"\n[Random] Average score: {np.mean(random_scores):.2f} ± {np.std(random_scores):.2f}")

env.close()

# 📝 Save results to CSV
with open(RESULTS_PATH, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Episode", "Agent Score", "Random Score"])
    for i in range(N_EPISODES):
        writer.writerow([i+1, agent_scores[i], random_scores[i]])

print("\n✅ Results saved to `evaluation_results.csv`")
