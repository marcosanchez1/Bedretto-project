'''
In this script I'll do a 1D histogram of the amplitudes of the signals.

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
from Functions import get_raw_datFile, get_raw_rootFile, perform_fit_on_dataframe, f

dt = 0.3125
def main(df, rate, route_figure):

    max0 = []
    max1 = []
    max2 = []
    for row in df['channels']:
        ch0 = np.array(row[0])
        baseline_0 = np.mean(ch0[:100]) #To compute baseline we should only take like first 100 samples nothing too far.
        ch0_corr = ch0 - baseline_0
        A0 = np.max(ch0_corr)

        ch1 = np.array(row[1])
        baseline_1 = np.mean(ch1[:100])   # or median
        ch1_corr = ch1 - baseline_1
        A1 = np.max(ch1_corr)

        ch2 = np.array(row[2])
        baseline_2 = np.mean(ch2[:100])   # or median
        ch2_corr = ch2 - baseline_2
        A2 = np.max(ch2_corr)

        max0.append(A0)
        max1.append(A1)
        max2.append(A2)

    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    ax0, ax1, ax2, ax3 = ax.flatten()
    
    N = 2
    bins0 = int(round(N * np.sqrt(len(max0)),0))
    h0 = ax0.hist(
            max0,
            bins=bins0,
            alpha=0.7,
            label=f'bins={bins0}',
            range=[min(max0), max(max0)],
            histtype='step'
            )
    ax0.set_title(f"Amplitude distribution CH0 (samples={len(max0)};rate={rate}Hz)")
    ax0.set_ylabel("Counts")
    ax0.set_xlabel("Max_CH0 (V)")
    ax0.legend()
    ax0.grid(True)

    bins1 = int(round(N * np.sqrt(len(max1)),0))
    h1 = ax1.hist(
            max1,
            bins=bins1,
            alpha=0.7,
            label=f'bins={bins1}',
            range=[min(max1), max(max1)],
            histtype='step'
            )
    ax1.set_title(f"Amplitude distribution CH1 (samples={len(max1)};rate={rate}Hz)")
    ax1.set_ylabel("Counts")
    ax1.set_xlabel("Max_CH1 (V)")
    ax1.legend()
    ax1.grid(True)
    
    bins2 = int(round(N * np.sqrt(len(max2)),0))
    h2 = ax2.hist(
            max2,
            bins=bins2,
            alpha=0.7,
            label=f'bins={bins2}',
            range=[min(max2), max(max2)],
            histtype='step'
            )
    ax2.set_title(f"Amplitude distribution CH2 (samples={len(max2)};rate={rate}Hz)")
    ax2.set_ylabel("Counts")
    ax2.set_xlabel("Max_CH2 (V)")
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Amp_Histograms.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":

    trigger = '0.005'
    voltage = '57'
    run = '1'
    day = '16'
    month = '10'

    route_figure = fr".\All_plots_with_raw_data_3Ch\Plots"
    route_data = fr".\Data\Raw_data\2Bar_3Ch\OpticalGreaseTests\AfterOptical_CoinTriggerCh0Ch1Ch2_{voltage}V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii"

    df = get_raw_datFile(route_data + ".dat")

    RATE = len(df['unix_time']) / (df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = round(RATE, 3)

    main(df, RATE, route_figure)

    print("\nEnd of execution.\n")