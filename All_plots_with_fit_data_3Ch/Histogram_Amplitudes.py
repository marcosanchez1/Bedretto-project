"""
Amplitude histogram + Landau + Exponential fit
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from scipy.optimize import curve_fit

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from Functions import get_raw_datFile, perform_fit_on_dataframe

dt = 0.3125

# -----------------------------
# Landau + Exponential functions
# -----------------------------

def landau_pdf(x, mpv, sigma):
    """Approximate Landau PDF."""
    return np.exp(-0.5 * ((x - mpv) / sigma + np.exp(-(x - mpv) / sigma)))

def landau_plus_exp(x, mpv, sigma, CL, CE, tau):
    """Landau + exponential tail."""
    return CL * landau_pdf(x, mpv, sigma) + CE * np.exp(-x / tau)

# -----------------------------
# Main plotting + fitting logic
# -----------------------------

def main(df, rate, route_figure):
        # Extract amplitudes (sample 0 = peak)
        max0 = [row[0][0] for row in df['channels']]
        max1 = [row[1][0] for row in df['channels']]
        max2 = [row[2][0] for row in df['channels']]

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
        def fit_and_plot(ax, data, ch_label, rate):

                N = 2
                bins = int(round(N * np.sqrt(len(data)), 0))

                # Histogram
                counts, bin_edges = np.histogram(
                        data,
                        bins=bins,
                        range=[min(data), max(data)]
                )
                bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

                # Initial guesses
                p0 = [
                        np.mean(data),     # mpv
                        np.std(data),        # sigma
                        max(counts),         # CL
                        max(counts) / 10,    # CE
                        float(trigger)        # tau
                ]

                # Fit
                params, cov = curve_fit(landau_plus_exp, bin_centers, counts, p0=p0)
                mpv, sigma, CL, CE, tau = params

                # Compute chi^2
                yfit = landau_plus_exp(bin_centers, *params)
                chi2 = np.sum((counts - yfit)**2 / (yfit + 1e-9))
                ndof = len(counts) - len(params)
                chi2_red = chi2 / ndof

                # Plot histogram
                ax.hist(
                        data,
                        bins=bins,
                        alpha=0.7,
                        label=f"bins={bins}",
                        range=[min(data), max(data)],
                        histtype='step'
                )

                # Plot fit curve
                xfit = np.linspace(min(data), max(data), 500)
                yfit_curve = landau_plus_exp(xfit, *params)
                ax.plot(xfit, yfit_curve, 'r-', label='Landau + Exp fit')

                # Labels
                ax.set_title(
                        f"{ch_label} amplitude (N={len(data)}, rate={rate}Hz)\n"
                        f"MPV={mpv:.4f}, σ={sigma:.4f}, τ={tau:.4f}, χ²/ndof={chi2_red:.2f}"
                )
                ax.set_ylabel("Counts")
                ax.set_xlabel(f"Amplitude {ch_label} (V)")
                ax.legend()
                ax.grid(True)

        # -----------------------------
        # Fit each channel
        # -----------------------------
        fit_and_plot(ax0, max0, "CH0", rate)
        fit_and_plot(ax1, max1, "CH1", rate)
        fit_and_plot(ax2, max2, "CH2", rate)

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
    route_data = fr".\Data\Raw_data\2Bar_3Ch\ExternalTriggerTests\AfterOptical_CoinTriggerCh0Ch1Ch2_{voltage}V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii"

    df = get_raw_datFile(route_data + ".dat")
    df = perform_fit_on_dataframe(df)

    RATE = len(df['unix_time']) / (df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    main(df, RATE, route_figure)

    print("\nEnd of execution.\n")
