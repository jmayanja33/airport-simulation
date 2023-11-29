import pandas as pd
import matplotlib.pyplot as plt


def find_and_write_simulation_statistics_to_file(simulation_type, departure_df, arrival_df):
    """Function to write all statistics from simulation results to a file"""
    num_departures = len(departure_df)
    max_departure_wait_time = max(departure_df["Wait Time"])
    average_departure_wait_time = departure_df["Wait Time"].mean()

    num_arrivals = len(arrival_df)
    max_arrivals_wait_time = max(arrival_df["Circle Time"])
    average_arrival_wait_time = arrival_df["Circle Time"].mean()

    with open(f"{simulation_type}/stats.txt", "w") as file:
        results = f"""Departures:\n
- Total Departures: {num_departures} flights
- Max Departure Wait Time: {max_departure_wait_time} minutes
- Avg. Departure Wait Time: {average_departure_wait_time} minutes
  
Arrivals:\n      
- Total Arrivals: {num_arrivals} flights
- Max Arrival Wait Time: {max_arrivals_wait_time} minutes
- Avg. Arrival Wait Time: {average_arrival_wait_time} minutes
        """
        file.write(results)
        file.close()


def find_and_plot_hourly_average_wait_times(simulation_type, departure_df, arrival_df):
    """Function to find daily average departure/arrival wait times"""
    departure_df["Rounded Time"] = [round(i, 0) for i in departure_df["Time"]]
    arrival_df["Rounded Time"] = [round(i, 0) for i in arrival_df["Time"]]

    wait_times_departure_df = departure_df.groupby("Rounded Time", as_index=False)["Wait Time"].mean()
    wait_times_arrival_df = arrival_df.groupby("Rounded Time", as_index=False)["Circle Time"].mean()

    # Plot all wait times/circle times by time of day
    plt.figure(figsize=(6, 4))
    plt.bar(wait_times_departure_df["Rounded Time"], wait_times_departure_df["Wait Time"])
    plt.title(f"Mean Departure Wait Times")
    plt.xlabel("Hour of Day")
    plt.ylabel("Wait Time (Minutes)")

    plt.savefig(f"{simulation_type}/departure_all_wait_times.png")

    # Plot all wait times/circle times by time of day
    plt.figure(figsize=(6, 4))
    plt.bar(wait_times_arrival_df["Rounded Time"], wait_times_arrival_df["Circle Time"], color="Orange")
    plt.title(f"Mean Arrival Wait Times")
    plt.xlabel("Hour of Day")
    plt.ylabel("Wait Time (Minutes)")
    plt.savefig(f"{simulation_type}/arrival_all_wait_times.png")


def find_and_plot_mean_runway_counts(simulation_type, departure_df, arrival_df):
    """Function to find daily average runway takeoff/departures"""
    data = {}
    graph_data = []
    departure_runways = departure_df["Runway"].unique()
    arrival_runways = arrival_df["Runway"].unique()

    # Calculate means for departure runways
    for drunway in departure_runways:
        df = departure_df[departure_df["Runway"] == drunway]
        mean_runway_departures = len(df) / 31
        data[drunway] = [mean_runway_departures, 0]

    # Calculate means for arrival runways
    for arunway in arrival_runways:
        df = arrival_df[arrival_df["Runway"] == arunway]
        mean_runway_arrivals = len(df) / 31
        if arunway not in data.keys():
            data[arunway] = [0, mean_runway_arrivals]
        else:
            data[arunway][1] = mean_runway_arrivals

    # Format Data
    for d in data.keys():
        graph_data.append((d, data[d][0], data[d][1]))

    plot_df = pd.DataFrame(graph_data, columns=["Runway", "Departure Mean", "Arrival Mean"])
    plot_df["Total Flights"] = plot_df["Departure Mean"] + plot_df["Arrival Mean"]
    plot_df = plot_df.sort_values(by="Total Flights", ascending=False)

    # Plot mean departures/arrivals count by runway
    plt.figure(figsize=(6, 4))
    plt.bar(plot_df["Runway"], plot_df["Departure Mean"], label="Departures")
    plt.bar(plot_df["Runway"], plot_df["Arrival Mean"], label="Arrivals")
    plt.title(f"Avg. Daily Runway Utilization (Normal Runways)")
    plt.xlabel("Runway")
    plt.ylabel("Avg. Number of Flights")
    plt.legend()
    plt.savefig(f"{simulation_type}/all_runway_counts.png")


# Run script to create visualizations
if __name__ == '__main__':
    # Load data
    print("Loading Data")
    control_departure_df = pd.read_csv("../Data/departure_results_control.csv")
    control_arrival_df = pd.read_csv("../Data/arrival_results_control.csv")

    one_runway_down_departure_df = pd.read_csv("../Data/departure_results_one_runway_down.csv")
    one_runway_down_arrival_df = pd.read_csv("../Data/arrival_results_one_runway_down.csv")

    extra_runway_departure_df = pd.read_csv("../Data/departure_results_extra_runway.csv")
    extra_runway_arrival_df = pd.read_csv("../Data/arrival_results_extra_runway.csv")

    two_runways_down_departure_df = pd.read_csv("../Data/departure_results_two_runways_down.csv")
    two_runways_down_arrival_df = pd.read_csv("../Data/arrival_results_two_runways_down.csv")

    extra_runway_two_down_departure_df = pd.read_csv("../Data/departure_results_extra_runway_with_two_down.csv")
    extra_runway_two_down_arrival_df = pd.read_csv("../Data/arrival_results_extra_runway_with_two_down.csv")

    # Evaluate control metrics
    print("Writing statistics to file")
    find_and_write_simulation_statistics_to_file("Control", control_departure_df, control_arrival_df)
    find_and_write_simulation_statistics_to_file("OneRunwayDown", one_runway_down_departure_df,
                                                 one_runway_down_arrival_df)
    find_and_write_simulation_statistics_to_file("ExtraRunway", extra_runway_departure_df,
                                                 extra_runway_arrival_df)
    find_and_write_simulation_statistics_to_file("TwoRunwaysDown", two_runways_down_departure_df,
                                                 two_runways_down_arrival_df)
    find_and_write_simulation_statistics_to_file("ExtraRunwayWithTwoDown",
                                                 extra_runway_two_down_departure_df,
                                                 extra_runway_two_down_arrival_df)

    # Plot all wait times/circle times by time of day
    print("Plotting hourly average wait times")
    find_and_plot_hourly_average_wait_times("Control", control_departure_df, control_arrival_df)
    find_and_plot_hourly_average_wait_times("OneRunwayDown", one_runway_down_departure_df,
                                            one_runway_down_arrival_df)
    find_and_plot_hourly_average_wait_times("TwoRunwaysDown", two_runways_down_departure_df,
                                            two_runways_down_arrival_df)
    find_and_plot_hourly_average_wait_times("ExtraRunway", extra_runway_departure_df,
                                            extra_runway_arrival_df)
    find_and_plot_hourly_average_wait_times("ExtraRunwayWithTwoDown", extra_runway_two_down_departure_df,
                                            extra_runway_two_down_arrival_df)

    # Plot mean departures/arrivals count by runway
    print("Plotting daily average runway counts")
    find_and_plot_mean_runway_counts("Control", control_departure_df, control_arrival_df)
    find_and_plot_mean_runway_counts("OneRunwayDown", one_runway_down_departure_df,
                                     one_runway_down_arrival_df)
    find_and_plot_mean_runway_counts("TwoRunwaysDown", two_runways_down_departure_df,
                                     two_runways_down_arrival_df)
    find_and_plot_mean_runway_counts("ExtraRunway", extra_runway_departure_df,
                                     extra_runway_arrival_df)
    find_and_plot_mean_runway_counts("ExtraRunwayWithTwoDown", extra_runway_two_down_departure_df,
                                     extra_runway_two_down_arrival_df)

    print("Finished!")
