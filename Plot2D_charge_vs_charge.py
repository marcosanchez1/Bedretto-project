import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ast

from Functions import discriminated_df

def main(df, RATE, route_figure):

    data = {'charge_0':[], 'charge_1':[]}

    for i in range(len(df['channels'])):
        charge_0 = df['channels'].iloc[i][0]['charge']
        charge_1 = df['channels'].iloc[i][1]['charge']
        
        data['charge_0'].append(charge_0)
        data['charge_1'].append(charge_1)


    plt.figure(figsize=(8,5))

    n_bins = int(round(np.sqrt(len(data['charge_0'])),0))
    h = plt.hist2d(
                   data['charge_0'],
                   data['charge_1'],
                   bins=n_bins,
                   cmap="turbo",
                   range = [[min(data['charge_0']), max(data['charge_0'])], [min(data['charge_1']), max(data['charge_1'])]]
                   )
    plt.ylabel('Charge channel-1 (V*ns)') #I shouldn't call it time of arrival it may generate confusion
    plt.xlabel('Charge channel-0 (V*ns)')
    plt.colorbar(h[3], label="Counts")
    plt.title(f"Charge-1 vs Charge-0. bins={n_bins};rate={RATE}Hz;events={len(data['charge_0'])}")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Charge_1_vs_Charge_0.png")
    #plt.show()

# This is in case we want to run this script alone.
if __name__ == "__main__":
    Voltage = '57'
    trigger = '0.05' # in volts.
    run = 0
    day = 16
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