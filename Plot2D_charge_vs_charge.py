import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ast


def main(route_data, route_figure):

    # Load fitted data
    df_fit = pd.read_csv(route_data)
    df_fit["channels"] = df_fit["channels"].apply(ast.literal_eval)

    RATE = int(round(len(df_fit)/(df_fit['unix_time'].iloc[-1] - df_fit['unix_time'].iloc[0]), 0))

    data = {'charge_0':[], 'charge_1':[]}
    for i in range(len(df_fit['channels'])):
        data['charge_0'].append(df_fit['channels'].iloc[i][0]['charge'])
        data['charge_1'].append(df_fit['channels'].iloc[i][1]['charge'])


    # Now let's just plot tL vs tR
    plt.figure(figsize=(8,5))

    n_bins = int(round(np.sqrt(len(data['charge_0'])),0))
    h = plt.hist2d(
                   data['charge_0'],
                   data['charge_1'],
                   bins=n_bins,
                   cmap="turbo",
                   range = [[min(data['charge_0']), max(data['charge_0'])], [min(data['charge_1']), max(data['charge_1'])]]
                   )
    plt.ylabel('Charge channel-1') #I shouldn't call it time of arrival it may generate confusion
    plt.xlabel('Charge channel-0')
    plt.colorbar(h[3], label="Counts")
    plt.title(f"Charge-1 vs Charge-0. bins={n_bins};rate={RATE};events={len(data['charge_0'])}")
    plt.grid(True)
    plt.tight_layout()
    
    plt.savefig(f"{route_figure}\\Charge_1_vs_Charge_0.png")
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