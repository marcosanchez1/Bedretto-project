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
from Functions import rid_of_muon_signal, get_raw_data

dt = 0.3125

def main(df, rate, route_figure):
    time0 = []
    time1 = []
    for row in df['channels']:
        Amplitude0 = np.max(row[0])
        Amplitude1 = np.max(row[1])

        idx = np.where(row[0] >= Amplitude0*0.1 )[0]
        time0.append(idx[0]*dt)
        
        idx = np.where(row[1] >= Amplitude1*0.1 )[0]
        time1.append(idx[0]*dt)

    fig, ax = plt.subplots(1, 2, figsize=(10, 10))
    ax0, ax1 = ax.flatten()
    
    N = 5
    bins0 = int(round(N * np.sqrt(len(time0)),0))
    h0 = ax0.hist(
            time0,
            bins=bins0,
            alpha = 0.7,
            label = f'bins={bins0}',
            range=[min(time0), max(time0)],
            histtype='step',
            density = False
            )
    ax0.set_title(f"TimeArrival_CH0 Distribution(samples={len(time0)};rate={rate}Hz)")
    ax0.set_ylabel("Counts")
    ax0.set_xlabel("TimeArrival_CH0 (ns)")
    ax0.legend()
    ax0.grid(True)

    bins1 = int(round(N * np.sqrt(len(time1)),0))
    h1 = ax1.hist(
            time1,
            bins=bins1,
            alpha = 0.7,
            label = f'bins={bins1}',
            range=[min(time1), max(time1)],
            histtype='step',
            density = False
            )
    ax1.set_title(f"TimeArrival_CH1 Distribution(samples={len(time1)};rate={rate}Hz)")
    ax1.set_ylabel("Counts")
    ax1.set_xlabel("TimeArrival_CH1 (ns)")
    ax1.legend()
    ax1.grid(True)

    plt.tight_layout()
    #plt.savefig(f"{route_figure}\\TimeArrival_Histograms.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":

    voltage = '0.020'
    run = '10'
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

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")