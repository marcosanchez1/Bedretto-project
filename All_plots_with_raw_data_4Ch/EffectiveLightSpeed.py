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
c = 30 # cm/ns
d = 5
L = 170

def main(df, route_figure, trigger):
    DELTA_X_PLUS = []
    DELTA_X_MINUS = []
    
    DELTA_T = []
    DELTA_T_aux = []

    for index, row in df.iterrows():
        ch0 = row['channels'][0]
        ch1 = row['channels'][1]
        ch2 = row['channels'][2]
        ch3 = row['channels'][3]

        peak0 = np.max(ch0)
        peak1 = np.max(ch1)
        peak2 = np.max(ch2)
        peak3 = np.max(ch3)

        # Find the index of the maximum value in each channel
        t0 = get_t(ch0, 0.2)
        t1 = get_t(ch1, 0.2)
        t2 = get_t(ch2, 0.2)
        t3 = get_t(ch3, 0.2)

        time_window = 20
        # Check if all peaks are above the trigger threshold and if the time differences are within time window
        if peak0 >= trigger and peak1 >= trigger and peak2 >= trigger and peak3 >= trigger:
            #if abs(t0 - t1) < time_window and abs(t2 - t3) < time_window:  # Check if the time differences are within time window
                
                delta_t = (t1 + t0 - t3 - t2)/2
                if delta_t < 0.166 or delta_t > 5.699:
                            # By definition delta_t cannot be negative and the maximum value it can
                            # have according to my calculations is 5.699ns
                            # This could substitute the time window check.
                            continue

                # Instead of sqrt we use binomial expansion to avoid complex number
                #delta_x = np.sqrt((c*delta_t)**2 - d**2)
                x = -(d/(c*delta_t))**2
                delta_x = c*delta_t*(1 + 0.5*x - 0.125*x**2) # binomial expansion up to second order

                DELTA_T.append(delta_t)
                DELTA_T_aux.append(delta_t + t3 - t1)
                DELTA_X_PLUS.append(delta_x)
                DELTA_X_MINUS.append(-delta_x)

    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    N = 2
    N_bins = int( round( N*np.sqrt(len(DELTA_X_PLUS)) ,0) )

    axs[0, 0].hist(DELTA_X_PLUS, bins=N_bins, histtype='step', color='green', alpha=0.7, label=f'(+),bins={N_bins}')
    axs[0, 0].hist(DELTA_X_MINUS, bins=N_bins, histtype='step', color='blue', alpha=0.7, label=f'(-),bins={N_bins}')
    axs[0, 0].set_title(f'x - x\' Distribution (samples={len(DELTA_X_PLUS)})')
    axs[0, 0].set_xlabel('Position (cm)')
    axs[0, 0].set_ylabel('Frequency')
    axs[0, 0].legend()
    axs[0, 0].grid(True)

    axs[0, 1].hist(DELTA_T, bins=N_bins, histtype='step', color='red', alpha=0.7, label=f'bins={N_bins}')
    axs[0, 1].set_title(f't\' - t Distribution (samples={len(DELTA_T)})')
    axs[0, 1].set_xlabel('Time (ns)')
    axs[0, 1].set_ylabel('Frequency')
    axs[0, 1].legend()
    axs[0, 1].grid(True)

    im = axs[1, 0].hist2d(DELTA_T_aux, DELTA_X_PLUS, bins=N_bins, cmap='turbo')
    axs[1, 0].set_title(f't\' - t + t3 - t1 vs (x - x\')_plus (samples={len(DELTA_X_PLUS)})')
    axs[1, 0].set_xlabel('Time (ns)')
    axs[1, 0].set_ylabel('Position (cm)')
    fig.colorbar(im[3], ax=axs[1, 0], label='Counts')

    im = axs[1, 1].hist2d(DELTA_T_aux, DELTA_X_MINUS, bins=N_bins, cmap='turbo')
    axs[1, 1].set_title(f't\' - t + t3 - t1 vs (x - x\')_minus (samples={len(DELTA_X_MINUS)})')
    axs[1, 1].set_xlabel('Time (ns)')
    axs[1, 1].set_ylabel('Position (cm)')
    fig.colorbar(im[3], ax=axs[1, 1], label='Counts')

    plt.tight_layout()
    plt.savefig(f"{route_figure}/SpeedPositionTime_Distributions.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":
    print('\nStart execution.\n')

    voltage = '0.015'
    run = '3'
    day = '17'
    month = '6'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_raw_data_4Ch\Plots"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\2Bar_4Ch\NormalMode\TriggerCh0\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df = get_raw_datFile(route_data)

    main(df, route_figure, float(voltage))
    
    print("\nEnd of execution.\n")