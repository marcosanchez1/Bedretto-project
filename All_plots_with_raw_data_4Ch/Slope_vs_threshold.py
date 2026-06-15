'''
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
import os

def curve(x,m,b):
    return m*x + b

def perform_fit(X,Y):
    P, cov = curve_fit(curve, X, Y)
    return P

def main():
    dt = 0.3125  # ns
    route_files = r".\Data\Raw_data\1Bar_2Chs\57V_TriggerCh0_VaryTrigger"
    list_files = os.listdir(route_files)

    DELTA_T = np.linspace(0, 60, 200)

    time_k = [10 + 1*i for i in range(11)]
    M = [[] for _ in time_k]
    TH = [[] for _ in time_k]

    for file in list_files:
        if not file.endswith(".dat"):
            continue
        input_path = os.path.join(route_files, file)
        df = get_raw_data(input_path)
        th = float(file.split("_")[1].replace("V", ""))

        # Pre-extract arrays for speed
        channels = df["channels"].to_numpy()
        ch0_peaks = np.array([np.max(row[0]) for row in channels])
        ch1_peaks = np.array([np.max(row[1]) for row in channels])
        ch0_argmax = np.array([np.argmax(row[0]) for row in channels])
        ch1_argmax = np.array([np.argmax(row[1]) for row in channels])

        TOTAL_TIME = df["unix_time"].iloc[-1] - df["unix_time"].iloc[0]
        
        th_f = th + 0.005
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
            for i,tk in enumerate(time_k):
                k = np.where(DELTA_T >= tk )[0][0]
                X,Y = DELTA_T[k:], COINCIDENCE[k:]
                P = perform_fit(X, Y)

                M[i].append(P[0])
                TH[i].append(th)
            th += 0.001

    fig, ax = plt.subplots(1, 1, figsize=(15, 10))

    for i,tk in enumerate(time_k):
        ax.plot(TH[i], M[i], label=f'Δt>{tk}ns', marker='o', linestyle='-', alpha=0.7)
    ax.set_title(f'Slope vs threshold')
    ax.set_xlabel('Threshold (V)')
    ax.set_ylabel('Slope (Hz^2)')
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    plt.show()

    return 0


if __name__ == "__main__":
    print('\nStart execution.\n')
    main()
    print("\nFinish execution\n")
