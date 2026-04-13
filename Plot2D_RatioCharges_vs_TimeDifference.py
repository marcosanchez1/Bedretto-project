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


def main(route_data, route_figure):

    # Load fitted data
    df_fit = pd.read_csv(route_data)
    df_fit["channels"] = df_fit["channels"].apply(ast.literal_eval)

    RATE = int(round(len(df_fit)/(df_fit['unix_time'].iloc[-1] - df_fit['unix_time'].iloc[0]), 0))

    # time difference = t0 - t1
    # charge ratio charge0/charge1
    data = {'time_difference':[], 'charge_ratio':[]}
    for i in range(len(df_fit['channels'])):

        # Lets get the time at which the signal is at 10% of its
        # max. value.
        t0 = df_fit['channels'].iloc[i][0]['t_10']
        t1 = df_fit['channels'].iloc[i][1]['t_10']

        charge_ch0 = df_fit['channels'].iloc[i][0]['charge']
        charge_ch1 = df_fit['channels'].iloc[i][1]['charge']

        if charge_ch1 == 0:
            continue
        else:
            data['charge_ratio'].append(charge_ch0/charge_ch1)
            data['time_difference'].append(t0 - t1)


    # Now let's just plot tL vs tR
    plt.figure(figsize=(8,5))

    n_bins = int(round(np.sqrt(len(data['time_difference'])),0))
    h = plt.hist2d(
                   data['time_difference'],
                   data['charge_ratio'],
                   bins=n_bins,
                   cmap="turbo",
                   range = [[min(data['time_difference']), max(data['time_difference'])], [min(data['charge_ratio']), max(data['charge_ratio'])]]
                   )
    plt.ylabel('Charge Ratio(charge0/charge1)') #I shouldn't call it time of arrival it may generate confusion
    plt.xlabel('Time Difference(t0 - t1; in ns)')
    plt.colorbar(h[3], label="Counts")
    plt.title(f"Charge Ratio vs Time Difference. bins={n_bins};rate={RATE};events={len(data['time_difference'])}")
    plt.grid(True)
    plt.tight_layout()
    
    plt.savefig(f"{route_figure}\\Charge_Ratio_vs_Time_Difference.png")
    #plt.show()

if __name__ == "__main__":
    Voltage = '57'
    run = 1
    day = 9
    month = 3

    route_data = f".\\Data\\Processed_data\\1Bar_2Chs\\Run_{Voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.csv"
    route_figure = f".\\Data\\Figures\\1Bar_2Chs"

    main(route_data, route_figure)

    print("\nEnd of execution.\n")