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
from Functions import rid_of_muon_signal, get_raw_data

dt = 0.3125
def main(df, rate, route_figure):

    diff_charges = []
    for row in df['channels']:
        ch0 = np.array(row[0])
        baseline_0 = np.mean(ch0[:100]) #To compute baseline we should only take like first 100 samples nothing too far.
        ch0_corr = ch0 - baseline_0
        charge0 = np.sum(ch0_corr)*dt

        ch1 = np.array(row[1])
        baseline_1 = np.mean(ch1[:100])   # or median
        ch1_corr = ch1 - baseline_1
        charge1 = np.sum(ch1_corr)*dt

        diff_charges.append(charge0 - charge1)

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax0 = ax
    
    N = 2
    bins0 = int(round(N * np.sqrt(len(diff_charges)),0))
    h0 = ax0.hist(
            diff_charges,
            bins=bins0,
            alpha=0.7,
            label=f'bins={bins0}',
            range=[min(diff_charges), max(diff_charges)],
            histtype='step',
            density=False
            )
    ax0.set_title(f"Charge_CH0 - Charge_CH1 (samples={len(diff_charges)};rate={rate}Hz)")
    ax0.set_ylabel("Counts")
    ax0.set_xlabel("Difference in Charge (ADC*ns)")
    ax0.legend()
    ax0.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Charge_Difference_Histogram.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":

    voltage = '0.003'
    run = '17'
    day = '6'
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