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
    N = 7 # we have 7 parameters A0, A1, A2,...,A6

    # Create a list of 2 empty matrices one for each channel, each matrix with N rows
    # 1 for each parameter and in this rows we'll deposit the values of A0 in row zero
    # por example to later plot the histograms. 
    A = [[[] for i in range(N)], [[] for i in range(N)]]

    for row in df['channels']:
        for i in range(N):
            for j in range(2):
                A[j][i].append(row[j]['fit_parameters'][i])

    for i in range(N):
        a0 = A[0][i] # j=channel, i=parameter number(0,1,2,...,5)
        a1 = A[1][i]

        bins0 = int(round(2 * np.sqrt(len(a0)),0))
        bins1 = int(round(2 * np.sqrt(len(a1)),0))

        fig, axs = plt.subplots(1, 2, figsize=(8, 8))
        ax0, ax1 = axs.flatten()
        ax0.hist(a0,
                bins=bins0,
                alpha=0.75,
                range=[min(a0), max(a1)],
                label=f'bins={bins0};rate={int(round(RATE,0))}Hz',
                histtype = 'step'
                )
        ax0.set_title(f"A{i} Distribution - Ch0 (samples={len(a0)})")
        ax0.set_xlabel(f"A{i}")
        ax0.set_ylabel("Counts")
        ax0.legend()
        ax0.grid(True)

        ax1.hist(a1,
                bins=bins1,
                alpha=0.75,
                range=[min(a1), max(a1)],
                label=f'bins={bins1};rate={int(round(RATE,0))}Hz',
                histtype='step'
                )
        ax1.set_title(f"A{i} Distribution - Ch1 (samples={len(a1)})")
        ax1.set_xlabel(f"A{i}")
        ax1.set_ylabel("Counts")
        ax1.legend()
        ax1.grid(True)

        plt.tight_layout()
        plt.savefig(f"{route_figure}\\A{i}_Histograms.png")
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