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
import sys
import os

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from Functions import get_raw_datFile, get_raw_rootFile, perform_fit_on_dataframe, get_t_with_fit

dt = 0.3125
def main(df1, df2, df3 , rate1, rate2, rate3, route_figure):
    max0 = [[], [], []]
    max1 = [[], [], []]
    max2 = [[], [], []]
    for i in range(len(df1['channels'])):

        max0[0].append(df1['channels'].iloc[i][0][0])
        max0[1].append(df2['channels'].iloc[i][0][0])
        max0[2].append(df3['channels'].iloc[i][0][0])

        max1[0].append(df1['channels'].iloc[i][1][0])
        max1[1].append(df2['channels'].iloc[i][1][0])
        max1[2].append(df3['channels'].iloc[i][1][0])

        max2[0].append(df1['channels'].iloc[i][2][0])
        max2[1].append(df2['channels'].iloc[i][2][0])
        max2[2].append(df3['channels'].iloc[i][2][0])

    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    ax0, ax1, ax2, ax3 = ax.flatten()
    
    N = 2
    bins0 = int(round(N * np.sqrt(len(max0[0])),0))
    h0_1 = ax0.hist(
            max0[0],
            bins=bins0,
            alpha=0.7,
            label=f'V=55V; rate={rate1}Hz',
            range=[min(max0[0]), max(max0[0])],
            histtype='step'
            )
    h0_2 = ax0.hist(
            max0[1],
            bins=bins0,
            alpha=0.7,
            label=f'V=56V;rate={rate2}Hz',
            range=[min(max0[1]), max(max0[1])],
            histtype='step'
            )
    h0_3 = ax0.hist(
            max0[2],
            bins=bins0,
            alpha=0.7,
            label=f'V=57V; rate={rate3}Hz',
            range=[min(max0[2]), max(max0[2])],
            histtype='step'
            )
    ax0.set_title(f"Amplitude distributions CH0 (samples={len(max0[0])})")
    ax0.set_ylabel("Counts")
    ax0.set_xlabel("Amplitude CH0 (V)")
    ax0.legend()
    ax0.grid(True)

    bins1 = int(round(N * np.sqrt(len(max1[0])),0))
    h1_1 = ax1.hist(
            max1[0],
            bins=bins1,
            alpha=0.7,
            label=f'V=55V;rate={rate1}Hz',
            range=[min(max1[0]), max(max1[0])],
            histtype='step'
            )
    h1_2 = ax1.hist(
            max1[1],
            bins=bins1,
            alpha=0.7,
            label=f'V=56V;rate={rate2}Hz',
            range=[min(max1[1]), max(max1[1])],
            histtype='step'
            )
    h1_3 = ax1.hist(
            max1[2],
            bins=bins1,
            alpha=0.7,
            label=f'V=57V; rate={rate3}Hz',
            range=[min(max1[2]), max(max1[2])],
            histtype='step'
            )
    ax1.set_title(f"Amplitude distributions CH1 (samples={len(max1[0])})")
    ax1.set_ylabel("Counts")
    ax1.set_xlabel("Amplitude CH1 (V)")
    ax1.legend()
    ax1.grid(True)
    
    bins2 = int(round(N * np.sqrt(len(max2[0])),0))
    h2_1 = ax2.hist(
            max2[0],
            bins=bins2,
            alpha=0.7,
            label=f'V=55V;rate={rate1}Hz',
            range=[min(max2[0]), max(max2[0])],
            histtype='step'
            )
    h2_2 = ax2.hist(
            max2[1],
            bins=bins2,
            alpha=0.7,
            label=f'V=56V;rate={rate2}Hz',
            range=[min(max2[1]), max(max2[1])],
            histtype='step'
            )
    h2_3 = ax2.hist(
            max2[2],
            bins=bins2,
            alpha=0.7,
            label=f'V=57V; rate={rate3}Hz',
            range=[min(max2[2]), max(max2[2])],
            histtype='step'
            )
    ax2.set_title(f"Amplitude distributions CH2 (samples={len(max2[0])})")
    ax2.set_ylabel("Counts")
    ax2.set_xlabel("Amplitude CH2 (V)")
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Amp_Histograms_Bars.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":

    trigger = '0.004'
    run = '0'
    day = '20'
    month = '8'

    #route of folder where to save the figures
    route_figure = fr".\SPS_scripts\Plots"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data_1 = fr".\Data\Raw_data\10Bar_3Ch\FollowingCorrectProcedure\coincidenceCh0Ch1Ch2_Ps55V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    route_data_2 = fr".\Data\Raw_data\10Bar_3Ch\FollowingCorrectProcedure\coincidenceCh0Ch1Ch2_Ps56V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    route_data_3 = fr".\Data\Raw_data\10Bar_3Ch\FollowingCorrectProcedure\coincidenceCh0Ch1Ch2_Ps57V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    
    # Get data frame from .dat or .root file
    df1 = get_raw_datFile(route_data_1)
    df2 = get_raw_datFile(route_data_2)
    df3 = get_raw_datFile(route_data_3)

    df1 = perform_fit_on_dataframe(df1)
    df2 = perform_fit_on_dataframe(df2)
    df3 = perform_fit_on_dataframe(df3)
        
    # compute rate
    RATE1 = len(df1['unix_time'])/(df1['unix_time'].iloc[-1] - df1['unix_time'].iloc[0])
    RATE1 = int(round(RATE1, 0))

    RATE2 = len(df2['unix_time'])/(df2['unix_time'].iloc[-1] - df2['unix_time'].iloc[0])
    RATE2 = int(round(RATE2, 0))

    RATE3 = len(df3['unix_time'])/(df3['unix_time'].iloc[-1] - df3['unix_time'].iloc[0])
    RATE3 = int(round(RATE3, 0))

    main(df1, df2, df3, RATE1, RATE2, RATE3, route_figure)
    
    print("\nEnd of execution.\n")