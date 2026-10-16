'''
In this script I will plot the distribution of rate of events, now this is a bit weird but it's kind of the whole point.

So the idea is the following, say we divide our data set into N chunks and each chunk has a time length of T, then for each
chunk we can count the number of events that happened in that chunk and then divide by T to get the rate of events in that chunk.
Then we can plot the distribution of these rates, and see if which distribution we get(if any).
'''

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
import os
import sys

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from Functions import get_raw_datFile, get_raw_rootFile, perform_fit_on_dataframe, f, get_t_with_samples

dt = 0.3125 # multiply sample_i by this to get it in ns
max_number_samples = 1024
v = 15.95 # speed of light inside scintillator in cm/ns.
L = 170

def main():
    trigger_oscilloscope = '0.020' # with 15mV it's mostly muons

    # Load raw data
    df = get_raw_datFile(fr".\Data\Raw_data\2Bar_4Ch\CoincidenceMode\COIN_CH0123_PS57V_GL15ns\Run_{trigger_oscilloscope}V_Run5_Data_6_25_2026_Ascii.dat")
    # I know that the rate is something like 10-20Hz, so say T=10
    T = 0.5
    # I know the length of the data and the time to gather it so we can directly get N
    N = int( (df["unix_time"].iloc[-1] - df["unix_time"].iloc[0]) / T )

    # Now let's just compute the rates
    RATE = []
    for i in range(N):
        # Get the start and end time of the chunk
        t_start = df["unix_time"].iloc[0] + i*T
        t_end = t_start + T
        # Count the number of events in this chunk
        n_events = len(df[(df["unix_time"] >= t_start) & (df["unix_time"] < t_end)])
        # Compute the rate
        rate = n_events / T
        RATE.append(rate)

    # Now let's do a fit to a Gaussian distribution
    RATE_array = np.array(RATE)
    mean_rate = np.mean(RATE_array)
    std_rate = np.std(RATE_array)
    x = np.linspace(mean_rate - 3*std_rate, mean_rate + 3*std_rate, 100)
    y = 1/(std_rate * np.sqrt(2 * np.pi)) * np.exp(-0.5 * ((x - mean_rate) / std_rate)**2)

    # Now let's plot the distribution of rates
    plt.figure(figsize=(10,6))
    bins = int(0.5*np.sqrt(N))
    plt.hist(RATE,
            bins = bins,
            density = True,
            alpha = 0.6,
            histtype = 'step',
            label=f'bins={bins}')
    plt.plot(x, y, 'r-', linewidth=2, label=f'Gaussian fit (μ={mean_rate:.2f}, σ={std_rate:.2f})')
    plt.xlabel('Rate (events/s)')
    plt.ylabel('Counts')
    plt.title(f'Distribution of Event Rates (T={T}s, N={N})')
    plt.grid(True)
    plt.legend()
    plt.savefig(fr".\All_plots_with_raw_data_4Ch\Plots" + f"\\Rate_Distribution.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":
    main()