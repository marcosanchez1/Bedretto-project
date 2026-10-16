'''
In this script I'll do the 2D histogram of the max value of CH0 against the time at which the max value of CH0 happened, and the
same goes for CH1.

The data structure of the data frames should be something like this:
channels,unix_time
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_0
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_1
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_2
...

'''
import numpy as np
import matplotlib.pyplot as plt

import os
import sys
# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from Functions import get_raw_datFile, perform_fit_on_dataframe

def main(df, rate, route_figure):

    max0 = []
    max1 = []
    max2 = []
    for row in df['channels']:

        #if row[0][0] < 0.15 and row[1][0] < 0.15 and row[2][0] < 0.15:
        max0.append(row[0][0])
        max1.append(row[1][0])
        max2.append(row[2][0])

    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    ax0, ax1, ax2, ax3 = ax.flatten()
    N = 1
    bins0 = int(round(N * np.sqrt(len(max0)),0))
    h0 = ax0.hist2d(
            max0,
            max1,
            bins=bins0,
            range=[[min(max0), max(max0)], [min(max1), max(max1)]],
            cmap='turbo'
            )
    ax0.set_title(f"Amplitude Ch0 vs Amplitude Ch1")
    ax0.set_ylabel("Amplitude Ch1 (V)")
    ax0.set_xlabel("Amplitude Ch0 (V)")
    plt.colorbar(h0[3], label="Counts")
    ax0.grid(True)

    bins1 = int(round(N * np.sqrt(len(max0)),0))
    h1 = ax1.hist2d(
            max0,
            max2,
            bins=bins0,
            range=[[min(max0), max(max0)], [min(max2), max(max2)]],
            cmap='turbo'
            )
    ax1.set_title(f"Amplitude Ch0 vs Amplitude Ch2")
    ax1.set_xlabel("Amplitude Ch0 (V)")
    ax1.set_ylabel("Amplitude Ch2 (V)")
    plt.colorbar(h1[3], label="Counts")
    ax1.grid(True)

    bins2 = int(round(N * np.sqrt(len(max0)),0))
    h2 = ax2.hist2d(
            max1,
            max2,
            bins=bins0,
            range=[[min(max1), max(max1)], [min(max2), max(max2)]],
            cmap='turbo'
            )
    ax2.set_title(f"Amplitude Ch1 vs Amplitude Ch2")
    ax2.set_xlabel("Amplitude Ch1 (V)")
    ax2.set_ylabel("Amplitude Ch2 (V)")
    plt.colorbar(h2[3], label="Counts")
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Amp_vs_Amp.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":

    trigger = '0.005'
    voltage = '57'
    run = '0'
    day = '12'
    month = '10'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_fit_data_3Ch\Plots"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\2Bar_3Ch\OpticalGreseTests\BeforeOptical_CoinTriggerCh0Ch1Ch2_{voltage}V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii"
    
    # Get data frame from .dat or .root file
    df = get_raw_datFile(route_data + ".dat")
    df = perform_fit_on_dataframe(df)
        
    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")