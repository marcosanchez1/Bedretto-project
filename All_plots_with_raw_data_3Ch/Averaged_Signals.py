'''
Plot average waveforms grouped by time difference (tL - tR).
Grouping is done into fixed bins from -12 ns to +12 ns.
'''

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from Functions import get_raw_datFile, perform_fit_on_dataframe, get_t_with_fit, get_t_with_samples

dt = 0.3125  # ns per sample
max_number_samples = 1024

def main():
    voltage = 57
    trigger = '0.004'
    day = 20
    month = 8
    run = 0

    # Load raw data
    df = get_raw_datFile(
        fr".\Data\Raw_data\10Bar_3Ch\FollowingCorrectProcedure\coincidenceCh0Ch1Ch2_Ps{voltage}V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    )
    df_fit = perform_fit_on_dataframe(df)

    trigger = float(trigger)

    RATE = len(df) / (df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])

    # Extract raw samples
    ch0 = [np.array(ev[0]) for ev in df["channels"]]
    ch1 = [np.array(ev[1]) for ev in df["channels"]]
    ch2 = [np.array(ev[2]) for ev in df["channels"]]

    # --- Time-difference binning setup ---
    TD_MIN = -11     # ns
    TD_MAX =  11     # ns
    N_BINS = 7
    td_bins = np.linspace(TD_MIN, TD_MAX, N_BINS + 1)

    # Prepare bins for each channel
    bins_ch0 = [[] for _ in range(N_BINS)]
    bins_ch1 = [[] for _ in range(N_BINS)]
    bins_ch2 = [[] for _ in range(N_BINS)]

    # --- Fill bins based on time difference ---
    for i in range(len(ch0)):
        td = get_t_with_fit(df_fit['channels'].iloc[i][1], 0.1) - get_t_with_fit(df_fit['channels'].iloc[i][0], 0.1)

        # Find which bin the event belongs to
        bin_index = np.digitize(td, td_bins) - 1
        if bin_index < 0 or bin_index >= N_BINS:
            continue  # skip out-of-range events

        bins_ch0[bin_index].append(ch0[i])
        bins_ch1[bin_index].append(ch1[i])
        bins_ch2[bin_index].append(ch2[i])

    # --- Build plotting lists (bins already sorted by td) ---
    def build_plot_list(bins):
        plot_list = []
        for b in range(N_BINS):
            if len(bins[b]) > 0:
                avg_wf = np.mean(bins[b], axis=0)
                td_center = 0.5 * (td_bins[b] + td_bins[b+1])
                plot_list.append((td_center, avg_wf))
        return plot_list

    plot_list_ch0 = build_plot_list(bins_ch0)
    plot_list_ch1 = build_plot_list(bins_ch1)
    plot_list_ch2 = build_plot_list(bins_ch2)

    # --- Plotting ---
    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    ax0, ax1, ax2, ax3 = ax.flatten()

    time_axis = np.arange(max_number_samples) * dt

    # CH0
    for td, avg_wf in plot_list_ch0:
        ax0.plot(time_axis, avg_wf, label=f"{td:.2f} ns")

    ax0.set_xlabel('Time (ns)')
    ax0.set_ylabel('Signal (V)')
    ax0.grid(True)
    ax0.legend()
    ax0.set_title(f"Average Waveforms for CH0 at Trigger Level {trigger*1000:.1f}mV, Rate: {RATE:.2f} Hz")

    # CH1
    for td, avg_wf in plot_list_ch1:
        ax1.plot(time_axis, avg_wf, label=f"{td:.2f} ns")

    ax1.set_xlabel('Time (ns)')
    ax1.set_ylabel('Signal (V)')
    ax1.grid(True)
    ax1.legend()
    ax1.set_title(f"Average Waveforms for CH1 at Trigger Level {trigger*1000:.1f}mV, Rate: {RATE:.2f} Hz")

    # CH2
    for td, avg_wf in plot_list_ch2:
        ax2.plot(time_axis, avg_wf, label=f"{td:.2f} ns")

    ax2.set_xlabel('Time (ns)')
    ax2.set_ylabel('Signal (V)')
    ax2.grid(True)
    ax2.legend()
    ax2.set_title(f"Average Waveforms for CH2 at Trigger Level {trigger*1000:.1f}mV, Rate: {RATE:.2f} Hz")

    plt.savefig(r".\All_plots_with_raw_data_3Ch\Plots\Average_Waveforms.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":
    main()
