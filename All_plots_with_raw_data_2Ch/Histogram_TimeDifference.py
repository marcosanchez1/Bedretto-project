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
    time_diff = []
    for row in df['channels']:
        Amplitude0 = np.max(row[0])
        Amplitude1 = np.max(row[1])

        idx = np.where(row[0] >= Amplitude0*0.1 )[0]
        time0 = idx[0]*dt
        
        idx = np.where(row[1] >= Amplitude1*0.1 )[0]
        time1 = idx[0]*dt

        time_diff.append(time1 - time0)

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    N = 2
    bins0 = int(round(N * np.sqrt(len(time_diff)),0))
    h0 = ax.hist(
            time_diff,
            bins=bins0,
            alpha = 0.7,
            label = f'bins={bins0}',
            range=[min(time_diff), max(time_diff)],
            histtype='step',
            density = False
            )
    ax.set_title(f"TimeDifference(t1-t0) Distribution(samples={len(time_diff)};rate={rate}Hz)")
    ax.set_ylabel("Counts")
    ax.set_xlabel("TimeDifference (ns)")
    ax.axvline(x=10.6125, color='red', linestyle='--', alpha=0.5, label='estimated max time difference')
    ax.axvline(x=-10.6125, color='red', linestyle='--', alpha=0.5, label='estimated min time difference')
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    #plt.savefig(f"{route_figure}\\TimeDifference_Histograms.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":

    voltage = '0.015'
    run = '9'
    day = '5'
    month = '5'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_raw_data\Plots\1Bar_2Chs\57Vcoincidence_GateLEngth_15ns\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\1Bar_2Chs\57Vcoincidence_GateLEngth_15ns\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df = get_raw_data(route_data)

    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")