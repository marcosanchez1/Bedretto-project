'''
In this script I'll do the 2D histogram of the max value of CH0 against the max value of CH1, and by request of prof. I'll
also do the 2D histogram of the time at which the max value of CH0 is reached against the time at which the max value of CH1
is reached.
And it's important to noe that for this script I'll take the whole signal, including the muon peaks according to what prof said.

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

    charge0 = []
    charge1 = []
    for row in df['channels']:
        ch0 = np.array(row[0])
        baseline = np.mean(ch0[:100]) #To compute baseline we should only take like first 100 samples nothing too far.
        ch0_corr = ch0 - baseline

        ch1 = np.array(row[1])
        baseline = np.mean(ch1[:100])   # or median
        ch1_corr = ch1 - baseline

        aux_charge0 = np.sum(ch0_corr) * dt
        aux_charge1 = np.sum(ch1_corr) * dt
        
        charge0.append(aux_charge0)
        charge1.append(aux_charge1)

    rate = int(round(len(charge0) / len(df) * rate, 0))

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))    
    N = 2
    bins0 = int(round(N * np.sqrt(len(charge0)),0))
    h0 = ax.hist2d(
            charge0,
            charge1,
            bins=bins0,
            range=[[min(charge0), 2], [min(charge1), 2]],
            cmap='turbo'
            )
    ax.set_title(f"Charge_CH0 vs Charge_CH1(samples={len(charge0)};bins={bins0};rate={rate}Hz)")
    ax.set_xlabel("Charge_CH0 (ADC*ns)")
    ax.set_ylabel("Charge_CH1 (ADC*ns)")
    plt.colorbar(h0[3], label="Counts")
    ax.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Charge_vs_Charge_2DHistograms.png")
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

    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")