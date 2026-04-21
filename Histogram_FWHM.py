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

def main(df, RATE, route_figure, channel_number):
    
    # We create the dictionary of data
    FWHM = []

    for i in range(len(df['channels'])):
        # Just get the pre-computed FWHM
        fwhm = df['channels'].iloc[i][channel_number]['FWHM']
        # Append it
        FWHM.append(fwhm)

    # Now let's just plot tL vs tR
    plt.figure(figsize=(8,5))

    bins = int(round(2 * np.sqrt(len(FWHM)),0))

    plt.figure(figsize=(8,5))
    plt.hist(FWHM,
             bins=bins,
             alpha=0.7,
             range=[min(FWHM),max(FWHM)],
             label=f'bins={bins};rate={int(round(RATE,0))}Hz',
             density = False
             )
    plt.xlabel('FWHM (ns)')
    plt.ylabel('Counts')
    plt.title(f'FWHM Distribution CH{channel_number} (samples={len(FWHM)})')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{route_figure}\\FWHM_CH{channel_number}_histogram.png")
    plt.close()
    #plt.show()

# This if is in case we want to run this script alone.
if __name__ == "__main__":
    Voltage = '57'
    run = 1
    day = 9
    month = 3
    channel_number = 1
    trigger = '0.05'

    route_data = f".\\Data\\Processed_data\\1Bar_2Chs\\Run_{Voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.csv"
    route_figure = f".\\Data\\Figures\\1Bar_2Chs"

        # Load fitted data
    df = pd.read_csv(route_data)
    df["channels"] = df["channels"].apply(ast.literal_eval)

    RATE = int(round(len(df)/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0]), 0))

    # ____________________________________________Conditions____________________________________________________
    # I'll add some conditions to select or discriminate events, it can be based, on raise time or charge or whatever.
    df = discriminated_df(df, float(trigger))

    main(df, RATE, route_figure, channel_number)
    print("\nEnd of execution.\n")