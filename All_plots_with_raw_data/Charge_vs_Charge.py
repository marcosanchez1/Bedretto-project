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
    charge0 = []
    charge1 = []
    for row in df['channels']:
        # We integrate only until the peak.
        aux_ch0 = np.sum(row[0][:np.argmax(row[0])]) * dt
        aux_ch1 = np.sum(row[1][:np.argmax(row[1])]) * dt

        #if(aux_ch0 > 0.2 and aux_ch1 > 0.2): # We only take events that have a positive charge in both channels, to avoid taking noise events.
        charge0.append(aux_ch0)
        charge1.append(aux_ch1)
    
    # This is to compute the new rate considering we discriminated events.
    rate = (len(charge0)/len(df['channels'])) * rate
    rate = int(round(rate, 0))

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax0 = ax
    
    N = 3
    bins0 = int(round(N * np.sqrt(len(charge0)),0))
    h0 = ax0.hist2d(
            charge0,
            charge1,
            bins=bins0,
            range=[[min(charge0), max(charge0)], [min(charge1), max(charge1)]],
            cmap='turbo',
            density = False
            )
    ax0.set_title(f"Charge_CH0 vs Charge_CH1 (samples={len(charge0)};rate={rate}Hz)")
    ax0.set_ylabel("Charge_CH1 (ADC*ns)")
    ax0.set_xlabel("Charge_CH0 (ADC*ns)")
    plt.colorbar(h0[3], label="Counts")
    ax0.grid(True)
    ax0.set_aspect('equal', adjustable='box')

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Charge_vs_Charge.png")
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