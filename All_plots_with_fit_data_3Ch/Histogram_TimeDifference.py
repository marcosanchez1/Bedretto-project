"""
I define time of arrival at 10% of the amplitude,
and I want to see the distribution of these.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from Functions import (
    get_raw_datFile,
    perform_fit_on_dataframe,
    get_t_with_fit,
    f
)

dt = 0.3125

from scipy.integrate import quad
def perform_integral_with_fit(A):
    result, error = quad(lambda x: f(np.array([x]), A)[0], 0, 320)
    return result

def plot_distribution(ax, data, label, rate):

    N = 0.5
    bins = int(round(N * np.sqrt(len(data)), 0))

    ax.hist(
        data,
        bins=bins,
        alpha=0.7,
        range=[min(data), max(data)],
        histtype='step',
        label=f"bins={bins}"
    )

    ax.set_title(
        f"{label} (N={len(data)}, rate={rate}Hz)\n"
        f"μ={np.mean(data):.3f} ns, σ={np.std(data):.3f} ns"
    )

    ax.set_xlabel(label + " (ns)")
    ax.set_ylabel("Counts")
    ax.grid(True)
    ax.legend()


def main(df, df_fit, route_figure):

    time_diff_01 = []
    time_diff_02 = []
    time_diff_12 = []

    for row in df_fit['channels']:

        t0 = get_t_with_fit(row[0], 0.1)
        t1 = get_t_with_fit(row[1], 0.1)
        t2 = get_t_with_fit(row[2], 0.1)

        charge0 = perform_integral_with_fit(row[0])
        charge1 = perform_integral_with_fit(row[1])
        charge2 = perform_integral_with_fit(row[2])

        # reject impossible events
        if charge2 < 0.5:

            time_diff_01.append(t1 - t0)
            time_diff_02.append(t0 - t2)
            time_diff_12.append(t2 - t1)
    rate = round(len(time_diff_01) / (df['unix_time'].iloc[-1] - df['unix_time'].iloc[0]), 3)

    # --------------------------
    # Figure layout
    # --------------------------

    fig = plt.figure(figsize=(10, 10))

    ax0 = fig.add_subplot(2, 2, 1)
    ax1 = fig.add_subplot(2, 2, 2)

    # centered CH2 plot
    ax2 = fig.add_subplot(2, 1, 2)

    # --------------------------
    # Plot
    # --------------------------

    plot_distribution(ax0, time_diff_01, "t1 - t0", rate)
    plot_distribution(ax1, time_diff_02, "t0 - t2", rate)
    plot_distribution(ax2, time_diff_12, "t2 - t1", rate)

    plt.tight_layout()
    plt.savefig(
        f"{route_figure}\\TimeDifference_Histograms.png"
    )
    plt.show()
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