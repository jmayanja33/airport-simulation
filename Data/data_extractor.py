import os
import time
import requests
import pandas as pd


class DataExtractor:
    """Class to extract airport, airline and flight data"""

    def __init__(self):
        # Load airport data
        self.airport_data = pd.read_csv("airports.csv")
        self.airport_data = self.airport_data.fillna("None")

        # Load and filter airline data
        airline_data = pd.read_csv("airlines.csv")
        airline_data = airline_data.fillna("None")
        self.airline_data = airline_data[airline_data["Active"] == "Y"]
        self.airline_data.reset_index(inplace=True, drop=True)

        # Load and filter route data
        route_data = pd.read_csv("routes.csv")
        route_data = route_data.fillna("None")

        # Filter data for only Boston flights
        self.boston_data = self.airport_data[self.airport_data["City"] == "Boston"]
        self.boston_departure_data = route_data[route_data["Source Airport"] == "BOS"]
        self.boston_arrival_data = route_data[route_data["Destination Airport"] == "BOS"]
        self.boston_departure_data.reset_index(inplace=True, drop=True)
        self.boston_arrival_data.reset_index(inplace=True, drop=True)

        # Extract Data
        self.airports = self.extract_airport_data()
        self.airlines = self.extract_airline_data()
        self.routes = self.extract_route_data()
        self.probabilities = self.calculate_probabilities()
        self.runways = self.configure_runways()

    def extract_airport_data(self):
        """Function to save all airport data to a dictionary"""
        airports = {}
        num_airports = len(self.airport_data)
        for i in range(num_airports):
            print(f"Extracting airport data: Progress {i}/{num_airports}")
            airport_id = self.airport_data["IATA"][i]
            airports[airport_id] = {}
            airports[airport_id]["Name"] = self.airport_data["Name"][i]
            airports[airport_id]["City"] = self.airport_data["City"][i]
            airports[airport_id]["Country"] = self.airport_data["Country"][i]

        return airports

    def extract_airline_data(self):
        """Function to save all airline data to a dictionary"""
        airlines = {}
        num_airlines = len(self.airline_data)
        for i in range(num_airlines):
            print(f"Extracting airline data; Progress: {i+1}/{num_airlines}")
            airline_id = self.airline_data["IATA"][i]
            airlines[airline_id] = {}
            airlines[airline_id]["Name"] = self.airline_data["Name"][i]
            airlines[airline_id]["ICAO"] = self.airline_data["ICAO"][i]

        return airlines

    def extract_route_data(self):
        """Function to extract data on all routes to Boston"""
        routes = {'Departures': {}, 'Arrivals': {}}

        # Extract departure data
        num_departures = len(self.boston_departure_data)
        for i in range(num_departures):
            print(f"Extracting departure routes; Progress: {i+1}/{num_departures}")
            destination = self.boston_departure_data["Destination Airport"][i]
            if destination not in routes['Departures'].keys():
                routes['Departures'][destination] = {}

            # Save planes used by airline by route
            airline = self.boston_departure_data["Airline"][i]
            routes['Departures'][destination][airline] = self.boston_departure_data["Equipment"][i].split(" ")

        # Extract arrival data
        num_arrivals = len(self.boston_arrival_data)
        for i in range(num_arrivals):
            print(f"Extracting arrival routes: Progress: {i}/{num_arrivals}")
            source = self.boston_arrival_data["Source Airport"][i]
            if source not in routes['Arrivals'].keys():
                routes['Arrivals'][source] = {}

            # Save planes used by airline by route
            airline = self.boston_arrival_data["Airline"][i]
            routes['Arrivals'][source][airline] = self.boston_arrival_data["Equipment"][i].split(" ")

        return routes

    def calculate_probabilities(self):
        """Function to calculate flight probabilities"""
        num_departures = len(self.boston_departure_data)
        num_arrivals = len(self.boston_arrival_data)
        probabilities = {
            "Departures": {},
            "Arrivals": {},
            "Num Departures": num_departures,
            "Departure Rate": round(num_departures/24, 0),
            "Num Arrivals": num_arrivals,
            "Arrival Rate": round(num_arrivals/24, 0),
            "Wind": {
                "Northeast": 0.18,
                "Northwest": 0.37,
                "Southeast": 0.17,
                "Southwest": 0.28
            }
        }

        # Collect departure data
        for i in range(len(self.boston_departure_data)):
            print(f"Collecting Departure Probability Data; Progress: {i}/{len(self.boston_departure_data)}")
            aircrafts = self.boston_departure_data["Equipment"][i].split(" ")
            airline = self.boston_departure_data["Airline"][i]
            destination = self.boston_departure_data["Destination Airport"][i]

            # Track airlines
            if airline not in probabilities['Departures'].keys():
                probabilities['Departures'][airline] = {}

            # Track departures
            if 'Count' not in probabilities['Departures'][airline].keys():
                probabilities['Departures'][airline]['Count'] = 0
            probabilities['Departures'][airline]['Count'] += 1

            # Track destinations
            if 'Routes' not in probabilities['Departures'][airline].keys():
                probabilities['Departures'][airline]['Routes'] = {}

            if destination not in probabilities['Departures'][airline]['Routes']:
                probabilities['Departures'][airline]['Routes'][destination] = {'Count': 0}
            probabilities['Departures'][airline]['Routes'][destination]['Count'] += 1

            # Track aircrafts
            if 'Aircrafts' not in probabilities['Departures'][airline]['Routes'][destination]:
                probabilities['Departures'][airline]['Routes'][destination]['Aircrafts'] = {}
                for aircraft in aircrafts:
                    probabilities['Departures'][airline]['Routes'][destination]['Aircrafts'][aircraft] = {}
                    probabilities['Departures'][airline]['Routes'][destination]['Aircrafts'][aircraft]['Probability'] = 1/len(aircrafts)

        # Calculate departure probabilities
        counter = 1
        for airline in probabilities['Departures'].keys():
            print(f"Collecting Departure Probabilities; Progress: {counter}/{len(probabilities['Departures'].keys())}")
            # Calculate airline probabilities
            airline_probability = probabilities['Departures'][airline]['Count'] / num_departures
            probabilities['Departures'][airline]['Probability'] = airline_probability

            # Calculate route probabilities
            for route in probabilities['Departures'][airline]['Routes']:
                route_probability = probabilities['Departures'][airline]['Routes'][route]['Count'] / len(probabilities['Departures'][airline]['Routes'])
                probabilities['Departures'][airline]['Routes'][route]['Probability'] = route_probability

            counter += 1

        # Collect arrival data
        for i in range(len(self.boston_arrival_data)):
            print(f"Collecting Arrival Probability Data; Progress: {i}/{len(self.boston_arrival_data)}")
            aircrafts = self.boston_arrival_data["Equipment"][i].split(" ")
            airline = self.boston_arrival_data["Airline"][i]
            source = self.boston_arrival_data["Source Airport"][i]

            # Track airlines
            if airline not in probabilities['Arrivals'].keys():
                probabilities['Arrivals'][airline] = {}

            # Track arrivals
            if 'Count' not in probabilities['Arrivals'][airline].keys():
                probabilities['Arrivals'][airline]['Count'] = 0
            probabilities['Arrivals'][airline]['Count'] += 1

            # Track sources
            if 'Routes' not in probabilities['Arrivals'][airline].keys():
                probabilities['Arrivals'][airline]['Routes'] = {}

            if source not in probabilities['Arrivals'][airline]['Routes']:
                probabilities['Arrivals'][airline]['Routes'][source] = {'Count': 0}
            probabilities['Arrivals'][airline]['Routes'][source]['Count'] += 1

            # Track aircrafts
            if 'Aircrafts' not in probabilities['Arrivals'][airline]['Routes'][source]:
                probabilities['Arrivals'][airline]['Routes'][source]['Aircrafts'] = {}
                for aircraft in aircrafts:
                    probabilities['Arrivals'][airline]['Routes'][source]['Aircrafts'][aircraft] = {}
                    probabilities['Arrivals'][airline]['Routes'][source]['Aircrafts'][aircraft]['Probability'] = 1 / len(aircrafts)

        # Calculate arrival probabilities
        counter = 1
        for airline in probabilities['Arrivals'].keys():
            print(f"Collecting Arrival Probabilities; Progress: {counter}/{len(probabilities['Arrivals'].keys())}")
            # Calculate airline probabilities
            airline_probability = probabilities['Arrivals'][airline]['Count'] / num_departures
            probabilities['Arrivals'][airline]['Probability'] = airline_probability

            # Calculate route probabilities
            for route in probabilities['Arrivals'][airline]['Routes']:
                route_probability = probabilities['Arrivals'][airline]['Routes'][route]['Count'] / len(
                    probabilities['Arrivals'][airline]['Routes'])
                probabilities['Arrivals'][airline]['Routes'][route]['Probability'] = route_probability

            counter += 1

        return probabilities

    def configure_runways(self):
        """Function to set runway data"""
        runways = {
            "Northeast": {
                "Departures": {
                    "9": {"Non Jet": False},
                    "4L": {"Non Jet": True},
                    "4R": {"Non Jet": False}
                },
                "Arrivals": {
                    "4L": {"Non Jet": False},
                    "4R": {"Non Jet": False}
                }
            },
            "Northwest": {
                "Departures": {
                    "33L": {"Non Jet": False},
                    "27": {"Non Jet": False}
                },
                "Arrivals": {
                    "33L": {"Non Jet": False},
                    "27": {"Non Jet": False},
                    "32": {"Non Jet": False}
                }
            },
            "Southeast": {
                "Departures": {
                    "15R": {"Non Jet": False},
                    "15L": {"Non Jet": False}
                },
                "Arrivals": {
                    "15R": {"Non Jet": False},
                    "14": {"Non Jet": False},
                    "9": {"Non Jet": False}
                }

            },
            "Southwest": {
                "Departures": {
                    "22L": {"Non Jet": False},
                    "22R": {"Non Jet": False}
                },
                "Arrivals": {
                    "22L": {"Non Jet": False},
                    "27": {"Non Jet": False},
                    "22R": {"Non Jet": True}
                }
            }
        }

        return runways

    def save_extracted_data(self):
        """Function to save data to file"""
        print("Writing data to file")
        with open("final_data.py", "w", encoding='utf-8') as file:
            file.write(f"airports = {self.airports}\n\nairlines = {self.airlines}\n\nroutes = {self.routes}\n\nprobabilities = {self.probabilities}\n\nrunways = {self.runways}")
            file.close()


if __name__ == '__main__':
    data_extractor = DataExtractor()
    data_extractor.save_extracted_data()
