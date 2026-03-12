'''
In this script I'll try to compute a 2D histogram of the signals as the professor told me but I think I need
either an animation or to do the 2D histogram of the charges? And max. voltages?
I think I'll try to do this last thing, the 2D histogram of charges en voltages, like x = charges_ch1
y=charges_ch2 and z=frequencies of coincidences.
'''

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ast

def main():
    voltage = 60
    trigger_oscilloscope = -0.99
    day = 10
    run = 0
    dt = 1  # ps

    df = pd.read_csv(
        fr".\Data\1Bar_2Chs_filtered_data\Run_{voltage}V_Run{run}_Data_3_{day}_2026_Ascii.csv"
    )
    df["channels"] = df["channels"].apply(ast.literal_eval)

    # Extract all samples into NumPy arrays for speed
    samples1 = [np.array(ev[0]["samples"], dtype=float) for ev in df["channels"]]
    samples2 = [np.array(ev[1]["samples"], dtype=float) for ev in df["channels"]]

    # Initial and final time without taking into consideration coincidence
    DT = df['unix_time'].iloc[-1] - df['unix_time'].iloc[0]

    baselines1 = np.array([ev[0]["baseline"] for ev in df["channels"]], dtype=float)
    baselines2 = np.array([ev[1]["baseline"] for ev in df["channels"]], dtype=float)

    mean_baseline1 = baselines1.mean()
    mean_baseline2 = baselines2.mean()

    # Precompute max values
    max_v1_all = np.array([s.max() for s in samples1])
    max_v2_all = np.array([s.max() for s in samples2])

    # Baseline-subtracted signals
    samples1_bs = [s - mean_baseline1 for s in samples1]
    samples2_bs = [s - mean_baseline2 for s in samples2]

    # Precompute charges (integrals)
    charge1_all = np.array([s.sum() * dt for s in samples1_bs])
    charge2_all = np.array([s.sum() * dt for s in samples2_bs])

    # Threshold list
    #In case we're in the negative range of thresholds for the oscilloscope
    if trigger_oscilloscope < 0:
        #Just once for now
        thresholds = [trigger_oscilloscope - (i * 0.01 * trigger_oscilloscope) for i in range(0,1)]#From 0 to 8 without touching 8.
    # In case we're in the positive range of thresholds for the oscilloscope
    else:
        # Just one time for now.
        thresholds = [trigger_oscilloscope * i for i in range(1,2)]

    for i, th in enumerate(thresholds):
        # Coincidence mask
        mask = (max_v1_all >= th) & (max_v2_all >= th)

        charge_ch1 = charge1_all[mask]
        charge_ch2 = charge2_all[mask]

        max_v1 = max_v1_all[mask]
        max_v2 = max_v2_all[mask]

        # In this rate we take into account only the coincidence events, and it's the same
        # for both channels.
        RATE = len(max_v1)/(DT)

        # Plotting
        fig, axs = plt.subplots(1, 2, figsize=(10, 8))
        ax1, ax2 = axs.flatten()

        # Number of bins for the charge distributions
        N = 1
        bins_charge = int(N*np.sqrt(len(charge_ch1)))
        bins_maxV = int(N*np.sqrt(len(max_v1)))

        #Plot histograms for charge distributions
        ax1.hist2d(charge_ch1,charge_ch2, bins=bins_charge, cmap="viridis",range=[[np.min(charge_ch1), 6], [np.min(charge_ch2), 6]])
        #ax1.hist2d(charge_ch1,charge_ch2, bins=bins_charge, cmap="viridis")
        ax1.set_title(f"Charge distribution (samples={len(charge_ch1)};bins={bins_charge};rate={int(round(RATE,0))}muons/s)")
        ax1.set_xlabel("Charge channel-1 (pC)")
        ax1.set_ylabel("Charge channel-2 (pC)")
        ax1.grid(True)

        ax2.hist2d(max_v1,max_v2, bins=bins_maxV, cmap="viridis",range=[[np.min(max_v1), -0.85], [np.min(max_v2), -0.85]])
        #ax2.hist2d(max_v1,max_v2, bins=bins_maxV, cmap="viridis")
        ax2.set_title(f"Max.Voltage distribution (samples={len(max_v1)};bins={bins_maxV};rate={int(round(RATE,0))}muons/s)")
        ax2.set_xlabel("Max. Voltage channel-1 (pC)")
        ax2.set_ylabel("Max. Voltage channel-2 (pC)")
        ax2.grid(True)

        plt.tight_layout()
        plt.savefig(fr"2D_plot.png")
        print(f"Finished plot with threshold = {th}")

        plt.show()

    print("\nEnd of execution.\n")

if __name__ == "__main__":
    main()