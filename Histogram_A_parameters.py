'''
The structure of the data is as follows:
channel,unix_time
{0:{fit_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90},1:{0:{fitting_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90}},unix_time_0

'''
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ast

from Functions import discriminated_df

def main(df, RATE, route_figure):

    # create a matrix with 6 rows(0,1,2,3,..,5) of empty lists that we'll fill
    A = [[[] for i in range(6)], [[] for i in range(6)]]

    for row in df['channels']:
        for i in range(6):
            for j in range(2):
                A[j][i].append(row[0]['fit_parameters'][i])

    for i in range(6):
        for j in range(2):
            a = A[j][i] # j=channel, i=parameter number(0,1,2,...,5)
            bins = int(round(2 * np.sqrt(len(a)),0))

            plt.figure(figsize=(8,5))
            plt.hist(a,
                    bins=bins,
                    alpha=0.7,
                    range=[min(a),max(a)],
                    label=f'bins={bins};rate={int(round(RATE,0))}Hz',
                    density = False
                    )
            plt.xlabel(f'A{i}')
            plt.ylabel('Counts')
            plt.title(f'A{i} fit parameter - CH{j} (samples={len(a)})')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f"{route_figure}\\A{i}_histogram_CH{j}.png")
            plt.close()
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