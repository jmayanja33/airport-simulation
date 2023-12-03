"""
Scratch file to do computations to determine departure/arrival rates, probabilities, process times
"""

# Number of departures over 3 days
Departure = {
    "Night": 82 + 92 + 67,
    "Morning": 426 + 456 + 371,
    "Afternoon": 522 + 589 + 469,
    "Evening": 372 + 520 + 331,
}

# Number of arrivals over 3 days
Arrival = {
    "Night": 112 + 72 + 53,
    "Morning": 390 + 347 + 327,
    "Afternoon": 632 + 610 + 552,
    "Evening": 510 + 395 + 366,
}

# Recorded take off times in seconds
take_off = [138, 63, 74, 58, 67, 67, 112, 121, 85, 85,
            48, 92, 74, 115, 91, 111, 71, 64, 83, 86,
            107, 72, 135, 170, 119, 74, 90, 95, 94, 72,
            81, 75, 68, 97, 64, 72, 86, 65, 117, 85,
            125, 65, 61, 76, 138, 114, 67, 63, 74, 122]

# Recorded arrival times in seconds
landing = [70, 86, 102, 103, 98, 113, 111, 122, 105, 129,
           141, 117, 104, 121, 123, 132, 104, 144, 152, 122,
           145, 156, 118, 131, 94, 112, 109, 116, 112, 107,
           124, 118, 115, 152, 113, 162, 124, 147, 138, 139,
           132, 141, 124, 139, 115, 139, 94, 146, 138, 137]

"""
Math: 

- Night:
    - 80 flights per hour
    - 1.3333 flights per minute
    - Departure probability = 0.504184
    - Arrival probability = 0.495816
    
- Morning: 
    - 386 flights per hour
    - 6.4333 flights per minute
    - Departure probability = 0.540785
    - Arrival probability = 0.459215
    
- Afternoon: 
    - 562 flights per hour
    - 9.3667 flights per minute
    - Departure probability = 0.468287
    - Arrival probability = 0.531713
    
- Evening:
    - 416 flights per hour
    - 6.9333 flights per minute
    - Departure probability = 0.490377
    - Arrival probability = 0.509623
    

- Take off mean process time: 1.4827 minutes
- Landing mean process time: 2.0453 minutes
"""