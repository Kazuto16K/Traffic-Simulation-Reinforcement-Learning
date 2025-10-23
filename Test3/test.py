import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from sumo_traffic_env import SumoTrafficEnv  # Your SUMO environment class

# ======== PARAMETERS ========
MODEL_PATH = "dqn_traffic_model.h5"  # Saved model path
EPISODES = 10                   # Number of test runs
RENDER = False                  # Whether to visualize SUMO GUI

# ======== LOAD ENVIRONMENT ========
env = SumoTrafficEnv(gui=RENDER)

# ======== LOAD TRAINED MODEL ========
model = tf.keras.models.load_model(MODEL_PATH)

# ======== METRICS STORAGE ========
episode_rewards = []
avg_wait_times = []
total_vehicles = []

# ======== TEST LOOP ========
for episode in range(EPISODES):
    state = env.reset()
    done = False
    total_reward = 0
    total_wait_time = 0
    vehicle_count = 0

    while not done:
        # Select best action (no epsilon-greedy here)
        q_values = model.predict(np.expand_dims(state, axis=0), verbose=0)
        action = np.argmax(q_values[0])

        next_state, reward, done, info = env.step(action)

        # Collect metrics
        total_reward += reward
        total_wait_time += info.get("total_wait_time", 0)
        vehicle_count += info.get("vehicle_count", 0)

        state = next_state

    # Store results for plotting
    episode_rewards.append(total_reward)
    avg_wait_times.append(total_wait_time / max(vehicle_count, 1))
    total_vehicles.append(vehicle_count)

    print(f"Episode {episode+1}/{EPISODES} - "
          f"Reward: {total_reward:.2f} | "
          f"Avg Wait Time: {avg_wait_times[-1]:.2f} | "
          f"Vehicles: {vehicle_count}")

# ======== PLOT PERFORMANCE ========
plt.figure(figsize=(12, 4))

# Rewards
plt.subplot(1, 3, 1)
plt.plot(episode_rewards, marker='o')
plt.title("Total Rewards per Episode")
plt.xlabel("Episode")
plt.ylabel("Total Reward")

# Wait Times
plt.subplot(1, 3, 2)
plt.plot(avg_wait_times, marker='o', color='orange')
plt.title("Average Wait Time")
plt.xlabel("Episode")
plt.ylabel("Wait Time (s)")

# Vehicle Count
plt.subplot(1, 3, 3)
plt.plot(total_vehicles, marker='o', color='green')
plt.title("Vehicles Processed")
plt.xlabel("Episode")
plt.ylabel("Count")

plt.tight_layout()
plt.show()

env.close()
