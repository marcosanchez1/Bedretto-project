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

from Functions import discriminated_df

def main(df, RATE, route_figure): 
    #I may get negative values if we put an offset that moves the signal below the x-axis and I guess it makes sens
    # we get a "negative area" since we're computing it in the negative y-axis.
    charge_ch0 = [row[0]['charge'] for row in df["channels"]]
    charge_ch1 = [row[1]['charge'] for row in df["channels"]]

    max_V0 = [row[0]['fit_parameters'][0] for row in df['channels']] #parameters[0]=A0 which is the amplitude not considering baseline.
    max_V1 = [row[1]['fit_parameters'][0] for row in df['channels']]

    # ____________________________________________Plotting____________________________________________________
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))
    ax1, ax2, ax3, ax4 = axs.flatten()

    N = 2 # With this we'll control the number of bins (N * sqr(len(data)))
    # Number of bins for the charge distributions
    bins1 = int(N * np.sqrt(len(charge_ch0)))
    bins2 = int(N * np.sqrt(len(charge_ch1)))

    # Number of bins for the max. voltage distribution.
    bins3 = int(N * np.sqrt(len(max_V0)))
    bins4 = int(N * np.sqrt(len(max_V1)))

    #Plot histograms for charge distributions
    bot_lim = min(charge_ch0)
    sup_lim = max(charge_ch0)
    ax1.hist(
            charge_ch0,
            bins=bins1,
            alpha=0.7,
            range=[bot_lim, sup_lim],
            label=f'bins={bins1};rate={int(round(RATE,0))}Hz'
            )
    ax1.set_title(f"Charge(Integral) Distribution - Ch0 (samples={len(charge_ch0)})")
    ax1.set_xlabel("Charge (ADC*ns)")
    ax1.set_ylabel("Counts")
    ax1.legend()
    ax1.grid(True)

    bot_lim = min(charge_ch1)
    sup_lim = max(charge_ch1)
    ax2.hist(
            charge_ch1, 
            bins=bins2,
            range=[bot_lim, sup_lim], 
            alpha=0.7, 
            label=f'bins={bins2};rate={int(round(RATE,0))}Hz'
            )
    ax2.set_title(f"Charge(Integral) Distribution - Ch1 (samples={len(charge_ch1)})")
    ax2.set_xlabel("Charge (ADC*ns)")
    ax2.set_ylabel("Counts")
    ax2.legend()
    ax2.grid(True)

    #Plot histograms for max. voltage distributions.
    sup_lim = max(max_V0)
    bot_lim = min(max_V0)
    ax3.hist(
            max_V0, 
            bins=bins3,
            range=[bot_lim, sup_lim], 
            alpha=0.7, 
            label=f'bins={bins3}'
            )
    ax3.set_title(f"Amplitude(A0) Distribution - Ch0 (samples={len(max_V0)})")
    ax3.legend()
    ax3.set_ylabel("Counts")
    ax3.set_xlabel("A0 (ADC)")
    ax3.grid(True)

    sup_lim = max(max_V1)
    bot_lim = min(max_V1)
    ax4.hist(
            max_V1, 
            bins=bins4,
            range=[bot_lim, sup_lim], 
            alpha=0.7, 
            label=f'bins={bins4}'
            )
    ax4.set_title(f"Amplitude(A0) Distribution - Ch1 (samples={len(max_V1)})")
    ax4.legend()
    ax4.set_ylabel("Counts")
    ax4.set_xlabel("A0 (ADC)")
    ax4.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Charge_and_Amplitude_Distributions.png")
    plt.close()
    #plt.show()
    
    return 0

# this is in case we want to run this script separately
if __name__ == "__main__":
    voltage = '57' # In 58 we just begin to distinguish the muon mountain
    trigger = '0.05' # in volts.
    run = 0
    day = 16
    month = 3
    
    route_data = f".\\Data\\Processed_data\\1Bar_2Chs\\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.csv"
    #route_data = f".\\Data\\Processed_data\\1Bar_2Chs\\57V_varying_gatelength_and_trigger_only\\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.csv"

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