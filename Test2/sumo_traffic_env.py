import numpy as np
import traci  # SUMO Python API
import gym
from gym import spaces

class SumoTrafficEnv(gym.Env):
    def __init__(self):
        super(SumoTrafficEnv, self).__init__()
        
        # Observation space: [N, S, E, W, current_phase, min_steps]
        self.observation_space = spaces.Box(
            low=0, high=1000, shape=(6,), dtype=np.float32
        )

        # Action space: 0 = stay in same phase, 1 = switch phase
        self.action_space = spaces.Discrete(2)

        self.current_phase = 0
        self.min_steps = 0
        self.time_since_change = 0

    def _get_state(self):
        """Extract traffic state from SUMO"""
        N = traci.edge.getLastStepVehicleNumber("north_in")
        S = traci.edge.getLastStepVehicleNumber("south_in")
        E = traci.edge.getLastStepVehicleNumber("east_in")
        W = traci.edge.getLastStepVehicleNumber("west_in")

        return np.array([N, S, E, W, self.current_phase, self.min_steps], dtype=np.float32)

    def step(self, action):
        reward = 0

        # Enforce minimum steps before changing phase
        if self.min_steps > 0:
            self.min_steps -= 1
            action = 0  # Force same phase

        if action == 1 and self.min_steps == 0:
            self.current_phase = (self.current_phase + 1) % 2
            traci.trafficlight.setPhase("junction_0", self.current_phase)
            self.min_steps = 5  # Minimum steps before switching again

        # Advance simulation
        traci.simulationStep()

        # Reward: negative queue length (we want to reduce queues)
        total_queue = sum([
            traci.edge.getLastStepVehicleNumber("north_in"),
            traci.edge.getLastStepVehicleNumber("south_in"),
            traci.edge.getLastStepVehicleNumber("east_in"),
            traci.edge.getLastStepVehicleNumber("west_in")
        ])
        reward = -total_queue

        state = self._get_state()
        done = traci.simulation.getMinExpectedNumber() <= 0

        return state, reward, done, {}

    def reset(self):
        traci.load(["-c", "junction.sumocfg"])
        self.current_phase = 0
        self.min_steps = 0
        return self._get_state()

    def close(self):
        traci.close()
