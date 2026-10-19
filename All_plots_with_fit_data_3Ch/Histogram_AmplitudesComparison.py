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
def main(df_before, df_after, rate_before, rate_after, route_figure):

        # Extract amplitudes (sample 0 = peak)
        Amplitude_ch0_before = [row[0][0] for row in df_before['channels']]
        Amplitude_ch1_before = [row[1][0] for row in df_before['channels']]
        Amplitude_ch2_before = [row[2][0] for row in df_before['channels']]

        Amplitude_ch0_after = [row[0][0] for row in df_after['channels']]
        Amplitude_ch1_after = [row[1][0] for row in df_after['channels']]
        Amplitude_ch2_after = [row[2][0] for row in df_after['channels']]

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
        plot(ax0, Amplitude_ch0_before, Amplitude_ch0_after, "CH0", rate_before, rate_after)
        plot(ax1, Amplitude_ch1_before, Amplitude_ch1_after, "CH1", rate_before, rate_after)
        plot(ax2, Amplitude_ch2_before, Amplitude_ch2_after, "CH2", rate_before, rate_after)

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

        route_data_before = fr".\Data\Raw_data\2Bar_3Ch\OpticalGreaseTests\BeforeOptical_NoCoinTriggerCh0_{voltage}V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
        route_data_after = fr".\Data\Raw_data\2Bar_3Ch\OpticalGreaseTests\AfterOptical_NoCoinTriggerCh0_{voltage}V\Run_{trigger}V_Run1_Data_{month}_16_2026_Ascii.dat"

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
