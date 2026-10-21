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
from Functions import get_raw_datFile, perform_fit_on_dataframe, get_t_with_fit

dt = 0.3125
def main(df, route_figure):

        max0, max1, max2, time_difference_01 = [], [], [], []
        for row in df['channels']:
                t0 = get_t_with_fit(row[0], 0.1)
                t1 = get_t_with_fit(row[1], 0.1)
                t2 = get_t_with_fit(row[2], 0.1)
                if abs(t1 - t0) < 11 and abs(t1 - t2) <  11:
                        max0.append(row[0][0])
                        max1.append(row[1][0])
                        max2.append(row[2][0])
                        time_difference_01.append(t1 - t0)
        rate = round(len(max0) / (df['unix_time'].iloc[-1] - df['unix_time'].iloc[0]), 3)

        fig = plt.figure(figsize=(10, 10))

        # Top row: CH0 and CH1
        ax0 = fig.add_subplot(2, 2, 1)
        ax1 = fig.add_subplot(2, 2, 2)

        # Bottom row: CH2 centered (span both columns)
        ax2 = fig.add_subplot(2, 1, 2)   # 2 rows, 1 column, second row

        # No ax3 needed


        # -----------------------------
        # Helper function to fit & plot
        # -----------------------------
        def plot(ax, data_x, data_y, ch_x_label, ch_y_label, rate):

                N = 2
                bins = int(round(N * np.sqrt(len(data_x)), 0))

                # Plot histogram
                h = ax.hist2d(
                        data_x,
                        data_y,
                        bins=bins,
                        range=[[min(data_x), max(data_x)], [min(data_y), max(data_y)]],
                        cmap='turbo'
                )
                plt.colorbar(h[3], label="Counts")

                # Labels
                ax.set_title(
                        f"{ch_x_label} vs {ch_y_label} amplitude (N={len(data_x)}, rate={rate}Hz)"
                )
                ax.set_ylabel(f"Amplitude {ch_y_label} (V)")
                ax.set_xlabel(f"Amplitude {ch_x_label} (V)")
                ax.grid(True)

        # -----------------------------
        # Fit each channel
        # -----------------------------
        plot(ax0, max0, max1, "CH0", "CH1", rate)
        plot(ax1, max1, max2, "CH1", "CH2", rate)
        plot(ax2, max0, max2, "CH2", "CH0", rate)

        plt.tight_layout()
        plt.savefig(f"{route_figure}\\Amp_Histograms_Bars.png")
        plt.show()
        plt.close()

        return 0

# -----------------------------
# Script entry point
# -----------------------------
if __name__ == "__main__":

    trigger = '0.005'
    voltage = '57'
    run = '0'
    day = '12'
    month = '10'

    route_figure = fr".\All_plots_with_fit_data_3Ch\Plots"
    route_data = fr".\Data\Raw_data\2Bar_3Ch\OpticalGreaseTests\BeforeOptical_CoinTriggerCh0Ch1Ch2_{voltage}V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii"

    df = get_raw_datFile(route_data + ".dat")
    df = perform_fit_on_dataframe(df)

    main(df, route_figure)

    print("\nEnd of execution.\n")
