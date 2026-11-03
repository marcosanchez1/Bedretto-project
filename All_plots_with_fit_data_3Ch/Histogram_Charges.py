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
from Functions import get_raw_datFile, perform_fit_on_dataframe, f, get_t_with_fit

from scipy.integrate import quad
def perform_integral_with_fit(A):
    result, error = quad(lambda x: f(np.array([x]), A)[0] - A[6], 0, A[1])
    return result

dt = 0.3125
def main(df, df_fit, route_figure):
        # Extract amplitudes (sample 0 = peak)
        charge0, charge1, charge2 = [], [], []
        for row in df_fit['channels']:
                t0 = get_t_with_fit(row[0], 0.1)
                t1 = get_t_with_fit(row[1], 0.1)
                t2 = get_t_with_fit(row[2], 0.1)
                if True:#-10 < t1-t0 and t1-t0 < -6:
                        charge0.append(perform_integral_with_fit(row[0]))
                        charge1.append(perform_integral_with_fit(row[1]))
                        charge2.append(perform_integral_with_fit(row[2]))

        rate = round(len(charge0) / (df['unix_time'].iloc[-1] - df['unix_time'].iloc[0]), 3)

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
        def plot(ax, data, ch_label, rate):

                N = 2
                bins = int(round(N * np.sqrt(len(data)), 0))

                # Plot histogram
                ax.hist(
                        data,
                        bins=bins,
                        alpha=0.7,
                        label=f"bins={bins}",
                        range=[min(data), max(data)],
                        histtype='step',
                        density=True
                )

                # Labels
                ax.set_title(
                        f"{ch_label} charge (N={len(data)}, rate={rate}Hz)"
                )
                ax.set_ylabel("Counts")
                ax.set_xlabel(f"Charge {ch_label} (V*ns)")
                ax.legend()
                ax.grid(True)

        # -----------------------------
        # Fit each channel
        # -----------------------------
        plot(ax0, charge0, "CH0", rate)
        plot(ax1, charge1, "CH1", rate)
        plot(ax2, charge2, "CH2", rate)

        plt.tight_layout()
        plt.show()
        plt.savefig(f"{route_figure}\\Charge_Histograms.png")
        plt.close()

        return 0

# -----------------------------
# Script entry point
# -----------------------------
if __name__ == "__main__":

    trigger = '0.005'
    voltage = '57'
    run = '1'
    day = '16'
    month = '10'

    route_figure = fr".\All_plots_with_fit_data_3Ch\Plots"
    route_data = fr".\Data\Raw_data\2Bar_3Ch\OpticalGreaseTests\AfterOptical_CoinTriggerCh0Ch1Ch2_{voltage}V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii"

    df = get_raw_datFile(route_data + ".dat")
    df_fit = perform_fit_on_dataframe(df)

    main(df, df_fit, route_figure)

    print("\nEnd of execution.\n")
