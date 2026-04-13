'''
In this script I'll just compute the histograms of the charge distributions using the raw values
for both channels so far I've been just working with channel 0 and 1 so I'll just stick to that.
'''
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ast
from Functions import get_raw_data

def main():
    voltage = '-0.980' # In 58 we just begin to distinguish the muon mountain
    #trigger_oscilloscope = -0.95
    run = 1
    day = 31
    month = 3
    dt = 0.312 # multiply sample_i by this to get it in ns

    df = get_raw_data(f".\\Data\\Raw_data\\1Bar_2Chs\\57V_varying_gatelength_and_trigger_only\\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat") 
    
    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    
    charge_ch0 = []
    charge_ch1 = []
    max_V0 = []
    max_V1 = []
    for row in df['channels']:
        baseline_ch0 = np.mean(row[0][:20]) # Assuming the first 10 samples are baseline
        charge_ch0.append(np.sum(row[0] - baseline_ch0)*dt) # Subtract baseline and multiply by dt to get charge in V*ns
        
        baseline_ch1 = np.mean(row[1][:20]) # Assuming the first 10
        charge_ch1.append(np.sum(row[1] - baseline_ch1)*dt) # Subtract baseline and multiply by dt to get charge in V*ns

        max_V0.append(np.max(row[0] - baseline_ch0)) # Subtract baseline to get the actual amplitude of the signal
        max_V1.append(np.max(row[1] - baseline_ch1)) # Subtract baseline to get the actual amplitude of the signal

    # ____________________________________________Plotting: For some reason it's taking too long to make the plots
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
    sup_lim = max(charge_ch0)
    bot_lim = min(charge_ch0)
    ax1.hist(
            charge_ch0,
            bins=bins1,
            alpha=0.7,
            range=[bot_lim, sup_lim],
            label=f'bins={bins1};rate={int(round(RATE,0))}events/s'
            )
    ax1.set_title(f"Charge(Integral) Distribution - Ch0 (samples={len(charge_ch0)})")
    ax1.set_xlabel("Charge (V*ns)")
    ax1.set_ylabel("Frequency")
    ax1.legend()
    ax1.grid(True)

    sup_lim = max(charge_ch1)
    bot_lim = min(charge_ch1)
    ax2.hist(
            charge_ch1, 
            bins=bins2,
            range=[bot_lim, sup_lim], 
            alpha=0.7, 
            label=f'bins={bins2};rate={int(round(RATE,0))}events/s'
            )
    ax2.set_title(f"Charge(Integral) Distribution - Ch1 (samples={len(charge_ch1)})")
    ax2.set_xlabel("Charge (V*ns)")
    ax2.set_ylabel("Frequency")
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
    ax3.set_title(f"Amplitude Distribution - Ch0 (samples={len(max_V0)})")
    ax3.legend()
    ax3.set_ylabel("Frequency")
    ax3.set_xlabel("Amplitude (V)")
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
    ax4.set_title(f"Amplitude Distribution - Ch1 (samples={len(max_V1)})")
    ax4.legend()
    ax4.set_ylabel("Frequency")
    ax4.set_xlabel("Amplitude (V)")
    ax4.grid(True)

    plt.tight_layout()
    plt.show()

    print("\nEnd of execution.\n")

if __name__ == "__main__":
    main()