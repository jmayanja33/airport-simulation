# Logan Airport Simulation

## Description
This project, undertaken for a Master's level simulation class, had the goal of determining how efficient the runways at Boston’s Logan International Airport are. The main objectives were to see how long planes departing and leaving the airport were waiting just to use a runway, how these wait times would be affected if two of the airport’s busiest runways were shut down, and how they would be affected if a new runway was built. These scenarios were evaluated by simulating a month of air traffic flowing into and out of Logan Airport, under different circumstances.

The simulation model built for this project was created using Python, specifically the Simpy library. The model was very efficient, as it provided easily interpretable results, and only took around 12 seconds to run a full simulation for each scenario. After simulating 5 different scenarios involving different runway configurations, it was found that the runways at Logan Airport are run very efficiently and can adapt well to runway closures. Mean wait times for runways never rose above 1 minute, even with two runways closed. See the report in `Documents/Group204FinalReport.pdf` for an analysis of the full results.

## Code

### Data
This folder contains all the data used in the project. `airlines.csv`, `airports.csv`, `routes.csv`, and `raw_flight_data.py` are the four files containing the raw data for the project. `data_extractor.py` processes all of this data in stores it in python dictionaries in the file `final_data.py`. `final_data.py` is the data file used by the actual simulation.
The rest of the data in this folder are simulation results from the simulations run, which are utilized by `Visulaizations/visualizations.py` to visualize the results.

### Simulation
This folder contains all files to create the simulation. `plane.py`, `airport.py`, and `runway.py` create plane, airport, and runway objects respectively. `simulator.py` runs the simulation based on the conditions set in the `.env` file.

### Visualizations
`visulaizations.py` creates three plots and a general statistics file for each scenario tested. The plots show mean departure wait times, mean arrival wait times, and runway usage. The statistics file contains stats on average daily wait times.
