'''
In this script I'll just perform two histograms of the max values of both channels noise parts aka the static line before
the actual muon peaks.

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

def main(df, rate, route_figure):

    max0 = []
    max1 = []
    for row in df['channels']:
        ch0 = np.array(row[0])
        baseline = np.mean(ch0)   # or median
        ch0_corr = ch0 - baseline

        max0.append(np.max(ch0_corr))

        ch1 = np.array(row[1])
        baseline = np.mean(ch1)   # or median
        ch1_corr = ch1 - baseline

        max1.append(np.max(ch1_corr))

    fig, ax = plt.subplots(1, 2, figsize=(10, 10))
    ax0, ax1 = ax.flatten()
    N = 2

    bins0 = int(round(N * np.sqrt(len(max0)),0))
    ax0.hist(
            max0,
            bins=bins0,
            alpha=0.7,
            range=[min(max0), max(max0)],
            label=f'bins={bins0};rate={int(round(RATE,0))}Hz;std={round(np.std(max0),3)}',
            histtype='step'
            )
    ax0.set_title(f"Max values of noise - CH0 (samples={len(max0)})")
    ax0.set_xlabel("Max values (ADC)")
    ax0.set_ylabel("Counts")
    ax0.legend()
    ax0.grid(True)

    bins1 = int(round(N * np.sqrt(len(max1)),0))
    ax1.hist(
            max1,
            bins=bins1,
            alpha=0.7,
            range=[min(max1), max(max1)],
            label=f'bins={bins1};rate={int(round(RATE,0))}Hz;std={round(np.std(max1),3)}',
            histtype='step'
            )
    ax1.set_title(f"Max values of noise - CH1 (samples={len(max1)})")
    ax1.set_xlabel("Max values (ADC)")
    ax1.set_ylabel("Counts")
    ax1.legend()
    ax1.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Max_Values_Noise_Histograms.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":

    voltage = '0.000'
    run = '6'
    day = '5'
    month = '5'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_raw_data\Plots\1Bar_2Chs\57Vcoincidence"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\1Bar_2Chs\57Vcoincidence\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df = get_raw_data(route_data)

    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    # With this function we get rid of muon peaks in both channels and we're left with only the "static" part
    # of the signal, it's working well just take into account that on the last few samples I'm taking about 10%
    # of the muon peak, so we should see a bit of bias here.
    df = rid_of_muon_signal(df)

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")