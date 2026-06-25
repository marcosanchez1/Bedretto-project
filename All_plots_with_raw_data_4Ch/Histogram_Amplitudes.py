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
from Functions import get_raw_datFile

dt = 0.3125
def main(df, rate, route_figure):

    max0 = []
    max1 = []
    max2 = []
    max3 = []
    for row in df['channels']:
        ch0 = np.array(row[0])
        baseline_0 = np.mean(ch0[:100]) #To compute baseline we should only take like first 100 samples nothing too far.
        ch0_corr = ch0 - baseline_0

        ch1 = np.array(row[1])
        baseline_1 = np.mean(ch1[:100])   # or median
        ch1_corr = ch1 - baseline_1

        ch2 = np.array(row[2])
        baseline_2 = np.mean(ch2[:100])   # or median
        ch2_corr = ch2 - baseline_2

        ch3 = np.array(row[3])
        baseline_3 = np.mean(ch3[:100])   # or median
        ch3_corr = ch3 - baseline_3

        max0.append(np.max(ch0_corr))
        max1.append(np.max(ch1_corr))
        max2.append(np.max(ch2_corr))
        max3.append(np.max(ch3_corr))

    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    ax0, ax1, ax2, ax3 = ax.flatten()
    
    N = 3
    bins0 = int(round(N * np.sqrt(len(max0)),0))
    h0 = ax0.hist(
            max0,
            bins=bins0,
            alpha=0.7,
            label=f'bins={bins0}',
            range=[min(max0), max(max0)],
            histtype='step'
            )
    ax0.set_title(f"Amplitude distribution CH0 (samples={len(max0)};rate={rate}Hz)")
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
    ax1.set_title(f"Amplitude distribution CH1 (samples={len(max1)};rate={rate}Hz)")
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
    ax2.set_title(f"Amplitude distribution CH2 (samples={len(max2)};rate={rate}Hz)")
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
    ax3.set_title(f"Amplitude distribution CH3 (samples={len(max3)};rate={rate}Hz)")
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

    voltage = '0.015'
    run = '1'
    day = '9'
    month = '6'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_raw_data_4Ch\Plots"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\2Bar_4Ch\CoincidenceMode\COIN_CH0123_PS57V_GL15ns\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df = get_raw_datFile(route_data)

    #df = df[df["channels"].apply(lambda row: np.argmax(row[0])*dt > 200 and np.argmax(row[0])*dt < 250)
    #                & df["channels"].apply(lambda row: np.argmax(row[1])*dt > 200 and np.argmax(row[1])*dt < 250)]
        
    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")