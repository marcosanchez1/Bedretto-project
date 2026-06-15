'''
In this script I'll do the 2D histogram of the max value of CH0 against the time at which the max value of CH0 happened, and the
same goes for CH1.

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

    max0 = []
    max1 = []
    time0 = []
    time1 = []
    for row in df['channels']:
        ch0 = np.array(row[0])
        baseline = np.mean(ch0[:100]) #To compute baseline we should only take like first 100 samples nothing too far.
        ch0_corr = ch0 - baseline

        max0.append(np.max(ch0_corr))
        time0.append(np.argmax(ch0_corr) * dt)

        ch1 = np.array(row[1])
        baseline = np.mean(ch1[:100])   # or median
        ch1_corr = ch1 - baseline

        max1.append(np.max(ch1_corr))
        time1.append(np.argmax(ch1_corr) * dt)

    fig, ax = plt.subplots(1, 2, figsize=(10, 10))
    ax0, ax1 = ax.flatten()
    
    N = 2
    bins0 = int(round(N * np.sqrt(len(max0)),0))
    h0 = ax0.hist2d(
            time0,
            max0,
            bins=bins0,
            range=[[min(time0), max(time0)], [min(max0), max(max0)]],
            cmap='turbo'
            )
    ax0.set_title(f"Max_CH0 vs TimeMax_CH0(samples={len(max0)};bins={bins0};rate={int(round(RATE,0))}Hz)")
    ax0.set_ylabel("Max_CH0 (ADC)")
    ax0.set_xlabel("TimeMax_CH0 (ns)")
    plt.colorbar(h0[3], label="Counts")
    ax0.grid(True)

    bins1 = int(round(N * np.sqrt(len(time0)),0))
    h1 = ax1.hist2d(
            time1,
            max1,
            bins=bins1,
            range=[[min(time1), max(time1)], [min(max1), max(max1)]],
            cmap='turbo'
            )
    ax1.set_title(f"Max_CH1 vs TimeMax_CH1(samples={len(max1)};bins={bins1};rate={int(round(RATE,0))}Hz)")
    ax1.set_ylabel("Max_CH1 (ADC)")
    ax1.set_xlabel("TimeMax_CH1 (ns)")
    plt.colorbar(h1[3], label="Counts")
    ax1.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Amp_vs_Time_2DHistograms.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":

    voltage = '0.005'
    run = '7'
    day = '5'
    month = '5'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_raw_data\Plots\1Bar_2Chs\57Vcoincidence\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\1Bar_2Chs\57Vcoincidence\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df = get_raw_data(route_data)

    #df = df[df["channels"].apply(lambda row: np.argmax(row[0])*dt > 200 and np.argmax(row[0])*dt < 250)
    #                & df["channels"].apply(lambda row: np.argmax(row[1])*dt > 200 and np.argmax(row[1])*dt < 250)]
        
    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")