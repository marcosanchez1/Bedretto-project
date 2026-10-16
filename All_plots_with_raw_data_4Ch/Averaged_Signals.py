'''
In this script I will plot the average waveforms of the signals as if they were captured on the same readout window,
and I will plot several depending on the distance of arrival from the left SiPM.

'''

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
import os
import sys

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from Functions import get_raw_datFile, get_raw_rootFile, perform_fit_on_dataframe, f, get_t_with_samples

dt = 0.3125 # multiply sample_i by this to get it in ns
max_number_samples = 1024
v = 15.95 # speed of light inside scintillator in cm/ns.
L = 170

def main():
    trigger = 0.004 # with 15mV it's mostly muons
    voltage = 57
    run = 0
    day = 20
    month = 8

    # Load raw data
    df = get_raw_datFile(fr".\Data\Raw_data\10Bar_3Ch\FollowingCorrectProcedure\coincidenceCh0Ch1Ch2_Ps{voltage}V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat")
    RATE = len(df) / (df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])

    # Extract raw samples
    ch0 = [np.array(ev[0]) for ev in df["channels"]]
    ch1 = [np.array(ev[1]) for ev in df["channels"]]
    baseline_ch1 = [np.mean(ev[1][:50]) for ev in df["channels"]]

    # Say we divide the time window in 20, depending on where the 10% of the signal is, is
    # where I'll place the waveforms.
    n = 50
    interval = (max_number_samples - 640) / n  # 640 is the number of samples that correspond to 200ns, which is the time when the signals start to arrive.
    # For now let's just try and plot the waveforms of channel 1.
    waveforms_ch0 = [{'number_wf':0, 'wf': [], 'distance':[]} for i in range(n)]
    waveforms_ch1 = [{'number_wf':0, 'wf': [], 'distance':[]} for i in range(n)]

    # The idea is good but I have to consider that almost all signals arrive at times between 200ns and 320ns,
    # so it would be better to divide from the range from 200ns to 320ns
    for i in range(len(ch1)):
        arrival_time_ch0 = get_t_with_samples(ch0[i], 0.1)
        index_arrival_ch0 = (arrival_time_ch0 - 200) / dt

        arrival_time_ch1 = get_t_with_samples(ch1[i], 0.1)
        index_arrival_ch1 = (arrival_time_ch1 - 200) / dt

        distance = (v*(arrival_time_ch1-arrival_time_ch0) + L)/2

        # Determine where to place the waveform based on the index of the arrival
        index_ch0 = int(index_arrival_ch0 / interval)
        index_ch1 = int(index_arrival_ch1 / interval)

        waveforms_ch0[index_ch0]['wf'].append(ch0[i])
        waveforms_ch0[index_ch0]['number_wf'] += 1
        waveforms_ch0[index_ch0]['distance'].append(distance)

        waveforms_ch1[index_ch1]['wf'].append(ch1[i])
        waveforms_ch1[index_ch1]['number_wf'] += 1
        waveforms_ch1[index_ch1]['distance'].append(distance)

    for i in range(len(waveforms_ch1)):
        if waveforms_ch1[i]['number_wf'] > 0:

            avg_wf_ch0 = np.mean(waveforms_ch0[i]['wf'], axis=0)
            avg_wf_ch1 = np.mean(waveforms_ch1[i]['wf'], axis=0)
            plt.plot(np.arange(max_number_samples) * dt, avg_wf_ch1, label=f"{waveforms_ch1[i]['distance'][0]:.2f} cm")
    plt.xlabel('Time (ns)')
    plt.ylabel('Signal (V)')
    plt.legend()
    plt.grid(True)
    plt.title(f"Average Waveforms for CH1 at Trigger Level {trigger}V, Rate: {RATE:.2f} Hz")
    plt.savefig(fr".\All_plots_with_raw_data_4Ch\Plots\Average_Waveforms_CH1.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":
    main()