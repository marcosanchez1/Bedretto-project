'''
In this script I'll just take the data of the special run and plot it, by special run I mean that I did a run
just to measure the rate without taking wf data, this should be more accurate to measure the rate.

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
from scipy.optimize import curve_fit

def curve(x,m,b):
    return m*x + b

def perform_fit(X,Y):
    P, cov = curve_fit(curve, X, Y)
    return P

def main():
    th = input('Threshold: ')
    run = input('Run: ')

    dt = 0.3125  # ns
    filename = fr".\Data\Raw_data\1Bar_2Chs\57V_TriggerCh0_VaryTrigger\Run_{th}V_Run{run}_Data_3_22_2026_Ascii.dat"

    th = float(th)

    df = get_raw_data(filename)

    # Pre-extract arrays for speed
    channels = df["channels"].to_numpy()
    ch0_peaks = np.array([np.max(row[0]) for row in channels])
    ch1_peaks = np.array([np.max(row[1]) for row in channels])
    ch0_argmax = np.array([np.argmax(row[0]) for row in channels])
    ch1_argmax = np.array([np.argmax(row[1]) for row in channels])

    TOTAL_TIME = df["unix_time"].iloc[-1] - df["unix_time"].iloc[0]

    fig, ax = plt.subplots(1, 1, figsize=(15, 10))

    th_f = th + 0.001
    DELTA_T = np.linspace(0, 60, 200)

    while th < th_f:

        # Precompute coincidence mask for this threshold
        valid_events = (ch0_peaks >= th) & (ch1_peaks >= th)
        dt_peaks = (ch0_argmax - ch1_argmax) * dt
        dt_valid = dt_peaks[valid_events]

        # Vectorized coincidence counting
        COINCIDENCE = np.array([
            np.sum(np.abs(dt_valid) <= delta_t) / TOTAL_TIME
            for delta_t in DELTA_T
        ])

        # Plot
        ax.plot(DELTA_T, COINCIDENCE, label=f'Th={round(th,4)}', marker='o', linestyle='-', alpha=0.7)
        
        k = np.where(DELTA_T >= 20 )[0][0]
        X,Y = DELTA_T[:k], COINCIDENCE[:k]
        P1 = perform_fit(X, Y)
        ax.plot(X, [curve(x, *P1) for x in X], label=f'm={round(P1[0],4)};b={round(P1[1],4)}', marker='', linestyle='-', alpha=0.7)

        X,Y = DELTA_T[k:], COINCIDENCE[k:]
        P2 = perform_fit(X, Y)
        ax.plot(X, [curve(x, *P2) for x in X], label=f'm={round(P2[0],4)};b={round(P2[1],4)}', marker='', linestyle='-', alpha=0.7)

        th += 0.001

    ax.set_title(f'Coincidences vs Δt')
    ax.set_xlabel('Δt (ns)')
    ax.set_ylabel('Rate (Hz)')
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    plt.savefig(fr'.\All_plots_with_raw_data\Plots\1Bar_2Chs\57V_TriggerCh0_VaryTrigger\Run{run}_Th{round(th-0.005,4)}.png')
    plt.show()

    return 0


if __name__ == "__main__":
    print('\nStart execution.\n')
    main()
    print("\nFinish execution\n")
