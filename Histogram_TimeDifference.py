'''
In this script I'll just compute the histograms of the charge distributions using the fitted values
for both channels so far I've been just working with channel 0 and 1 so I'll just stick to that.
The structure of the data is as follows:
channel,unix_time
{0:{fit_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90},1:{0:{fitting_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90}},unix_time_0

'''
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ast

from Condition_to_take_event import discriminated_df

def main(df, RATE, route_figure):

    TIME_DIFF = [row[0]['t_10'] - row[1]['t_10'] for row in df['channels']]

    bins = int(round(2 * np.sqrt(len(TIME_DIFF)),0))

    plt.figure(figsize=(8,5))
    plt.hist(TIME_DIFF,
             bins=bins,
             alpha=0.7,
             range=[-11,11],
             label=f'bins={bins};rate={int(round(RATE,0))}Hz')
    plt.xlabel('Time Difference (t0 - t1 in ns)')
    plt.ylabel('Frequency')
    plt.title(f'Time Difference Distribution (samples={len(TIME_DIFF)})')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Time_Difference_histogram.png")
    #plt.show()
    
    return 0

if __name__ == "__main__":
    voltage = '-0.920' # In 58 we just begin to distinguish the muon mountain
    trigger = '0.05' # in volts.
    run = 1
    day = 31
    month = 3
    
    #route_data = f".\\Data\\Processed_data\\1Bar_2Chs\\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.csv"
    route_data = f".\\Data\\Processed_data\\1Bar_2Chs\\57V_varying_gatelength_and_trigger_only\\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.csv"
    
    route_figure = f".\\Data\\Figures\\1Bar_2Chs"

    df = pd.read_csv(route_data)
    df["channels"] = df["channels"].apply(ast.literal_eval)

    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    
    # ____________________________________________Conditions____________________________________________________
    # I'll add some conditions to select or discriminate events, it can be based, on raise time or charge or whatever.
    df = discriminated_df(df, float(trigger))
    
    main(df, RATE, route_figure)

    print("\nEnd of execution.\n")