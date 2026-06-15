'''
Data structure:

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

from Functions import discriminated_df

def main(df, RATE, route_figure):

    data = {'time_difference':[], 'amplitude_ratio':[]}
    for i in range(len(df['channels'])):

        # Lets get the time at which the signal is at 10% of its
        # max. value.
        t0 = df['channels'].iloc[i][0]['t_10']
        t1 = df['channels'].iloc[i][1]['t_10']

        amplitude_ch0 = df['channels'].iloc[i][0]['fit_parameters'][0]
        amplitude_ch1 = df['channels'].iloc[i][1]['fit_parameters'][0]

        # What else could we have done?
        if amplitude_ch1 == 0:
            continue
        else:
            data['amplitude_ratio'].append(amplitude_ch0/amplitude_ch1)
            data['time_difference'].append(t0 - t1)


    # Now let's just plot tL vs tR
    plt.figure(figsize=(8,5))

    n_bins = int(round(np.sqrt(len(data['time_difference'])),0))
    h = plt.hist2d(
                   data['time_difference'],
                   data['amplitude_ratio'],
                   bins=n_bins,
                   cmap="turbo",
                   range = [[min(data['time_difference']), max(data['time_difference'])], [min(data['amplitude_ratio']), max(data['amplitude_ratio'])]]
                   )
    plt.ylabel('Amplitude Ratio(A0_CH0/A0_CH1)') #I shouldn't call it time of arrival it may generate confusion
    plt.xlabel('Time Difference(t0 - t1; in ns)')
    plt.colorbar(h[3], label="Counts")
    plt.title(f"Amplitude Ratio vs Time Difference. bins={n_bins};rate={RATE}Hz;events={len(data['time_difference'])}")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Amplitude_Ratio_vs_Time_Difference.png")
    #plt.show()
    plt.close()

# This is in case we want to run this script alone.
if __name__ == "__main__":
    Voltage = '57'
    trigger = '0.05' # in volts.
    run = 1
    day = 9
    month = 3

    route_data = f".\\Data\\Processed_data\\1Bar_2Chs\\Run_{Voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.csv"
    route_figure = f".\\Data\\Figures\\1Bar_2Chs"

    # Load fitted data
    df = pd.read_csv(route_data)
    df["channels"] = df["channels"].apply(ast.literal_eval)
    
    RATE = int(round(len(df)/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0]), 0))
    
    # ____________________________________________Conditions____________________________________________________
    # I'll add some conditions to select or discriminate events, it can be based, on raise time or charge or whatever.
    df = discriminated_df(df, float(trigger))

    main(df, RATE, route_figure)

    print("\nEnd of execution.\n")