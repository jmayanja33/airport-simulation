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
        random.seed(random_seeds[i])

        if i > 0:
            new_env = simpy.Environment()
            airport.env = new_env
            new_env.process(airport.simulate())
            new_env.run(24*60)
        else:
            env.process(airport.simulate())
            env.run(until=24*60)


# Run simulation
if __name__ == '__main__':
    env = simpy.Environment()
    logan_airport = Airport(env)
    simulate_airport(logan_airport, env)
