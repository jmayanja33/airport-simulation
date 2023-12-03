import numpy as np
import random
import os
from Data.final_data import airports, probabilities, airlines
from dotenv import load_dotenv

# Replace defunct airlines with airlines that bought them
replacement_airlines = {
    "FL": "WN",
    "US": "AA",
    "CO": "UA",
    "NW": "DL",
    "VX": "AS",
    "UN": "BA"
}

# Set of non-jet plane models
non_jet = {"DH4", "CNA", "SF3", "DH1", "DH3", "DH8"}


def choose_airline(departing):
    """Function to randomly choose an airline for an aircraft"""
    if departing:
        airline_codes = [i for i in probabilities["Departures"].keys()]
        airline_probabilities = [probabilities["Departures"][i]["Probability"] for i in probabilities["Departures"].keys()]
    else:
        airline_codes = [i for i in probabilities["Arrivals"].keys()]
        airline_probabilities = [probabilities["Arrivals"][i]["Probability"] for i in probabilities["Arrivals"].keys()]

    airline_code = np.random.choice(airline_codes, p=airline_probabilities)

    if airline_code in replacement_airlines.keys():
        replacement_code = replacement_airlines[airline_code]
        flight_number = f"{replacement_code}{random.randint(10, 10000)}"
        airline_name = airlines[replacement_code]["Name"]

    else:
        flight_number = f"{airline_code}{random.randint(10,10000)}"
        airline_name = airlines[airline_code]["Name"]

    return airline_name, flight_number, airline_code


def choose_route(departing, airline_code):
    """Function to choose where a plane is going to/coming from"""
    if departing:
        routes = [i for i in probabilities["Departures"][airline_code]["Routes"].keys()]
        route_probabilities = [probabilities["Departures"][airline_code]['Routes'][i]["Probability"] \
                               for i in probabilities["Departures"][airline_code]['Routes'].keys()]
    else:
        routes = [i for i in probabilities["Arrivals"][airline_code]["Routes"].keys()]
        route_probabilities = [probabilities["Arrivals"][airline_code]['Routes'][i]["Probability"] \
                               for i in probabilities["Arrivals"][airline_code]['Routes'].keys()]

    route = np.random.choice(routes, p=route_probabilities)
    route_airport = f"{airports[route]['Name']}; {airports[route]['City']}, {airports[route]['Country']}"

    return route, route_airport


def choose_aircraft(departing, airline_code, route):
    """Function to choose what kind of aircraft a plane is"""
    if departing:
        aircrafts = [i for i in probabilities["Departures"][airline_code]["Routes"][route]['Aircrafts'].keys()]
        aircraft_probabilities = [probabilities["Departures"][airline_code]["Routes"][route]['Aircrafts'][i]["Probability"] \
                                  for i in probabilities["Departures"][airline_code]["Routes"][route]['Aircrafts'].keys()]
    else:
        aircrafts = [i for i in probabilities["Arrivals"][airline_code]["Routes"][route]['Aircrafts'].keys()]
        aircraft_probabilities = [probabilities["Arrivals"][airline_code]["Routes"][route]['Aircrafts'][i]["Probability"] \
                                  for i in probabilities["Arrivals"][airline_code]["Routes"][route]['Aircrafts'].keys()]

    aircraft = np.random.choice(aircrafts, p=aircraft_probabilities)

    if aircraft in non_jet:
        jet = False
    else:
        jet = True

    return aircraft, jet


def determine_departing(time_of_day):
    """Function to choose if an aircraft is departing or arriving"""
    if time_of_day < 6*60:
        return np.random.choice([True, False],
                                p=[float(os.getenv("DEPARTURE_PROB_NIGHT")), float(os.getenv("ARRIVAL_PROB_NIGHT"))])
    elif time_of_day < 12*60:
        return np.random.choice([True, False],
                                p=[float(os.getenv("DEPARTURE_PROB_MORNING")), float(os.getenv("ARRIVAL_PROB_MORNING"))])
    elif time_of_day < 18*60:
        return np.random.choice([True, False],
                                p=[float(os.getenv("DEPARTURE_PROB_AFTERNOON")), float(os.getenv("ARRIVAL_PROB_AFTERNOON"))])
    else:
        return np.random.choice([True, False],
                                p=[float(os.getenv("DEPARTURE_PROB_EVENING")), float(os.getenv("ARRIVAL_PROB_EVENING"))])


class Plane:

    def __init__(self, time_of_day):
        """Class to represent a plane for our simulation"""
        # Load env file
        load_dotenv()

        # Randomly choose if the plane is departing or arriving
        self.departing = determine_departing(time_of_day)

        # Randomly choose the plane's airline based off of its departure status
        self.airline, self.flight_number, airline_code = choose_airline(self.departing)

        # Randomly choose the route the plane is flying based off its departure status and airline
        route_code, self.route = choose_route(self.departing, airline_code)

        # Randomly choose the plane's model based off its departure status, airline, and route
        self.aircraft_type, self.jet = choose_aircraft(self.departing, airline_code, route_code)
