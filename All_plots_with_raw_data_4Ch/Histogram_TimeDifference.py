'''
I define time of arrival at 10% of the amplitude, and I want to see the distribution of these.

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

dt = 0.3125
def main(df, rate, route_figure):
    time_diff_01 = []
    time_diff_23 = []
    for row in df['channels']:
        t0 = get_t(row[0],0.2)
        t1 = get_t(row[1],0.2)
        t2 = get_t(row[2],0.2)
        t3 = get_t(row[3],0.2)

        time_diff_01.append(t1 - t0)
        time_diff_23.append(t3 - t2)

    fig, ax = plt.subplots(1, 2, figsize=(10, 10))
    ax0, ax1 = ax.flatten()
    
    N = 1
    bins0 = int(round(N * np.sqrt(len(time_diff_01)),0))
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

    bins1 = int(round(N * np.sqrt(len(time_diff_23)),0))
    h1 = ax1.hist(
            time_diff_23,
            bins=bins1,
            alpha=0.7,
            label=f'bins={bins1}',
            range=[min(time_diff_23), max(time_diff_23)],
            histtype='step'
            )
    ax1.set_title(f"t3-t2 distribution (samples={len(time_diff_23)};rate={rate}Hz)")
    ax1.set_ylabel("Counts")
    ax1.set_xlabel("t3-t2 (ns)")
    ax1.legend()
    ax1.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\TimeDifference_Histograms.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":

    voltage = '0.015'
    run = '1'
    day = '9'
    month = '6'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_raw_data_4Ch\Plots"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\2Bar_4Ch\CoincidenceMode\COIN_CH0123_PS57V_GL15ns\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df = get_raw_datFile(route_data)
        
    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")