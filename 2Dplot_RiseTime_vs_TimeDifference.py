'''
In this script I'll try to plot TimeR vs TimeL in a 2D histogram maybe? or simply a plot?
Federico said that we should only look at the difference in times, he said to look at the difference
in times at 10% of amplitude but I'll take at the amplitude I think it's easier and the same.
Also the plot I'm not quite sure but I think I'll do a 2D hi

channel,unix_time
{0:{fit_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90},1:{0:{fitting_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90}},unix_time_0


The meaning of the parameters is in the paper but basically the're A0,A1,A2, etc...

Just as a side note we know that the whole interval of time(t) has 1024 samples, but we only parametrized from 0 to peak+30
samples, from our parameters A1 gives us the position of the peak, say it's 200, then we're gonna plot from 0 to 230.
'''

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ast

def main():
    Voltage = '-0.920'
    run = 2
    day = 31
    month = 3

    # Load fitted data
    df_fit = pd.read_csv(f".\\Data\\Processed_data\\1Bar_2Chs\\57V_varying_gatelength_and_trigger_only\\Run_{Voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.csv")
    df_fit["channels"] = df_fit["channels"].apply(ast.literal_eval)

    RATE = int(round(len(df_fit)/(df_fit['unix_time'].iloc[-1] - df_fit['unix_time'].iloc[0]), 0))

    # We create the dictionary of data
    channel_number = 1
    rise_time_key = f'rise_time_ch_{channel_number}'
    data = {'time_difference':[], rise_time_key:[]}

    for i in range(len(df_fit['channels'])):
        time_difference = df_fit['channels'].iloc[i][0]['t_10'] - df_fit['channels'].iloc[i][1]['t_10']

        # We append the values of t
        data['time_difference'].append(time_difference)
        
        if channel_number == 0:
            RiseTime = df_fit['channels'].iloc[i][0]['t_90'] - df_fit['channels'].iloc[i][0]['t_10']
        elif channel_number == 1:
            RiseTime = df_fit['channels'].iloc[i][1]['t_90'] - df_fit['channels'].iloc[i][1]['t_10']
        
        # Append rise time
        data[rise_time_key].append(RiseTime)

    # Now let's just plot tL vs tR
    plt.figure(figsize=(8,5))

    N = 2
    n_bins = int(round(N * np.sqrt(len(data['time_difference'])),0))
    time_limits = [min(data['time_difference']), max(data['time_difference'])-30]
    RiseTime_limits = [min(data[rise_time_key]), max(data[rise_time_key])]
    h = plt.hist2d(
                   data['time_difference'],
                   data[rise_time_key],
                   bins=n_bins, #bins = n_bins x n_bins; since it's a 2D plot
                   cmap="turbo",
                   range=[time_limits, RiseTime_limits]
                   )
    plt.ylabel(f'Rise Time Ch_{channel_number} (t_90% - t_10%; in ns)')
    plt.xlabel('Time Difference(t0 - t1; in ns)')
    plt.colorbar(h[3], label="Counts")
    plt.title(f"Rise Time Ch_{channel_number} vs Time Difference. bins={n_bins};rate={RATE};events={len(data['time_difference'])}")
    plt.grid(True)
    plt.tight_layout()
    #plt.axis('equal')
    plt.show()

if __name__ == "__main__":
    main()