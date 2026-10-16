"""
Amplitude histogram + Landau + Exponential fit
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from Functions import get_raw_datFile, perform_fit_on_dataframe

dt = 0.3125
def main(df, rate, route_figure):
        # Extract amplitudes (sample 0 = peak)
        max0 = [row[4][0] for row in df['channels']]
        max1 = [row[5][0] for row in df['channels']]
        max2 = [row[6][0] for row in df['channels']]
        max3 = [row[7][0] for row in df['channels']]

        fig = plt.figure(figsize=(10, 10))

        # Top row: CH0 and CH1
        ax0 = fig.add_subplot(2, 2, 1)
        ax1 = fig.add_subplot(2, 2, 2)
        ax2 = fig.add_subplot(2, 2, 3)
        ax3 = fig.add_subplot(2, 2, 4)

        # -----------------------------
        # Helper function to fit & plot
        # -----------------------------
        def plot(ax, data, ch_label, rate):

                N = 4
                bins = int(round(N * np.sqrt(len(data)), 0))

                # Plot histogram
                ax.hist(
                        data,
                        bins=bins,
                        alpha=0.7,
                        label=f"bins={bins}",
                        range=[min(data), max(data)],
                        histtype='step'
                )

                ax.set_title(
                        f"{ch_label} amplitude (N={len(data)}, rate={rate}Hz)"
                )
                ax.set_ylabel("Counts")
                ax.set_xlabel(f"Amplitude {ch_label} (V)")
                ax.legend()
                ax.grid(True)

        # -----------------------------
        # Fit each channel
        # -----------------------------
        plot(ax0, max0, "CH4", rate)
        plot(ax1, max1, "CH5", rate)
        plot(ax2, max2, "CH6", rate)
        plot(ax3, max3, "CH7", rate)
        plt.tight_layout()
        plt.savefig(f"{route_figure}\\Amp_Histograms_Bars.png")
        plt.show()
        plt.close()

        return 0

# -----------------------------
# Script entry point
# -----------------------------
if __name__ == "__main__":
        trigger = '-0.005'
        voltage = '57'
        run = '0'
        day = '12'
        month = '10'

        route_figure = fr".\All_plots_with_fit_data_3Ch\Plots"
        route_data = fr".\Data\Raw_data\ExternalTriggerTests\TriggerCh0_{trigger}_NoCoincidence\Run_900V_Run1_Data_10_13_2026_Ascii.dat"

        df = get_raw_datFile(route_data)
        df = perform_fit_on_dataframe(df)

        RATE = len(df['unix_time']) / (df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
        RATE = round(RATE, 3)

        main(df, RATE, route_figure)

        print("\nEnd of execution.\n")
