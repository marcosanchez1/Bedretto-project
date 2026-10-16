'''
I define time of arrival at 10% of the amplitude, and I want to see the distribution of these.

'''
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from Functions import get_raw_datFile, perform_fit_on_dataframe, get_t_with_fit

dt = 0.3125
def main(df, rate, route_figure):
    time_diff_01 = []
    time_diff_02 = []
    time_diff_12 = []
    for row in df['channels']:
        t0 = get_t_with_fit(row[0], 0.1)
        t1 = get_t_with_fit(row[1], 0.1)
        t2 = get_t_with_fit(row[2], 0.1)

        # we could include a condition like this one to discriminate the events which are impossible to obtain.
        if abs(t0 - t1) < 12 and abs(t2 - t1) < 12:
                time_diff_01.append(t1-t0)
                time_diff_02.append(t0-t2)
                time_diff_12.append(t2-t1)

    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    ax0, ax1, ax2, ax3 = ax.flatten()
    
    N = 0.5
    bins0 = int(round( N * np.sqrt(len(time_diff_01)),0))
    h0 = ax0.hist(
            time_diff_01,
            bins=bins0,
            alpha=0.7,
            label=f'bins={bins0}',
            range=[min(time_diff_01), max(time_diff_01)],
            histtype='step'
            )
    ax0.set_title(f"t1-t0 distribution (samples={len(time_diff_01)};rate={rate}Hz)")
    ax0.set_ylabel("Counts")
    ax0.set_xlabel("t1-t0 (ns)")
    ax0.legend()
    ax0.grid(True)

    bins1 = int(round(N * np.sqrt(len(time_diff_02)),0))
    h1 = ax1.hist(
            time_diff_02,
            bins=bins1,
            alpha=0.7,
            label=f'bins={bins1}',
            range=[min(time_diff_02), max(time_diff_02)],
            histtype='step'
            )
    ax1.set_title(f"t0-t2 distribution (samples={len(time_diff_02)};rate={rate}Hz)")
    ax1.set_ylabel("Counts")
    ax1.set_xlabel("t0-t2 (ns)")
    ax1.legend()
    ax1.grid(True)

    bins2 = int(round(N * np.sqrt(len(time_diff_12)),0))
    h2 = ax2.hist(
            time_diff_12,
            bins=bins2,
            alpha=0.7,
            label=f'bins={bins2}',
            range=[min(time_diff_12), max(time_diff_12)],
            histtype='step'
            )
    ax2.set_title(f"t2-t1 distribution (samples={len(time_diff_12)};rate={rate}Hz)")
    ax2.set_ylabel("Counts")
    ax2.set_xlabel("t2-t1 (ns)")
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\TimeDifference_Histograms.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":

    trigger = '0.004'
    voltage = '57'
    run = '0'
    day = '20'
    month = '8'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_fit_data_3Ch\Plots"

    # route of original data, will only use it to compare with the fit and discriminate events
    #route_data = fr".\Data\Raw_data\10Bar_3Ch\coincidenceCh0Ch1Ch2_PS{voltage}V\Run_0.020V_Run0(changedCableCh1)_Data_8_18_2026_Ascii.dat"
    route_data = fr".\Data\Raw_data\10Bar_3Ch\FollowingCorrectProcedure\coincidenceCh0Ch1Ch2_PS{voltage}V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df = get_raw_datFile(route_data)
    df = perform_fit_on_dataframe(df)
    
    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")