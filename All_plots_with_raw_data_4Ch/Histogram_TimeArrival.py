'''
In this script I'll do a 1D histogram of the time of arrival of signals.

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

    t0 = []
    t1 = []
    t2 = []
    t3 = []
    for row in df['channels']:
        t0.append(get_t(row[0],0.2))
        t1.append(get_t(row[1],0.2))
        t2.append(get_t(row[2],0.2))
        t3.append(get_t(row[3],0.2))

    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    ax0, ax1, ax2, ax3 = ax.flatten()
    
    N = 3
    bins0 = int(round(N * np.sqrt(len(t0)),0))
    h0 = ax0.hist(
            t0,
            bins=bins0,
            alpha=0.7,
            label=f'bins={bins0}',
            range=[min(t0), max(t0)],
            histtype='step'
            )
    ax0.set_title(f"Time of arrival distribution CH0 (samples={len(t0)};rate={rate}Hz)")
    ax0.set_ylabel("Counts")
    ax0.set_xlabel("t0 (ns)")
    ax0.legend()
    ax0.grid(True)

    bins1 = int(round(N * np.sqrt(len(t1)),0))
    h1 = ax1.hist(
            t1,
            bins=bins1,
            alpha=0.7,
            label=f'bins={bins1}',
            range=[min(t1), max(t1)],
            histtype='step'
            )
    ax1.set_title(f"Time of arrival distribution CH1 (samples={len(t1)};rate={rate}Hz)")
    ax1.set_ylabel("Counts")
    ax1.set_xlabel("t1 (ns)")
    ax1.legend()
    ax1.grid(True)
    
    bins2 = int(round(N * np.sqrt(len(t2)),0))
    h2 = ax2.hist(
            t2,
            bins=bins2,
            alpha=0.7,
            label=f'bins={bins2}',
            range=[min(t2), max(t2)],
            histtype='step'
            )
    ax2.set_title(f"Time of arrival distribution CH2 (samples={len(t2)};rate={rate}Hz)")
    ax2.set_ylabel("Counts")
    ax2.set_xlabel("t2 (ns)")
    ax2.legend()
    ax2.grid(True)

    bins3 = int(round(N * np.sqrt(len(t3)),0))
    h3 = ax3.hist(
            t3,
            bins=bins3,
            alpha=0.7,
            label=f'bins={bins3}',
            range=[min(t3), max(t3)],
            histtype='step'
            )
    ax3.set_title(f"Time of arrival distribution CH3 (samples={len(t3)};rate={rate}Hz)")
    ax3.set_ylabel("Counts")
    ax3.set_xlabel("t3 (ns)")
    ax3.legend()
    ax3.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\TimeOfArrival_Histograms.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":

    voltage = '0.005'
    run = '1'
    day = '25'
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