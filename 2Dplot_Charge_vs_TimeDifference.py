'''
In this script I'll try to plot TimeR vs TimeL in a 2D histogram maybe? or simply a plot?
Federico said that we should only look at the difference in times, he said to look at the difference
in times at 10% of amplitude but I'll take at the amplitude I think it's easier and the same.
Also the plot I'm not quite sure but I think I'll do a 2D hi

channel,unix_time
{0:{fitting_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90},1:{0:{fitting_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90}},unix_time_0

The meaning of the parameters is in the paper but basically the're A0,A1,A2, etc...

Just as a side note we know that the whole interval of time(t) has 1024 samples, but we only parametrized from 0 to peak+30
samples, from our parameters A1 gives us the position of the peak, say it's 200, then we're gonna plot from 0 to 230.
'''

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ast
import scipy.integrate as integrate

dt = 0.312 # multiply sample_i by this to get it in ns
WINDOW = 30*dt # We did the fit until max peak +30

def main():
    Voltage = 57
    run = 0
    day = 16

    # Load fitted data
    df_fit = pd.read_csv(f".\\Data\\Processed_data\\1Bar_2Chs\\Run_{Voltage}V_Run{run}_Data_3_{day}_2026_Ascii.csv")
    df_fit["channels"] = df_fit["channels"].apply(ast.literal_eval)

    RATE = int(round(len(df_fit)/(df_fit['unix_time'].iloc[-1] - df_fit['unix_time'].iloc[0]), 0))
    
    # time difference = t0 - t1
    channel_number = 1
    charge_key = f'charge_ch{channel_number}'
    data = {'time_difference':[], charge_key:[]}

    for i in range(len(df_fit['channels'])):

        # Lets get the time at which the signal is at 10% of its
        # max. value.
        t0 = df_fit["channels"].iloc[i][0]['t_10'] # We take the t_10 of the first channel as reference time for the event.
        t1 = df_fit["channels"].iloc[i][1]['t_10'] # We take the t_10 of the second channel as reference time for the event.
        time_difference = t0 - t1

        if charge_key == 'charge_ch0':
            charge_chN = df_fit["channels"].iloc[i][0]['charge'] # We take the charge of the first channel as reference charge for the event.
        elif charge_key =='charge_ch1':
            charge_chN = df_fit["channels"].iloc[i][1]['charge'] # We take the charge of the second channel as reference charge for the event.

        if True:#time_difference >= -1 and time_difference <= 1:     
            # We append the values of t
            data['time_difference'].append(t0 - t1)
            
            # We append values of charge
            data[charge_key].append(charge_chN)

    # Now let's just plot tL vs tR
    plt.figure(figsize=(8,5))

    N = 1
    n_bins = int(round(N * np.sqrt(len(data['time_difference'])),0))
    time_limits = [min(data['time_difference']), max(data['time_difference'])]
    charge_limits = [min(data[charge_key]), max(data[charge_key])]
    h = plt.hist2d(
                   data['time_difference'],
                   data[charge_key],
                   bins=n_bins,
                   cmap="turbo",
                   range = [time_limits,charge_limits]
                   )
    plt.ylabel(f'Charge-{channel_number} (V*ns)') #I shouldn't call it time of arrival it may generate confusion
    plt.xlabel('Time Difference(t0 - t1; in ns)')
    plt.colorbar(h[3], label="Counts")
    plt.title(f"Charge-{channel_number} vs Time Difference. bins={n_bins};rate={RATE};events={len(data['time_difference'])}")
    plt.grid(True)
    plt.tight_layout()
    #plt.gca().set_aspect('equal', adjustable='box')
    #plt.axis('equal')
    plt.show()

if __name__ == "__main__":
    main()