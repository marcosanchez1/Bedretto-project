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
from Functions import get_raw_datFile, get_t

dt = 0.3125
def main(df, rate, route_figure):

    charge0 = []
    charge1 = []
    charge2 = []
    charge3 = []
    for row in df['channels']:
        ch0 = np.array(row[0])
        baseline = np.mean(ch0[:100]) #To compute baseline we should only take like first 100 samples nothing too far.
        ch0_corr = ch0 - baseline

        ch1 = np.array(row[1])
        baseline = np.mean(ch1[:100])   # or median
        ch1_corr = ch1 - baseline

        ch2 = np.array(row[2])
        baseline = np.mean(ch2[:100])   # or median
        ch2_corr = ch2 - baseline

        ch3 = np.array(row[3])
        baseline = np.mean(ch3[:100])   # or median
        ch3_corr = ch3 - baseline

        # perform integral just until peak of signal, maybe we should even just do until 90%
        aux_charge0 = np.sum(ch0_corr[:np.argmax(ch0_corr)]) * dt
        aux_charge1 = np.sum(ch1_corr[:np.argmax(ch1_corr)]) * dt
        aux_charge2 = np.sum(ch2_corr[:np.argmax(ch2_corr)]) * dt
        aux_charge3 = np.sum(ch3_corr[:np.argmax(ch3_corr)]) * dt
        
        charge0.append(aux_charge0)
        charge1.append(aux_charge1)
        charge2.append(aux_charge2)
        charge3.append(aux_charge3)

    fig, ax = plt.subplots(2, 2, figsize=(10, 10))    
    ax0, ax1, ax2, ax3 = ax.flatten()

    N = 2
    bins0 = int(round(N * np.sqrt(len(charge0)),0))
    upper_lim = max(charge0)
    lower_lim = min(charge0)
    for _ in [charge1,charge2, charge3]:
        if upper_lim < max(_):
            upper_lim = max(_)
        if lower_lim > min(_):
            lower_lim = min(_)
    h0 = ax0.hist2d(
            charge0,
            charge1,
            bins=bins0,
            range=[[lower_lim, upper_lim], [lower_lim, upper_lim]],
            cmap='turbo'
            )
    ax0.set_title(f"Charge_CH0 vs Charge_CH1(samples={len(charge0)};bins={bins0};rate={rate}Hz)")
    ax0.set_xlabel("Charge_CH0 (V*ns)")
    ax0.set_ylabel("Charge_CH1 (V*ns)")
    plt.colorbar(h0[3], label="Counts")
    ax0.grid(True)
    
    bins1 = int(round(N * np.sqrt(len(charge2)),0))
    h1 = ax1.hist2d(
            charge2,
            charge3,
            bins=bins1,
            range=[[lower_lim, upper_lim], [lower_lim, upper_lim]],
            cmap='turbo'
            )
    ax1.set_title(f"Charge_CH2 vs Charge_CH3")
    ax1.set_xlabel("Charge_CH2 (V*ns)")
    ax1.set_ylabel("Charge_CH3 (V*ns)")
    plt.colorbar(h1[3], label="Counts")
    ax1.grid(True)

    bins2 = int(round(N * np.sqrt(len(charge0)),0))
    h2 = ax2.hist2d(
            charge0,
            charge3,
            bins=bins2,
            range=[[lower_lim, upper_lim], [lower_lim, upper_lim]],
            cmap='turbo'
            )
    ax2.set_title(f"Charge_CH0 vs Charge_CH3")
    ax2.set_xlabel("Charge_CH0 (V*ns)")
    ax2.set_ylabel("Charge_CH3 (V*ns)")
    plt.colorbar(h2[3], label="Counts")
    ax2.grid(True)

    bins3 = int(round(N * np.sqrt(len(charge1)),0))
    h3 = ax3.hist2d(
            charge1,
            charge2,
            bins=bins3,
            range=[[lower_lim, upper_lim], [lower_lim, upper_lim]],
            cmap='turbo'
            )
    ax3.set_title(f"Charge_CH1 vs Charge_CH2")
    ax3.set_xlabel("Charge_CH1 (V*ns)")
    ax3.set_ylabel("Charge_CH2 (V*ns)")
    plt.colorbar(h3[3], label="Counts")
    ax3.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Charge_vs_Charge_2DHistograms.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":

    voltage = '0.015'
    run = '3'
    day = '25'
    month = '6'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_raw_data_4Ch\Plots"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\2Bar_4Ch\CoincidenceMode\COIN_CH0123_PS57V_GL15ns\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df = get_raw_datFile(route_data)

    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")