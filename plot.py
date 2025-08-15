import traci
import matplotlib.pyplot as plt
from collections import deque

# Start SUMO
traci.start(["sumo-gui", "-c", "junction.sumocfg"])

# Data buffers (last 50 steps)
north_q = deque(maxlen=50)
south_q = deque(maxlen=50)
east_q  = deque(maxlen=50)
west_q  = deque(maxlen=50)

plt.ion()
fig, ax = plt.subplots()
lines = {
    "north": ax.plot([], [], label="North")[0],
    "south": ax.plot([], [], label="South")[0],
    "east":  ax.plot([], [], label="East")[0],
    "west":  ax.plot([], [], label="West")[0],
}
ax.set_ylim(0, 10)  # adjust depending on max vehicles
ax.legend()

for step in range(200):  # number of steps
    traci.simulationStep()

    n = traci.edge.getLastStepVehicleNumber("north_in")
    s = traci.edge.getLastStepVehicleNumber("south_in")
    e = traci.edge.getLastStepVehicleNumber("east_in")
    w = traci.edge.getLastStepVehicleNumber("west_in")

    north_q.append(n)
    south_q.append(s)
    east_q.append(e)
    west_q.append(w)

    # Update plot
    x_vals = range(len(north_q))
    lines["north"].set_data(x_vals, list(north_q))
    lines["south"].set_data(x_vals, list(south_q))
    lines["east"].set_data(x_vals, list(east_q))
    lines["west"].set_data(x_vals, list(west_q))
    ax.set_xlim(0, len(north_q))
    plt.pause(0.01)

traci.close()
