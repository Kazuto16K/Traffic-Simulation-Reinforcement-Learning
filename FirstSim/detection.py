import traci

# Start SUMO with GUI
traci.start(["sumo-gui", "-c", "junction.sumocfg"])

lanes = ["north_in_0", "south_in_0", "east_in_0", "west_in_0"]
TL_ID = traci.trafficlight.getIDList()[0]

# Build phase states dynamically
def build_state(ns_green=False, ew_green=False, ns_yellow=False, ew_yellow=False):
    state = ""
    for link in traci.trafficlight.getControlledLinks(TL_ID):
        from_edge = link[0][0] if link else ""
        if from_edge.startswith("north_in") or from_edge.startswith("south_in"):
            if ns_green:
                state += "G"
            elif ns_yellow:
                state += "y"
            else:
                state += "r"
        elif from_edge.startswith("east_in") or from_edge.startswith("west_in"):
            if ew_green:
                state += "G"
            elif ew_yellow:
                state += "y"
            else:
                state += "r"
        else:
            state += "r"
    return state

# Phase definitions
phase0_state = build_state(ns_green=True)
phase0_yellow = build_state(ns_yellow=True)
phase1_state = build_state(ew_green=True)
phase1_yellow = build_state(ew_yellow=True)

# Timing settings
GREEN_MIN = 5     # min green time before switching
GREEN_MAX = 20    # max green time before forced switch
YELLOW_HOLD = 3
QUEUE_THRESHOLD = 2  # if total cars < threshold, switch early

# Phases: (state, min/max/yellow, id)
phase_order = [
    (phase0_state, 0),  # NS green
    (phase0_yellow, 0), # NS yellow
    (phase1_state, 1),  # EW green
    (phase1_yellow, 1)  # EW yellow
]

phase_index = 0
timer = 0
low_queue_timer = 0

step = 0
try:
    while step < 200:
        light_state, phase_id = phase_order[phase_index]
        traci.trafficlight.setRedYellowGreenState(TL_ID, light_state)

        traci.simulationStep()

        counts = [traci.lane.getLastStepVehicleNumber(lane) for lane in lanes]

        state_array = counts + [phase_id, timer]
        print(f"Step {step}: {state_array}")

        # Handle adaptive switching for green phases only
        if phase_index in [0, 2]:  # 0 = NS green, 2 = EW green
            active_lanes = [0, 1] if phase_id == 0 else [2, 3]
            total_cars = sum(counts[i] for i in active_lanes)

            if total_cars < QUEUE_THRESHOLD:
                low_queue_timer += 1
            else:
                low_queue_timer = 0

            if (timer >= GREEN_MIN and low_queue_timer >= 3) or timer >= GREEN_MAX:
                phase_index = (phase_index + 1) % len(phase_order)
                timer = 0
                low_queue_timer = 0
            else:
                timer += 1
        else:
            # Yellow phases
            if timer >= YELLOW_HOLD:
                phase_index = (phase_index + 1) % len(phase_order)
                timer = 0
            else:
                timer += 1

        step += 1

finally:
    traci.close()
