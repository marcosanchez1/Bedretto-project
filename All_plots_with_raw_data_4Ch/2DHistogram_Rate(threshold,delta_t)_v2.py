'''
In this script I just work with one data set and increase the threshold at software level, I think this shouldbe less
precise but it kind of looks better.

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
    
    trigger_base = '0.005'
    run = 1

    route_data = fr".\Data\Raw_data\1Bar_2Chs\57V_TriggerCh0_VaryTrigger\Run_{trigger_base}V_Run{run}_Data_3_22_2026_Ascii.dat"
    trigger_base = float(trigger_base)

    # Δt values (ns)
    DELTA_T = np.linspace(0, 100, 200)

    # Storage for heatmap
    TRIGGERS = []
    RATES = []
    
    df = get_raw_data(route_data)

    TOTAL_TIME = df["unix_time"].iloc[-1] - df["unix_time"].iloc[0]

    # Pre-extract channel data for speed
    channels = df["channels"].to_numpy()
    ch0_peaks = np.array([np.max(row[0]) for row in channels])
    ch1_peaks = np.array([np.max(row[1]) for row in channels])
    ch0_argmax = np.array([np.argmax(row[0]) for row in channels])
    ch1_argmax = np.array([np.argmax(row[1]) for row in channels])
    dt_peaks = (ch0_argmax - ch1_argmax) * dt

    # Scan trigger values from trigger to trigger+0.005
    trigger = trigger_base
    trigger_end = trigger_base*16

    while trigger < trigger_end:

        # Events above threshold
        valid = (ch0_peaks >= trigger) & (ch1_peaks >= trigger)
        dt_valid = dt_peaks[valid]

        # Vectorized coincidence counting
        coincidence_rates = np.array([
            np.sum(np.abs(dt_valid) <= delta_t) / TOTAL_TIME
            for delta_t in DELTA_T
        ])

        TRIGGERS.append(trigger)
        RATES.append(coincidence_rates)

        trigger += 0.001

    # Convert to arrays for plotting
    TRIGGERS = np.array(TRIGGERS)
    RATES = np.array(RATES)

    # 2D Histogram (Heatmap)
    fig, ax = plt.subplots(figsize=(14, 10))

    # imshow expects (rows = triggers, columns = delta_t)
    im = ax.imshow(
        RATES,
        aspect='auto',
        origin='lower',
        extent=[DELTA_T.min(), DELTA_T.max(), TRIGGERS.min(), TRIGGERS.max()],
        cmap='turbo'
    )

    ax.set_xlabel("Δt (ns)")
    ax.set_ylabel("Trigger Threshold (V)")
    ax.set_title("Coincidence Rate Heatmap")

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Coincidence Rate (Hz)")

    plt.tight_layout()
    plt.show()

    return 0



if __name__ == "__main__":
    print('\nStart execution.\n')
    main()
    print("\nFinish execution\n")

