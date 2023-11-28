import os
from Simulation.airport import Airport
import simpy
import random


# Generate random seeds
random_seeds = [i for i in range(30, 37)]


def simulate_airport(airport, env):
    """Function to simulate a week of departures/landings at an airport"""

    # Iterate over the course of 8 days
    for i in range(0, int(os.getenv("NUM_REPLICATIONS"))):
        print(f"Beginning Day: {i}")
        if i > 0:
            # Reset airport params
            new_env = simpy.Environment()
            airport.env = new_env
            airport.reset_runways()
            airport.reset_wind()

            # Run simulation
            new_env.process(airport.simulate())
            new_env.run(24*60)
        else:
            env.process(airport.simulate())
            env.run(until=24*60)
        print(f"Finished Day: {i}")


# Run simulation
if __name__ == '__main__':
    env = simpy.Environment()
    logan_airport = Airport(env)
    simulate_airport(logan_airport, env)
    logan_airport.save_simulation_data()
