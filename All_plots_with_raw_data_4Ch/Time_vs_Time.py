'''
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
        t0.append(get_t(row[0], 0.2))
        t1.append(get_t(row[1], 0.2))
        t2.append(get_t(row[2], 0.2))
        t3.append(get_t(row[3], 0.2))


    fig, ax = plt.subplots(2, 2, figsize=(10, 10))    
    ax0, ax1, ax2, ax3 = ax.flatten()

    N = 2
    bins0 = int(round(N * np.sqrt(len(t0)),0))
    upper_lim = max(t0)
    lower_lim = min(t0)
    for _ in [t1,t2,t3]:
        if upper_lim < max(_):
            upper_lim = max(_)
        if lower_lim > min(_):
            lower_lim = min(_)
    h0 = ax0.hist2d(
            t0,
            t1,
            bins=bins0,
            range=[[lower_lim, upper_lim], [lower_lim, upper_lim]],
            cmap='turbo'
            )
    ax0.set_title(f"t0 vs t1(samples={len(t0)};bins={bins0};rate={rate}Hz)")
    ax0.set_xlabel("t0 (ns)")
    ax0.set_ylabel("t1 (ns)")
    plt.colorbar(h0[3], label="Counts")
    ax0.grid(True)
    
    bins1 = int(round(N * np.sqrt(len(t2)),0))
    h1 = ax1.hist2d(
            t2,
            t3,
            bins=bins1,
            range=[[lower_lim, upper_lim], [lower_lim, upper_lim]],
            cmap='turbo'
            )
    ax1.set_title(f"t2 vs t3")
    ax1.set_xlabel("t2 (ns)")
    ax1.set_ylabel("t3 (ns)")
    plt.colorbar(h1[3], label="Counts")
    ax1.grid(True)

    bins2 = int(round(N * np.sqrt(len(t0)),0))
    h2 = ax2.hist2d(
            t0,
            t3,
            bins=bins2,
            range=[[lower_lim, upper_lim], [lower_lim, upper_lim]],
            cmap='turbo'
            )
    ax2.set_title(f"t0 vs t3")
    ax2.set_xlabel("t0 (ns)")
    ax2.set_ylabel("t3 (ns)")
    plt.colorbar(h2[3], label="Counts")
    ax2.grid(True)

    bins3 = int(round(N * np.sqrt(len(t1)),0))
    h3 = ax3.hist2d(
            t1,
            t2,
            bins=bins3,
            range=[[lower_lim, upper_lim], [lower_lim, upper_lim]],
            cmap='turbo'
            )
    ax3.set_title(f"t1 vs t2")
    ax3.set_xlabel("t1 (ns)")
    ax3.set_ylabel("t2 (ns)")
    plt.colorbar(h3[3], label="Counts")
    ax3.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Time_vs_time_2DHistograms.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":

    voltage = '0.015'
    run = '3'
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