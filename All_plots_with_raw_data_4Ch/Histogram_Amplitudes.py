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
from Functions import get_raw_datFile, get_raw_rootFile, perform_fit_on_dataframe, f, get_t_with_samples

dt = 0.3125
def main(df, rate, route_figure):
        max0 = []
        max1 = []
        max2 = []
        max3 = []
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

                ch3 = np.array(row[3])
                baseline_3 = np.mean(ch3[:100])   # or median
                ch3_corr = ch3 - baseline_3
                A3 = np.max(ch3_corr)

                max0.append(A0)
                max1.append(A1)
                max2.append(A2)
                max3.append(A3)

        fig, ax = plt.subplots(2, 2, figsize=(10, 10))
        ax0, ax1, ax2, ax3 = ax.flatten()

        N = 2
        bins0 = int(round(N * np.sqrt(len(max0)),0))
        # Histogram
        h0 = ax0.hist(
        max0,
        bins=bins0,
        alpha=0.7,
        range=[min(max0), max(max0)],
        histtype='step',
        label=f'bins={bins0}',
        )
        # Title and axes
        ax0.set_title(f"Amplitude distribution CH0(samples={len(df['channels'])};rate={rate})")
        ax0.set_ylabel("Counts")
        ax0.set_xlabel("Amplitude CH0 (V)")
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
        ax1.set_title(f"Amplitude distribution CH1(samples={len(df['channels'])};rate={rate})")
        ax1.set_ylabel("Counts")
        ax1.set_xlabel("Amplitude CH1 (V)")
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
        ax2.set_title(f"Amplitude distribution CH2(samples={len(df['channels'])};rate={rate})")
        ax2.set_ylabel("Counts")
        ax2.set_xlabel("Amplitude CH2 (V)")
        ax2.legend()
        ax2.grid(True)

        bins3 = int(round(N * np.sqrt(len(max3)),0))
        h3 = ax3.hist(
                max3,
                bins=bins3,
                alpha=0.7,
                label=f'bins={bins3}',
                range=[min(max3), max(max3)],
                histtype='step'
                )
        ax3.set_title(f"Amplitude distribution CH3(samples={len(df['channels'])};rate={rate})")
        ax3.set_ylabel("Counts")
        ax3.set_xlabel("Amplitude CH3 (V)")
        ax3.legend()
        ax3.grid(True)

        plt.tight_layout()
        plt.savefig(f"{route_figure}\\Amp_Histograms.png")
        plt.show()
        plt.close()

        return 0

if __name__ == "__main__":
    voltage = '57'
    trigger = '0.004'
    run = '0'
    day = '24'
    month = '8'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_raw_data_4Ch\Plots"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\2Bar_4Ch\CoincidenceMode\FollowingCorrectProcedure\coincidenceCh0Ch1Ch2Ch3_Ps{voltage}V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii"
    
    # Get data frame from .dat or .root file
    df = get_raw_datFile(route_data + ".dat")
    #df = get_raw_rootFile(route_data + ".root")
        
    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")