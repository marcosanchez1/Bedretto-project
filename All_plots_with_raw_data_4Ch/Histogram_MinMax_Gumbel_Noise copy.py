'''
In this script I'll just perform two histograms of the max values of both channels noise parts aka the static line before
the actual muon peaks.

The data structure of the data frames should be something like this:
channels,unix_time
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_0
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_1
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_2
...

'''
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import norm
from scipy.optimize import curve_fit
from scipy.stats import gumbel_r

import sys
import os
# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from Functions import get_raw_datFile, rid_of_muon_signal


def plot_extrema(ax, data, title, label):
    bins = int(round(2 * np.sqrt(len(data)), 0))

    # Histogram (density=True for PDF)
    hist_vals, bin_edges, _ = ax.hist(
        data, bins=bins, density=True, histtype='step', label=label
    )

    ax.set_title(title)
    ax.set_xlabel("Max/-Min (V)")
    ax.set_ylabel("Counts")
    ax.grid(True)
    ax.legend()

def main(df, rate, route_figure):
    
    min0, max0, min1, max1 = [], [], [], []
    for row in df['channels']:
        ch0 = np.array(row[0])
        baseline = np.mean(ch0)   # or median
        ch0_corr = ch0 - baseline

        min0.append(-np.min(ch0_corr))
        max0.append(np.max(ch0_corr))

        ch1 = np.array(row[1])
        baseline = np.mean(ch1)   # or median
        ch1_corr = ch1 - baseline

        min1.append(-np.min(ch1_corr))
        max1.append(np.max(ch1_corr))
    # Convert to arrays
    min0 = np.array(min0)
    max0 = np.array(max0)
    min1 = np.array(min1)
    max1 = np.array(max1)

    fig, ax = plt.subplots(2, 2, figsize=(10, 6))
    ax0, ax1, ax2, ax3 = ax.flatten()

    # Number of samples per waveform
    N_samples = len(df['channels'].iloc[0][0])

    # Apply to both channels
    plot_extrema(ax0, min0, f"CH0 Min (rate={rate} Hz)", '-Min')
    plot_extrema(ax0, max0, f"CH0 Max (rate={rate} Hz)", 'Max')
    plot_extrema(ax2, min1, f"CH1 Min (rate={rate} Hz)", '-Min')
    plot_extrema(ax2, max1, f"CH1 Max (rate={rate} Hz)", 'Max')

    plt.tight_layout()
    #plt.savefig(f"{route_figure}\\GumbelFit_MinMax_Noise.png")
    plt.show()
    plt.close()

if __name__ == "__main__":

    voltage = '57'
    run = '5'
    day = '15'
    month = '4'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_raw_data\Plots\1Bar_2Chs\Tests"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = f".\\Data\\Raw_data\\1Bar_2Ch\\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df = get_raw_datFile(route_data)

    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    # With this function we get rid of muon peaks in both channels and we're left with only the "static" part
    # of the signal, it's working well just take into account that on the last few samples I'm taking about 10%
    # of the muon peak, so we should see a bit of bias here.
    df = rid_of_muon_signal(df)

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")