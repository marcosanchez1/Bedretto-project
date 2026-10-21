import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from Functions import (
    get_raw_datFile,
    perform_fit_on_dataframe,
    get_t_with_fit,
    get_t_with_samples,
    f
)

dt = 0.3125


def compute_metrics(samples, fit):

    # Residuals
    residuals = samples - fit

    # R²
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((samples - np.mean(samples))**2)

    if ss_tot > 0:
        r2 = 1 - ss_res/ss_tot
    else:
        r2 = np.nan

    # RMSE
    rmse = np.sqrt(np.mean(residuals**2))

    amplitude = np.max(samples) - np.min(samples)

    if amplitude > 0:
        nrmse = rmse / amplitude
    else:
        nrmse = np.nan

    return r2, rmse, nrmse


def plot_distribution(ax, data, title, xlabel):

    bins = int(np.sqrt(len(data)))

    ax.hist(
        data,
        bins=bins,
        density=True,
        histtype='step'
    )

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Frequency")
    ax.grid(True)


def main(df, df_fit, route_figure):

    # ------------------------------------
    # Metric containers
    # ------------------------------------

    r2_ch0 = []
    r2_ch1 = []
    r2_ch2 = []

    nrmse_ch0 = []
    nrmse_ch1 = []
    nrmse_ch2 = []

    dt_error_ch0 = []
    dt_error_ch1 = []
    dt_error_ch2 = []

    # ------------------------------------
    # Loop over events
    # ------------------------------------

    for i, row in df.iterrows():

        channels = row["channels"]

        for ch in [0, 1, 2]:

            samples = np.array(channels[ch])

            peak_idx = np.argmax(np.abs(samples))

            # only evaluate until peak
            samples_cut = samples[:peak_idx+1]

            t = np.arange(peak_idx+1)*dt

            fit_pars = df_fit["channels"].iloc[i][ch]

            fit_values = f(t, fit_pars)

            # ------------------------
            # R² and NRMSE
            # ------------------------

            r2, rmse, nrmse = compute_metrics(
                samples_cut,
                fit_values
            )

            # ------------------------
            # Timing difference
            # ------------------------

            try:

                t_fit = get_t_with_fit(
                    fit_pars,
                    0.1
                )

                t_samples = get_t_with_samples(
                    samples,
                    0.1
                )

                delta_t = t_fit - t_samples

            except:
                delta_t = np.nan

            # ------------------------
            # Store
            # ------------------------

            if ch == 0:
                r2_ch0.append(r2)
                nrmse_ch0.append(nrmse)
                dt_error_ch0.append(delta_t)

            elif ch == 1:
                r2_ch1.append(r2)
                nrmse_ch1.append(nrmse)
                dt_error_ch1.append(delta_t)

            elif ch == 2:
                r2_ch2.append(r2)
                nrmse_ch2.append(nrmse)
                dt_error_ch2.append(delta_t)

    # ------------------------------------
    # Figure 1 : R²
    # ------------------------------------

    fig = plt.figure(figsize=(10, 10))

    ax0 = fig.add_subplot(2,2,1)
    ax1 = fig.add_subplot(2,2,2)
    ax2 = fig.add_subplot(2,1,2)

    plot_distribution(
        ax0,
        r2_ch0,
        f"CH0 R² (mean={np.nanmean(r2_ch0):.4f})",
        "R²"
    )

    plot_distribution(
        ax1,
        r2_ch1,
        f"CH1 R² (mean={np.nanmean(r2_ch1):.4f})",
        "R²"
    )

    plot_distribution(
        ax2,
        r2_ch2,
        f"CH2 R² (mean={np.nanmean(r2_ch2):.4f})",
        "R²"
    )

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\R2_Distributions.png")
    plt.show()

    # ------------------------------------
    # Figure 2 : NRMSE
    # ------------------------------------

    fig = plt.figure(figsize=(10, 10))

    ax0 = fig.add_subplot(2,2,1)
    ax1 = fig.add_subplot(2,2,2)
    ax2 = fig.add_subplot(2,1,2)

    plot_distribution(
        ax0,
        nrmse_ch0,
        f"CH0 NRMSE (mean={np.nanmean(nrmse_ch0):.4f})",
        "NRMSE"
    )

    plot_distribution(
        ax1,
        nrmse_ch1,
        f"CH1 NRMSE (mean={np.nanmean(nrmse_ch1):.4f})",
        "NRMSE"
    )

    plot_distribution(
        ax2,
        nrmse_ch2,
        f"CH2 NRMSE (mean={np.nanmean(nrmse_ch2):.4f})",
        "NRMSE"
    )

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\NRMSE_Distributions.png")
    plt.show()

    # ------------------------------------
    # Figure 3 : Timing error
    # ------------------------------------

    fig = plt.figure(figsize=(10, 10))

    ax0 = fig.add_subplot(2,2,1)
    ax1 = fig.add_subplot(2,2,2)
    ax2 = fig.add_subplot(2,1,2)

    plot_distribution(
        ax0,
        np.array(dt_error_ch0)[np.isfinite(dt_error_ch0)],
        f"CH0 Δt (σ={np.nanstd(dt_error_ch0):.3f} ns)",
        "t_fit - t_samples (ns)"
    )

    plot_distribution(
        ax1,
        np.array(dt_error_ch1)[np.isfinite(dt_error_ch1)],
        f"CH1 Δt (σ={np.nanstd(dt_error_ch1):.3f} ns)",
        "t_fit - t_samples (ns)"
    )

    plot_distribution(
        ax2,
        np.array(dt_error_ch2)[np.isfinite(dt_error_ch2)],
        f"CH2 Δt (σ={np.nanstd(dt_error_ch2):.3f} ns)",
        "t_fit - t_samples (ns)"
    )

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Time_Error_Distributions.png")
    plt.show()

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

    route_figure = r".\All_plots_with_fit_data_3Ch\Plots"

    route_data = (
        fr".\Data\Raw_data\2Bar_3Ch\OpticalGreaseTests"
        fr"\BeforeOptical_CoinTriggerCh0Ch1Ch2_{voltage}V"
        fr"\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    )

    df = get_raw_datFile(route_data)
    df_fit = perform_fit_on_dataframe(df)

    main(df, df_fit, route_figure)

    print("\nEnd of execution.\n")