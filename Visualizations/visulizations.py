import pandas as pd
# from matplotlib.pyplot import

# Load data
control_departure_df = pd.read_csv("../Data/departure_results_control.csv")
control_arrival_df = pd.read_csv("../Data/arrival_results_control.csv")

# Evaluate control metrics
num_departures = len(control_departure_df)
max_departure_wait_time = max(control_departure_df["Wait Time"])
average_departure_wait_time = control_departure_df["Wait Time"].mean()

num_arrivals = len(control_arrival_df)
max_arrivals_wait_time = max(control_arrival_df["Circle Time"])
average_arrival_wait_time = control_arrival_df["Circle Time"].mean()

# Plot all wait times by time of day

# Plot average wait times by runway

# Plot departures/arrivals count by runway

# Plot departures/arrivals by airline

# Plot departures/arrivals by plane type

pass