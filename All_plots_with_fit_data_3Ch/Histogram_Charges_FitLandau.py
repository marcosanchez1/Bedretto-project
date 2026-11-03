"""
Charge histogram + Landau + Exponential fit
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from Functions import get_raw_datFile, perform_fit_on_dataframe, f, get_t_with_fit

from scipy.optimize import curve_fit
# ----------------------------------------------------------
# Landau approximation
# ----------------------------------------------------------

def landau_pdf(x, mpv, sigma):
    z = (x - mpv) / sigma
    return np.exp(-0.5 * (z + np.exp(-z)))

# ----------------------------------------------------------
# Landau + exponential
# ----------------------------------------------------------

def landau_plus_exp(x,
                    mpv,
                    sigma,
                    A_landau,
                    A_exp,
                    tau):

    return (
        A_landau * landau_pdf(x, mpv, sigma)
        +
        A_exp * np.exp(-x/tau)
    )

dt = 0.3125
def main(df, df_fit, route_figure):
        # Extract amplitudes (sample 0 = peak)
        charge0, charge1, charge2 = [], [], []
        for i in range(len(df['channels'])):
                charge0.append(np.sum(df['channels'].iloc[i][0] - df_fit['channels'].iloc[i][0][6]) * dt)
                charge1.append(np.sum(df['channels'].iloc[i][1] - df_fit['channels'].iloc[i][1][6]) * dt)
                charge2.append(np.sum(df['channels'].iloc[i][2] - df_fit['channels'].iloc[i][2][6]) * dt)

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
        def fit_and_plot(ax, data, ch_label, rate):
                N = 1
                bins = int(round(N*np.sqrt(len(data)),0))

                # ---------------------------------
                # Histogram
                # ---------------------------------

                counts, edges = np.histogram(
                        data,
                        bins=bins,
                        density=True
                )

                centers = 0.5*(edges[:-1] + edges[1:])

                # ---------------------------------
                # Initial guesses
                # ---------------------------------

                p0 = [
                        np.median(data),      # MPV
                        np.std(data)/3,       # sigma
                        np.max(counts),       # Landau amplitude
                        np.max(counts),       # Exp amplitude
                        np.mean(data)         # tau
                ]

                # ---------------------------------
                # Fit
                # ---------------------------------

                try:

                        pars, cov = curve_fit(
                        landau_plus_exp,
                        centers,
                        counts,
                        p0=p0,
                        maxfev=20000
                        )

                        xfit = np.linspace(
                        np.min(data),
                        np.max(data),
                        1000
                        )

                        yfit = landau_plus_exp(
                        xfit,
                        *pars
                        )

                        # Reduced χ²

                        model = landau_plus_exp(
                        centers,
                        *pars
                        )

                        chi2 = np.sum(
                        (counts-model)**2 /
                        (model + 1e-10)
                        )

                        ndof = len(counts) - len(pars)

                        chi2_red = chi2/ndof

                except Exception as e:

                        pars = None
                        chi2_red = np.nan

                # ---------------------------------
                # Plot histogram
                # ---------------------------------

                ax.hist(
                        data,
                        bins=bins,
                        density=True,
                        histtype='step',
                        label=f"bins={bins}"
                )

                # ---------------------------------
                # Plot fit
                # ---------------------------------

                if pars is not None:

                        ax.plot(
                        xfit,
                        yfit,
                        'r',
                        linewidth=2,
                        label="Landau + Exp"
                        )

                        mpv, sigma, A_landau, A_exp, tau = pars

                        txt = (
                        f"MPV={mpv:.3f}\n"
                        f"σ={sigma:.3f}\n"
                        f"τ={tau:.3f}\n"
                        f"χ²/ndof={chi2_red:.2f}"
                        )

                        ax.text(
                        0.97,
                        0.95,
                        txt,
                        transform=ax.transAxes,
                        ha="right",
                        va="top",
                        bbox=dict(facecolor="white", alpha=0.8)
                        )

                # ---------------------------------
                # Labels
                # ---------------------------------

                ax.set_title(
                        f"{ch_label} charge (N={len(data)}, rate={rate}Hz)"
                )

                ax.set_xlabel(
                        f"Charge {ch_label} (V·ns)"
                )

                ax.set_ylabel(
                        "PDF"
                )

                ax.grid(True)
                ax.legend()

        # -----------------------------
        # Fit each channel
        # -----------------------------
        fit_and_plot(ax0, charge0, "CH0", rate)
        fit_and_plot(ax1, charge1, "CH1", rate)
        fit_and_plot(ax2, charge2, "CH2", rate)

        plt.tight_layout()
        plt.show()
        plt.savefig(f"{route_figure}\\Charge_Histograms_with_LandauFit.png")
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
