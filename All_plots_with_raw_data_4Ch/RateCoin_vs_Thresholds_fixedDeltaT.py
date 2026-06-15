'''
The idea of this script is to perform a 2D histogram of rate(delta_t,threshold) basically I just wanted to see if we something
useful of the dependency of the rate with delta_t(time difference between peaks) and thresholds.

The data structure of the data frames should be something like this:
channels,unix_time
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_0
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_1
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_2
...

'''

import numpy as np
import matplotlib.pyplot as plt
from Functions import get_raw_data
import os

def main():
    dt = 0.3125  # ns
    route_files = r".\Data\Raw_data\1Bar_2Chs\57V_TriggerCh0_VaryTrigger"
    list_files = os.listdir(route_files)

    # Δt values (ns)
    DELTA_T = 10

    # Storage for heatmap
    TRIGGERS = []
    RATES = []

    for file in list_files:
        if not file.endswith(".dat"):
            continue

        input_path = os.path.join(route_files, file)
        df = get_raw_data(input_path)

        TOTAL_TIME = df["unix_time"].iloc[-1] - df["unix_time"].iloc[0]

        # Extract trigger value from filename
        trigger = float(file.split("_")[1].replace("V", ""))

        # Pre-extract channel data for speed
        channels = df["channels"].to_numpy()
        ch0_peaks = np.array([np.max(row[0]) for row in channels])
        ch1_peaks = np.array([np.max(row[1]) for row in channels])
        ch0_argmax = np.array([np.argmax(row[0]) for row in channels])
        ch1_argmax = np.array([np.argmax(row[1]) for row in channels])
        dt_peaks = (ch0_argmax - ch1_argmax) * dt
        
        th_f = trigger + 0.005
        while trigger < th_f:
            # Events above threshold
            valid = (ch0_peaks >= trigger) & (ch1_peaks >= trigger)
            dt_valid = dt_peaks[valid]

            # Vectorized coincidence counting
            coincidence_rates = np.sum(np.abs(dt_valid) <= DELTA_T) / TOTAL_TIME
            
            TRIGGERS.append(trigger)
            RATES.append(coincidence_rates)
            trigger += 0.001

    # Convert to arrays for plotting
    TRIGGERS = np.array(TRIGGERS)
    RATES = np.array(RATES)

    # 2D Histogram (Heatmap)
    fig, ax = plt.subplots(figsize=(14, 10))

    ax.plot(TRIGGERS, RATES, label=f'Delta_t={DELTA_T}ns', marker='o', linestyle='-', alpha=0.7)

    ax.set_xlabel("Thresholds (V)")
    ax.set_ylabel("Rates (Hz)")
    ax.grid(True)
    ax.legend()
    ax.set_title("Coincidence Rate vs Thresholds")

    plt.tight_layout()
    plt.show()

    return 0



if __name__ == "__main__":
    print('\nStart execution.\n')
    main()
    print("\nFinish execution\n")

