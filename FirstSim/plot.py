import traci
import os

# --- CONFIG ---
config_path = "./junction.sumocfg"  # change to your actual path
lanes = ["north_in", "south_in", "east_in", "west_in"]
tl_id = "TL1"  # change to your actual traffic light ID in net.xml

# --- Start SUMO GUI ---
traci.start(["sumo-gui", "-c", config_path])

step = 0
green_start_step = 0
last_green_lane_index = None

try:
    while step < 200:
        traci.simulationStep()

        # 1. Vehicle counts for the 4 incoming lanes
        counts = [traci.lane.getLastStepVehicleNumber(lane) for lane in lanes]

        # 2. Determine which lane is currently green
        phase_index = traci.trafficlight.getPhase(tl_id)  # integer index of phase
        green_lane_index = phase_index % 4  # assuming one lane per phase in order N,S,E,W

        # 3. Track how long green has been active
        if green_lane_index != last_green_lane_index:
            green_start_step = step
            last_green_lane_index = green_lane_index
        green_duration = step - green_start_step

        # 4. Build state array
        state = counts + [green_lane_index, green_duration]
        print(f"Step {step}: {state}")

        step += 1

finally:
    traci.close()
