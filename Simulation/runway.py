import os
import simpy
import random


class Runway(object):
    """Class to represent a runway"""

    def __init__(self, env, name, wait_times, circle_times, departure=True, arrival=True, non_jet_departure=False,
                 non_jet_arrival=False):
        self.env = env
        self.name = name
        self.wait_times = wait_times
        self.circle_times = circle_times
        self.departure = departure
        self.arrival = arrival
        self.non_jet_departure = non_jet_departure
        self.non_jet_arrival = non_jet_arrival
        self.resource = simpy.Resource(env, capacity=1)

    def take_off(self, plane, wind_direction):
        """
        Function to simulate take off. It is assumed that take off will take between 1-2 minutes (up to 90 seconds for
        lining up and up to 30 seconds for rolling down the runway)
        """
        with self.resource.request() as request:
            # Begin timing
            start_time = self.env.now
            print(f"{plane.airline} flight {plane.flight_number} to {plane.route} waiting to take-off at runway: {self.name}")
            # Wait for runway to be free
            yield request
            # Take off
            yield self.env.timeout(random.expovariate(float(os.getenv("MU_TAKEOFF"))))
            wait_time = round(self.env.now - start_time, 2)
            print(f"{plane.airline} flight {plane.flight_number} to {plane.route} landed at runway: {self.name} after waiting {wait_time} minutes")
            self.resource.release(request)

            # Record stats
            data = (round(start_time/60, 2), plane.airline, plane.route, plane.flight_number, plane.aircraft_type, wind_direction,
                    self.name, wait_time)
            self.wait_times.append(data)

    def land(self, plane, wind_direction):
        """
        Function to simulate take off. It is assumed that landing will take between 1-3 minutes
        """
        with self.resource.request() as request:
            # Begin timing
            start_time = self.env.now
            print(f"{plane.airline} flight {plane.flight_number} from {plane.route} circling runway: {self.name}")
            # Wait for runway to be free
            yield request
            # Land
            yield self.env.timeout(random.expovariate(float(os.getenv("MU_LANDING"))))
            wait_time = round(self.env.now - start_time, 2)
            print(f"{plane.airline} flight {plane.flight_number} from {plane.route} landed at runway: {self.name} after waiting {wait_time} minutes")
            self.resource.release(request)

            # Record stats
            data = (round(start_time/60, 2), plane.airline, plane.route, plane.flight_number, plane.aircraft_type, wind_direction,
                    self.name, wait_time)
            self.circle_times.append(data)

    def check_if_non_jet(self, departure):
        """Function to determine if a runway is for non-jet only"""
        if departure:
            return self.non_jet_departure
        else:
            return self.non_jet_arrival

    def get_runway_line_length(self):
        """Function to return runway line length"""
        return len(self.resource.queue)
