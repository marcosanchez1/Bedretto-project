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
from Functions import get_raw_datFile, get_t
from scipy.optimize import curve_fit
import os

def curve(x,m,b):
    return m*x + b

def perform_fit(X,Y):
    P, cov = curve_fit(curve, X, Y)
    return P
def chi2(y_data, y_fit, y_err=None):
    if y_err is None:
        # assume equal weights
        y_err = np.ones_like(y_data)
    return np.sum(((y_data - y_fit) / y_err)**2)

def main():
    dt = 0.3125  # ns
    route_files = r".\Data\Raw_data\1Bar_2Ch\57V_TriggerCh0_VaryTrigger"
    list_files = os.listdir(route_files)
    
    fig, ax = plt.subplots(figsize=(10, 10))

    DELTA_T = np.linspace(0, 60, 200)

    for file in list_files:
        if not file.endswith(".dat"):
            continue

        input_path = os.path.join(route_files, file)
        df = get_raw_datFile(input_path)

        # Extract threshold value from filename
        th = float(file.split("_")[1].replace("V", ""))
        
        if th <= 0.006:
            TOTAL_TIME = df["unix_time"].iloc[-1] - df["unix_time"].iloc[0]
        
        # Pre-extract arrays for speed
        channels = df["channels"].to_numpy()
        ch0_peaks = np.array([np.max(row[0]) for row in channels])
        ch1_peaks = np.array([np.max(row[1]) for row in channels])
        time_detection_ch0= np.array([get_t(row[0], 0.2) for row in channels])
        time_detection_ch1= np.array([get_t(row[1], 0.2) for row in channels])

        COINCIDENCE = []
        for delta_t in DELTA_T:
            count = 0
            ti = df['unix_time'].iloc[0]
            for i in range(len(df)):
                peak0 = ch0_peaks[i]
                peak1 = ch1_peaks[i]

                t0 = time_detection_ch0[i]
                t1 = time_detection_ch1[i]
                
                # Coincidence conditions
                if peak0 >= th and peak1 >= th:
                    if abs(t0 - t1) <= delta_t:
                        count += 1

                # This conditions helps us stop when we have the same time on all data sets 
                tf = df['unix_time'].iloc[i]
                if tf - ti >= TOTAL_TIME:
                    break
            COINCIDENCE.append(count / TOTAL_TIME)  # Rate in Hz

        # Plot
        ax.plot(DELTA_T, COINCIDENCE, label=f'Th={round(th,4)}', marker='o', linestyle='-', alpha=0.7)
            
        k = np.where(DELTA_T >= 40 )[0][0]
        X1,Y1 = DELTA_T[k:], COINCIDENCE[k:]
        P1 = perform_fit(X1, Y1)
        # Compute fitted values
        Y_fit = np.array([curve(x, *P1) for x in X1])
        # Compute chi-square
        chi2_val = chi2(Y1, Y_fit)
        ndof = len(X1) - len(P1)   # number of degrees of freedom
        chi2_red_1 = chi2_val / ndof
        #ax.plot(X1, [curve(x, *P1) for x in X1], label=f'm={round(P[0],4)};b={round(P[1],4)};χ²={chi2_red:.2f}', marker='', linestyle='-', alpha=0.7)
        ax.plot(X1, [curve(x, *P1) for x in X1], label=f'', marker='', linestyle='-', alpha=0.7)

        k = np.where(DELTA_T >= 30 )[0][0]
        X2,Y2 = DELTA_T[:k], COINCIDENCE[:k]
        P2 = perform_fit(X2, Y2)
        # Compute fitted values
        Y_fit = np.array([curve(x, *P2) for x in X2])
        # Compute chi-square
        chi2_val = chi2(Y2, Y_fit)
        ndof = len(X2) - len(P2)   # number of degrees of freedom
        chi2_red_2 = chi2_val / ndof
        #ax.plot(X2, [curve(x, *P) for x in X2], label=f'm={round(P2[0],4)};b={round(P2[1],4)};χ²={chi2_red:.2f}', marker='', linestyle='-', alpha=0.7)
        ax.plot(X2, [curve(x, *P2) for x in X2], label=f'', marker='', linestyle='-', alpha=0.7)

        print(f'Threshold: {th}\n1st fit: m={round(P1[0],4)};b={round(P1[1],4)};χ²={chi2_red_1:.2f} | 2nd fit: m={round(P2[0],4)};b={round(P2[1],4)};χ²={chi2_red_2:.2f}')

    ax.set_title(f'Coincidences vs Δt(time_sampling={round(TOTAL_TIME,3)}s)')
    ax.set_xlabel('Δt (ns)')
    ax.set_ylabel('Rate (Hz)')
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    #plt.savefig(fr'.\All_plots_with_raw_data\Plots\1Bar_2Chs\57V_TriggerCh0_VaryTrigger\Run{run}_Th{round(th-0.005,4)}.png')
    plt.show()

    return 0


if __name__ == "__main__":
    print('\nStart execution.\n')
    main()
    print("\nFinish execution\n")
