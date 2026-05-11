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
from Functions import rid_of_muon_signal, get_raw_data

def main(df, rate, route_figure):
    
    min0, max0, min1, max1 = [], [], [], []
    for row in df['channels']:
        ch0 = np.array(row[0])
        baseline = np.mean(ch0)   # or median
        ch0_corr = ch0 - baseline

        ch1 = np.array(row[1])
        baseline = np.mean(ch1)   # or median
        ch1_corr = ch1 - baseline

        if np.max(ch0_corr) < 0.0055 and np.max(ch1_corr) < 0.0060:
            min0.append(-np.min(ch0_corr))
            max0.append(np.max(ch0_corr))
            min1.append(-np.min(ch1_corr))
            max1.append(np.max(ch1_corr))
    # Convert to arrays
    min0 = np.array(min0)
    max0 = np.array(max0)
    min1 = np.array(min1)
    max1 = np.array(max1)

    fig, ax = plt.subplots(1, 2, figsize=(10, 6))
    ax0, ax1 = ax.flatten()

    # Number of samples per waveform
    N = 1
    nbins = int(round(N * np.sqrt(len(min0)),0))

    # Plot histograms
    ax0.hist(min0, bins=nbins, alpha=0.7, label='-Min CH0', histtype='step', density=True)
    ax0.hist(max0, bins=nbins, alpha=0.7, label='Max CH0', histtype='step', density=True)
    ax0.set_title(f'-Min and Max Values of CH0 Noise(samples={len(min0)})')
    ax0.set_xlabel('Value(ADC)')
    ax0.set_ylabel('Frequency')
    ax0.legend()
    ax0.grid(True)

    ax1.hist(min1, bins=nbins, alpha=0.7, label='-Min CH1', histtype='step', density=True)
    ax1.hist(max1, bins=nbins, alpha=0.7, label='Max CH1', histtype='step', density=True)
    ax1.set_title(f'-Min and Max Values of CH1 Noise(samples={len(min1)})')
    ax1.set_xlabel('Value(ADC)')
    ax1.set_ylabel('Frequency')
    ax1.legend()
    ax1.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Superposition_MinMax_Noise.png")
    plt.show()
    plt.close()

if __name__ == "__main__":

    print("\nStarting execution.\n")

    voltage = '0.005'
    run = '7'
    day = '5'
    month = '5'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_raw_data\Plots\1Bar_2Chs\57Vcoincidence\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\1Bar_2Chs\57Vcoincidence\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df = get_raw_data(route_data)

    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    # With this function we get rid of muon peaks in both channels and we're left with only the "static" part
    # of the signal, it's working well just take into account that on the last few samples I'm taking about 10%
    # of the muon peak, so we should see a bit of bias here.
    df = rid_of_muon_signal(df)

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")