import traci

# Start SUMO with GUI
traci.start(["sumo-gui", "-c", "junction.sumocfg"])

# Lane IDs (incoming lanes)
lanes = ["north_in", "south_in", "east_in", "west_in"]

step = 0
try:
    while step < 200:  # run for 200 simulation steps (seconds)
        traci.simulationStep()

        # Get vehicle counts for each lane
        counts = [traci.lane.getLastStepVehicleNumber(lane) for lane in lanes]
        print(f"Step {step}: {counts}")

        step += 1
finally:
    traci.close()
