'''
In this script I'll do a 1D histograms of the charges of the four channels.

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

    charge0 = []
    charge1 = []
    charge2 = []
    charge3 = []
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

        charge0.append(np.sum(ch0)*dt)
        charge1.append(np.sum(ch1)*dt)
        charge2.append(np.sum(ch2)*dt)
        charge3.append(np.sum(ch3)*dt)

    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    ax0, ax1, ax2, ax3 = ax.flatten()
    
    N = 3
    bins0 = int(round(N * np.sqrt(len(charge0)),0))
    h0 = ax0.hist(
            charge0,
            bins=bins0,
            alpha=0.7,
            label=f'bins={bins0}',
            range=[min(charge0), max(charge0)],
            histtype='step'
            )
    ax0.set_title(f"Charge distribution CH0 (samples={len(charge0)};rate={rate}Hz)")
    ax0.set_ylabel("Counts")
    ax0.set_xlabel("Charge_CH0 (V*ns)")
    ax0.legend()
    ax0.grid(True)

    bins1 = int(round(N * np.sqrt(len(charge1)),0))
    h1 = ax1.hist(
            charge1,
            bins=bins1,
            alpha=0.7,
            label=f'bins={bins1}',
            range=[min(charge1), max(charge1)],
            histtype='step'
            )
    ax1.set_title(f"Charge distribution CH1 (samples={len(charge1)};rate={rate}Hz)")
    ax1.set_ylabel("Counts")
    ax1.set_xlabel("Charge_CH1 (V*ns)")
    ax1.legend()
    ax1.grid(True)
    
    bins2 = int(round(N * np.sqrt(len(charge2)),0))
    h2 = ax2.hist(
            charge2,
            bins=bins2,
            alpha=0.7,
            label=f'bins={bins2}',
            range=[min(charge2), max(charge2)],
            histtype='step'
            )
    ax2.set_title(f"Charge distribution CH2 (samples={len(charge2)};rate={rate}Hz)")
    ax2.set_ylabel("Counts")
    ax2.set_xlabel("Charge_CH2 (V*ns)")
    ax2.legend()
    ax2.grid(True)

    bins3 = int(round(N * np.sqrt(len(charge3)),0))
    h3 = ax3.hist(
            charge3,
            bins=bins3,
            alpha=0.7,
            label=f'bins={bins3}',
            range=[min(charge3), max(charge3)],
            histtype='step'
            )
    ax3.set_title(f"Charge distribution CH3 (samples={len(charge3)};rate={rate}Hz)")
    ax3.set_ylabel("Counts")
    ax3.set_xlabel("Charge_CH3 (V*ns)")
    ax3.legend()
    ax3.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Charge_Histograms.png")
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