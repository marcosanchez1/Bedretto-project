import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ast

def main():
    voltage = 60
    trigger_oscilloscope = -0.990
    dt = 1  # ps

    df = pd.read_csv(
        fr".\Data\1Bar_2Chs_filtered_data\Run_{voltage}V_Run0_Data_3_10_2026_Ascii.csv"
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
        thresholds = [trigger_oscilloscope - (i * 0.01 * trigger_oscilloscope) for i in range(0,11)]#From 0 to 8 without touching 8.
    # In case we're in the positive range of thresholds for the oscilloscope
    else:
        thresholds = [trigger_oscilloscope * i for i in range(1,5)]

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
        fig, axs = plt.subplots(2, 2, figsize=(10, 8))
        ax1, ax2, ax3, ax4 = axs.flatten()

        # Number of bins for the charge distributions
        N = 6
        bins1 = int(N*np.sqrt(len(charge_ch1)))
        bins2 = int(N*np.sqrt(len(charge_ch2)))

        # Number of bins for the max. voltage distribution.
        bins3 = int(N*np.sqrt(len(max_v1)))
        bins4 = int(N*np.sqrt(len(max_v2)))

        #Plot histograms for charge distributions
        ax1.hist(charge_ch1, bins=bins1, alpha=0.7, label=f'bins={bins1};rate={int(round(RATE,0))}muons/s')
        ax1.set_title(f"Charge Distribution Distribution - Ch1 (samples={len(charge_ch1)})")
        ax1.set_xlabel("Charge (pC)")
        ax1.legend()
        ax1.grid(True)

        ax2.hist(charge_ch2, bins=bins2, alpha=0.7, label=f'bins={bins2};rate={int(round(RATE,0))}muons/s')
        ax2.set_title(f"Charge Distribution Distribution - Ch2 (samples={len(charge_ch2)})")
        ax2.set_xlabel("Charge (pC)")
        ax2.legend()
        ax2.grid(True)

        #Plot histograms for max. voltage distributions.
        ax3.hist(max_v1, bins=bins3, alpha=0.7, label=f'bins={bins3}')
        ax3.axvline(trigger_oscilloscope, color="green", label=f'Oscilloscope Th.={trigger_oscilloscope}')
        ax3.axvline(th, color="orange", label = f'2nd Threshold={round(th,3)}')
        ax3.axvline(x=mean_baseline1, color="red", label = f'Baseline={round(mean_baseline1,3)}')
        ax3.set_title("Max Voltage Distribution - Ch1")
        ax3.legend()
        ax3.grid(True)

        ax4.hist(max_v2, bins=bins4, alpha=0.7, label=f'bins={bins4}')
        ax4.axvline(trigger_oscilloscope, color="green", label=f'Oscilloscope Th. = {trigger_oscilloscope}')
        ax4.axvline(th, color="orange", label = f'2nd Threshold={round(th,3)}')
        ax4.axvline(x=mean_baseline2, color="red", label = f'Baseline={round(mean_baseline2,3)}')
        ax4.set_title("Max Voltage Distribution - Ch2")
        ax4.legend()
        ax4.grid(True)

        plt.tight_layout()
        plt.savefig(
            fr".\Photos_of_charge_distributions_1Bar_2Ch_2ndThreshold\{voltage}V_{i}_Threshold_{round(th,4)}.png"
        )
        print(f"Finished plot with threshold = {th}")

        #plt.show()

    print("\nEnd of execution.\n")

if __name__ == "__main__":
    main()