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
from Functions import get_raw_datFile, get_t_with_fit, perform_fit_on_dataframe

dt = 0.3125
def main(df_before, df_after, rate_before, rate_after, route_figure):

        # Extract amplitudes (sample 0 = peak)
        max0_b, max1_b, max2_b = [], [], []
        for row in df_before['channels']:
                t0 = get_t_with_fit(row[0], 0.1)
                t1 = get_t_with_fit(row[1], 0.1)
                t2 = get_t_with_fit(row[2], 0.1)
                if abs(t1 - t0) < 11 and abs(t1 - t2) <  11:
                        max0_b.append(row[0][0])
                        max1_b.append(row[1][0])
                        max2_b.append(row[2][0])

        
        max0_a, max1_a, max2_a = [], [], []
        for row in df_after['channels']:
                t0 = get_t_with_fit(row[0], 0.1)
                t1 = get_t_with_fit(row[1], 0.1)
                t2 = get_t_with_fit(row[2], 0.1)
                if abs(t1 - t0) < 11 and abs(t1 - t2) <  11:
                        max0_a.append(row[0][0])
                        max1_a.append(row[1][0])
                        max2_a.append(row[2][0])

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
        def plot(ax, data_before, data_after, ch_label, rate_before, rate_after):

                N = 2
                bins = int(round(N * np.sqrt(len(data_before)), 0))

                # Plot histogram
                ax.hist(
                        data_before,
                        bins=bins,
                        alpha=0.7,
                        label=f"Before - bins={bins}",
                        range=[min(data_before), max(data_before)],
                        histtype='step'
                )
                ax.hist(
                        data_after,
                        bins=bins,
                        alpha=0.7,
                        label=f"After - bins={bins}",
                        range=[min(data_after), max(data_after)],
                        histtype='step'
                )

                # Labels
                ax.set_title(
                        f"{ch_label} amplitude (N={len(data_before)}, rate_before={rate_before}Hz, rate_after={rate_after}Hz)"
                )
                ax.set_ylabel("Counts")
                ax.set_xlabel(f"Amplitude {ch_label} (V)")
                ax.legend()
                ax.grid(True)

        # -----------------------------
        # Fit each channel
        # -----------------------------
        plot(ax0, max0_b, max0_a, "CH0", rate_before, rate_after)
        plot(ax1, max1_b, max1_a, "CH1", rate_before, rate_after)
        plot(ax2, max2_b, max2_a, "CH2", rate_before, rate_after)

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

        route_data_before = fr".\Data\Raw_data\2Bar_3Ch\OpticalGreaseTests\BeforeOptical_CoinTriggerCh0Ch1Ch2_{voltage}V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
        route_data_after = fr".\Data\Raw_data\2Bar_3Ch\OpticalGreaseTests\AfterOptical_CoinTriggerCh0Ch1Ch2_{voltage}V\Run_{trigger}V_Run1_Data_{month}_16_2026_Ascii.dat"

        df_before = get_raw_datFile(route_data_before)
        df_before = perform_fit_on_dataframe(df_before)

        df_after = get_raw_datFile(route_data_after)
        df_after = perform_fit_on_dataframe(df_after)

        rate_before = len(df_before['unix_time']) / (df_before['unix_time'].iloc[-1] - df_before['unix_time'].iloc[0])
        rate_before = round(rate_before, 3)

        rate_after = len(df_after['unix_time']) / (df_after['unix_time'].iloc[-1] - df_after['unix_time'].iloc[0])
        rate_after = round(rate_after, 3)

        main(df_before, df_after, rate_before, rate_after, route_figure)

        print("\nEnd of execution.\n")
