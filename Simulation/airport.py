"""
Class to simulate a week's worth of flights at Logan airport.

Goals:
    - The goal of this project is to gain a better understanding of how plane traffic builds up around the runways at
    Logan Airport in Boston, and how well the airport can adapt to issues on runways. Using this simulation model,
    we can hopefully test different scenarios that will minimize the wait time for planes taking off, and minimize the
    time circling the airport for arriving aircraft.

Assumptions:
    - Weather is constant and ideal
    - Winds are constant for 24 hours, then can randomly change direction every the next day (could stay the same)
    - Taxi and Gate issues are not being considered. The focus of this project is on getting planes on and off of
    the ground efficiently.
    - All non-jet aircraft will take off and land only on non-jet specific runways if presented the opportunity
    - ATC will guide all planes to successful takeoffs/landings (no collisions)

Scenarios to be Tested:
    - Control: leave all data as is
    - Remove busiest runway
    - Remove top 2 busiest runways
    - Add a new runway
    - Add a new runway and remove 2 busiest runways

Process:
    - Departures leave gate/Arrivals begin approach (both randomly)
    - Departures/Arrivals pick runway with shortest line. Departures wait on ground, arrivals circle
    - Departures exit system, arrivals taxi to gate

"""
import pandas as pd
import simpy
import random
import statistics
import json
import os
import numpy as np
from dotenv import load_dotenv
from Data.final_data import probabilities, runways
from Simulation.plane import Plane
from Simulation.runway import Runway
from dotenv import load_dotenv


def find_wind_direction():
    """Function to define which way the wind is blowing"""
    directions = list(probabilities["Wind"].keys())
    direction_probabilities = [probabilities["Wind"][i] for i in probabilities["Wind"].keys()]
    wind = np.random.choice(directions, p=direction_probabilities)

    print(f"Setting wind direction to: {wind}")
    return wind


class Airport(object):

    def __init__(self, env, simulation_type):
        load_dotenv()

        self.env = env
        self.simulation_type = simulation_type
        self.ignore_runways = set(json.loads(os.environ['EXCLUDE_RUNWAYS']))
        self.wait_times = []
        self.circle_times = []
        self.wind_direction = find_wind_direction()
        self.runways = self.prepare_runways()
        self.non_jet_departure_runways, self.all_departure_runways = self.find_non_jet_runways(departure=True)
        self.non_jet_arrival_runways, self.all_arrival_runways = self.find_non_jet_runways(departure=False)

    def prepare_runways(self):
        """Function to setup which runways are being used"""
        print("Preparing runways")

        runways_in_use = {}

        departure_runways = runways[self.wind_direction]["Departures"]
        arrival_runways = runways[self.wind_direction]["Arrivals"]

        # Initialize departure runways
        for runway in departure_runways.keys():
            if runway not in self.ignore_runways:
                if departure_runways[runway]["Non Jet"]:
                    runways_in_use[runway] = Runway(self.env, runway, self.wait_times, self.circle_times,
                                                    departure=True, arrival=False, non_jet_departure=True)
                else:
                    runways_in_use[runway] = Runway(self.env, runway, self.wait_times, self.circle_times,
                                                    departure=True, arrival=False)

        # Initialize arrival runways
        for runway in arrival_runways.keys():
            if runway not in self.ignore_runways:
                # Non jet runways
                if arrival_runways[runway]["Non Jet"]:
                    # If runway has already been initialized
                    if runway in runways_in_use.keys():
                        runways_in_use[runway].arrival = True
                        runways_in_use[runway].non_jet_arrival = True
                    else:
                        runways_in_use[runway] = Runway(self.env, runway, self.wait_times, self.circle_times,
                                                        departure=False, arrival=True, non_jet_arrival=True)
                # All aircraft runways
                else:
                    # If runway has already been initialized
                    if runway in runways_in_use.keys():
                        runways_in_use[runway].arrival = True
                    else:
                        runways_in_use[runway] = Runway(self.env, runway, self.wait_times, self.circle_times,
                                                        departure=False, arrival=True)

        return runways_in_use

    def reset_wind(self):
        """Function to reset wind direction"""
        self.wind_direction = find_wind_direction()

    def reset_runways(self):
        """Function to reset runways"""
        self.runways = self.prepare_runways()
        self.non_jet_departure_runways, self.all_departure_runways = self.find_non_jet_runways(departure=True)
        self.non_jet_arrival_runways, self.all_arrival_runways = self.find_non_jet_runways(departure=False)

    def find_non_jet_runways(self, departure):
        """Function to find the non-jet runways"""
        non_jet_runways = []
        regular_runways = []
        # Find departure runways
        if departure:
            for runway in self.runways.keys():
                if self.runways[runway].departure:
                    if self.runways[runway].non_jet_departure:
                        non_jet_runways.append(runway)
                    else:
                        regular_runways.append(runway)

        # Find arrival runways
        else:
            for runway in self.runways.keys():
                if self.runways[runway].arrival:
                    if self.runways[runway].non_jet_arrival:
                        non_jet_runways.append(runway)
                    else:
                        regular_runways.append(runway)

        return non_jet_runways, regular_runways

    def find_shortest_runway_line(self, runway_list):
        """Function to find the runway with the shortest line"""
        shortest_line_length = None
        shortest_line = None

        for runway in runway_list:
            runway_line_length = self.runways[runway].get_runway_line_length()
            if shortest_line_length is None:
                shortest_line_length = runway_line_length
                shortest_line = runway
                continue

            if runway_line_length <= shortest_line_length:
                shortest_line_length = runway_line_length
                shortest_line = runway

        return shortest_line

    def select_runway(self, plane):
        """Function to select a runway to takeoff from/land on"""
        # Departure runways
        if plane.departing:
            # Non-jet departures
            if not plane.jet:
                if len(self.non_jet_departure_runways) > 0:
                    return self.find_shortest_runway_line(self.non_jet_departure_runways)
                else:
                    return self.find_shortest_runway_line(self.all_departure_runways)
            # All other departures
            else:
                return self.find_shortest_runway_line(self.all_departure_runways)

        # Arrival runways
        else:
            # Non-jet arrivals
            if not plane.jet:
                if len(self.non_jet_arrival_runways) > 0:
                    return self.find_shortest_runway_line(self.non_jet_arrival_runways)
                else:
                    return self.find_shortest_runway_line(self.all_arrival_runways)
            # All other departures
            else:
                return self.find_shortest_runway_line(self.all_arrival_runways)

    def takeoff_from_airport(self, plane):
        """Function to simulate a departing plane"""
        runway = self.runways[self.select_runway(plane)]
        self.env.process(runway.take_off(plane, self.wind_direction))

    def land_at_airport(self, plane):
        """Function to simulate a landing plane"""
        runway = self.runways[self.select_runway(plane)]
        self.env.process(runway.land(plane, self.wind_direction))

    def simulate(self):
        """Function to simulate landing and departing at the airport"""

        # change_wind = False

        # Loop which executes until no planes are left in line
        while True:

            time_of_day = self.env.now

            # Change random arrival rate based on time of day
            if time_of_day < 6*60:
                yield self.env.timeout(float(os.getenv("LAMBDA_NIGHT")))
            elif time_of_day < 12*60:
                yield self.env.timeout(float(os.getenv("LAMBDA_MORNING")))
            elif time_of_day < 18*60:
                yield self.env.timeout(float(os.getenv("LAMBDA_AFTERNOON")))
            else:
                yield self.env.timeout(float(os.getenv("LAMBDA_EVENING")))

            # Generate plane
            plane = Plane(self.env.now)

            # Make plane takeoff or land
            if plane.departing:
                self.takeoff_from_airport(plane)
            else:
                self.land_at_airport(plane)

    def save_simulation_data(self):
        """Function to save data when simulation is finished"""

        # Save departure data
        print("Saving departure data to file")
        departing_df = pd.DataFrame(data=self.wait_times, columns=["Time", "Airline", "Destination", "Flight Number",
                                                                   "Aircraft Type", "Wind", "Runway", "Wait Time"])
        departing_df.to_csv(f"../Data/departure_results_{self.simulation_type}.csv", index=False)

        # Save arrival data
        print("Saving arrival data to file")
        arrival_df = pd.DataFrame(data=self.circle_times, columns=["Time", "Airline", "Destination", "Flight Number",
                                                                   "Aircraft Type", "Wind", "Runway", "Circle Time"])
        arrival_df.to_csv(f"../Data/arrival_results_{self.simulation_type}.csv", index=False)

