import os

import simpy
import random


class Runway(object):
    """Class to represent a runway"""

    def __init__(self, env, name, departure=True, arrival=True, non_jet_departure=False, non_jet_arrival=False):
        self.env = env
        self.name = name
        self.departure = departure
        self.arrival = arrival
        self.non_jet_departure = non_jet_departure
        self.non_jet_arrival = non_jet_arrival
        self.resource = simpy.Resource(env, capacity=1)

    def take_off(self, plane):
        """
        Function to simulate take off. It is assumed that take off will take between 1-2 minutes (up to 90 seconds for
        lining up and up to 30 seconds for rolling down the runway)
        """
        with self.resource.request() as request:
            print(f"{plane.airline} flight {plane.flight_number} to {plane.route} waiting to take-off at runway: {self.name}")
            yield request
            yield self.env.timeout(float(os.getenv("MU_TAKEOFF")))
            print(f"{plane.airline} flight {plane.flight_number} to {plane.route} departed from runway: {self.name}")
            self.resource.release(request)

    def land(self, plane):
        """
        Function to simulate take off. It is assumed that landing will take between 1-3 minutes
        """
        with self.resource.request() as request:
            print(f"{plane.airline} flight {plane.flight_number} from {plane.route} circling runway: {self.name}")
            yield request
            yield self.env.timeout(float(os.getenv("MU_LANDING")))
            print(f"{plane.airline} flight {plane.flight_number} to {plane.route} landed at runway: {self.name}")
            self.resource.release(request)

    def check_if_non_jet(self, departure):
        """Function to determine if a runway is for non-jet only"""
        if departure:
            return self.non_jet_departure
        else:
            return self.non_jet_arrival

    def get_runway_line_length(self):
        """Function to return runway line length"""
        return len(self.resource.queue)
