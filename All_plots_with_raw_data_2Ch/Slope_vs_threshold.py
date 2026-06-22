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
from Functions import get_raw_datFile, get_t
from scipy.optimize import curve_fit
import os

def curve(x,m,b):
    return m*x + b

def perform_fit(X,Y):
    P, cov = curve_fit(curve, X, Y)
    return P

def main():
    dt = 0.3125  # ns
    route_files = r".\Data\Raw_data\1Bar_2Ch\57V_TriggerCh0_VaryTrigger"
    list_files = os.listdir(route_files)

    DELTA_T = np.linspace(0, 60, 200)

    time_k = [10 + 1*i for i in range(11)]
    M = []
    TH = []

    for file in list_files:
        if not file.endswith(".dat"):
            continue
        input_path = os.path.join(route_files, file)
        df = get_raw_datFile(input_path)
        th = float(file.split("_")[1].replace("V", ""))

        # Pre-extract arrays for speed
        channels = df["channels"].to_numpy()
        ch0_peaks = np.array([np.max(row[0]) for row in channels])
        ch1_peaks = np.array([np.max(row[1]) for row in channels])
        time_detection_ch0 = np.array([get_t(row[0], 0.2) for row in channels])
        time_detection_ch1 = np.array([get_t(row[1], 0.2) for row in channels])

        if th <= 0.006:
            TOTAL_TIME = df["unix_time"].iloc[-1] - df["unix_time"].iloc[0]
        
        COINCIDENCE = []
        for delta_t in DELTA_T:
            count = 0
            ti = df['unix_time'].iloc[0]
            for i in range(len(df)):
                peak0 = ch0_peaks[i]
                peak1 = ch1_peaks[i]

                t0 = time_detection_ch0[i]
                t1 = time_detection_ch1[i]

                if peak0 >= th and peak1 >= th:
                    if abs(t0 - t1) <= delta_t:
                        count += 1
                
                tf = df['unix_time'].iloc[i]
                if tf - ti >= TOTAL_TIME:
                    break
            COINCIDENCE.append(count / TOTAL_TIME)  # Rate in Hz

        # Fit: I noticed that from 40ns onward we have what we want, maybe even from 35ns.
        k = np.where(DELTA_T >= 40 )[0][0]
        X,Y = DELTA_T[k:], COINCIDENCE[k:]
        P = perform_fit(X, Y)

        M.append(P[0])
        TH.append(th)

    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    ax.plot(TH, M, label=f'Δt>{40}ns', marker='o', linestyle='-', alpha=0.7)
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
