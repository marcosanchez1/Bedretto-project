'''
In this script I'll do the 2D histogram of time_ch0 vs time_ch1, but discriminating events based on a 2nd threshold that I
apply offline.

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
def main(df, route_figure):

    threshold = 0.2
    time0, time1 = [], []
    counts = 0
    for row in df['channels']:
        ch0 = row[0]
        ch1 = row[1]
        if np.max(ch0) < threshold and np.max(ch1) < threshold:
            time0.append(np.argmax(ch0)*dt)
            time1.append(np.argmax(ch1)*dt)
            counts += 1
    rate = int(round(counts / (df['unix_time'].iloc[-1] - df['unix_time'].iloc[0]),0))
    plt.figure(figsize=(8,6))
    n_bins = int(round(np.sqrt(len(time0)),0))
    plt.hist2d(time0, time1, bins=n_bins, cmap='turbo')
    plt.colorbar(label='Counts')
    plt.title(f'Time CH0 vs Time CH1; max_ch0,max_ch1<{threshold} (rate={rate}Hz)')
    plt.xlabel('Time CH0 (ns)')
    plt.ylabel('Time CH1 (ns)')
    plt.grid(True)
    plt.show()

    print(f"Number of events passing the threshold: {counts}")
    return 0

if __name__ == "__main__":

    print("\nStarting execution of Time_vs_Time.py\n")

    voltage = '0.003'
    run = '17'
    day = '6'
    month = '5'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_raw_data\Plots\1Bar_2Chs\57Vcoincidence\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\1Bar_2Chs\57Vcoincidence\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df = get_raw_data(route_data)

    main(df, route_figure)
    
    print("\nEnd of execution.\n")