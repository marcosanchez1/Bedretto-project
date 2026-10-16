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

        noise0 = []
        noise1 = []
        noise2 = []
        noise3 = []
        trigger_ch0 = 0.0515
        trigger_ch1 = 0.0597
        trigger_ch2 = 0.0247
        trigger_ch3 = 0.0405
        for row in df['channels']:
                A0 = row[0][0]
                A1 = row[1][0]
                A2 = row[2][0]
                A3 = row[3][0]

                max0.append(A0)
                max1.append(A1)
                max2.append(A2)
                max3.append(A3)

                if A0 <= trigger_ch0:
                        noise0.append(A0)
                if A1 <= trigger_ch1:
                        noise1.append(A1)
                if A2 <= trigger_ch2:
                        noise2.append(A2)
                if A3 <= trigger_ch3:
                        noise3.append(A3)
        total_time = df['unix_time'].iloc[-1] - df['unix_time'].iloc[0]

        print("Noise CH0: ", len(noise0)/total_time)
        print("Noise CH1: ", len(noise1)/total_time)
        print("Noise CH2: ", len(noise2)/total_time)
        print("Noise CH3: ", len(noise3)/total_time)

        print("Muon rate CH0: ", (len(max0) - len(noise0))/total_time)
        print("Muon rate CH1: ", (len(max1) - len(noise1))/total_time)
        print("Muon rate CH2: ", (len(max2) - len(noise2))/total_time)
        print("Muon rate CH3: ", (len(max3) - len(noise3))/total_time)

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
        ax0.set_title(f"Amplitude of signals distribution CH0")
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
        ax1.set_title(f"Amplitude of signals distributiondistribution CH1")
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
        ax2.set_title(f"Amplitude of signals distribution distribution CH2")
        ax2.set_ylabel("Counts")
        ax2.set_xlabel("Max_CH2 (V)")
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
        ax3.set_title(f"Amplitude of signals distribution distribution CH3")
        ax3.set_ylabel("Counts")
        ax3.set_xlabel("Max_CH3 (V)")
        ax3.legend()
        ax3.grid(True)

        plt.tight_layout()
        plt.savefig(f"{route_figure}\\Amp_Histograms.png")
        plt.show()
        plt.close()

        return 0

if __name__ == "__main__":

    voltage = '0.020'
    run = '5'
    day = '25'
    month = '6'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_fit_data_4Ch\Plots"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\2Bar_4Ch\CoincidenceMode\COIN_CH0123_PS57V_GL15ns\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii"
    
    # Get data frame from .dat or .root file
    df = get_raw_datFile(route_data + ".dat")
    df = perform_fit_on_dataframe(df)
        
    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")