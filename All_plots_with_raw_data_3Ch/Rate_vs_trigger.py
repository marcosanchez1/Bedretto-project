'''
In this script I'll just take the data of the special run and plot it, by special run I mean that I did a run
just to measure the rate without taking wf data, this should be more accurate to measure the rate.

The data structure of the data frames should be something like this:
channels,unix_time
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_0
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_1
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_2
...

'''

import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from Functions import get_raw_datFile, get_raw_rootFile, perform_fit_on_dataframe, f

def read_rate_vs_threshold(filename):
    thresholds = []
    rates_ch0 = []
    rates_ch1 = []
    rates_ch2 = []

    reading_x = False
    reading_y0 = False
    reading_y1 = False
    reading_y2 = False

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()

            # Detect section starts
            if "X AXIS" in line:
                reading_x = True
                reading_y0 = False
                reading_y1 = False
                reading_y2 = False
                continue

            if "Y AXIS" in line and "CHANNEL : 0" in line:
                reading_x = False
                reading_y0 = True
                reading_y1 = False
                reading_y2 = False
                continue

            if "Y AXIS" in line and "CHANNEL : 1" in line:
                reading_x = False
                reading_y0 = False
                reading_y1 = True
                reading_y2 = False
                continue

            if "Y AXIS" in line and "CHANNEL : 2" in line:
                reading_x = False
                reading_y0 = False
                reading_y1 = False
                reading_y2 = True
                continue

            # Stop reading when a new header appears
            if line.startswith("=="):
                reading_x = False
                reading_y0 = False
                reading_y1 = False
                reading_y2 = False
                continue

            # Read numbers
            if reading_x:
                thresholds.extend([float(x) for x in line.split()])

            if reading_y0:
                rates_ch0.extend([float(x) for x in line.split()])

            if reading_y1:
                rates_ch1.extend([float(x) for x in line.split()])

            if reading_y2:
                rates_ch2.extend([float(x) for x in line.split()])

    return np.array(thresholds), np.array(rates_ch0), np.array(rates_ch1), np.array(rates_ch2)

def get_rate_coincidence(filename, thresholds):
    df = get_raw_datFile(filename)
    RATES = []

    for threshold in thresholds:
        # Count events where any of the channels exceeds the threhold, is a coincidence so it's not necessay to check all channels
        count = df[(df['channels'].apply(lambda x: max(x[0]) > threshold))].shape[0]
        total_time = df['unix_time'].iloc[-1] - df['unix_time'].iloc[0]
        RATES.append(count/total_time)

    return RATES

def main():
    filename = fr".\Data\Raw_data\10Bar_3Ch\rate_vs_threshold\Run0_100Nb_1s_0.002_to_0.4.dat"
    filename_coin = r".\Data\Raw_data\10Bar_3Ch\Run_0.002V_Run0_Data_8_13_2026_Ascii.dat"

    # obtain data
    thresholds, rates_ch0, rates_ch1, rates_ch2 = read_rate_vs_threshold(filename)
    rate_coin = get_rate_coincidence(filename_coin, thresholds)
    
    plt.figure(figsize=(10,6))
    i = 1
    plt.plot(thresholds[i:], rates_ch0[i:], label='CH0 Rate', marker='o', linestyle='-', alpha=0.7)
    plt.plot(thresholds[i:], rates_ch1[i:], label='CH1 Rate', marker='s', linestyle='-', alpha=0.7)
    plt.plot(thresholds[i:], rates_ch2[i:], label='CH2 Rate', marker='^', linestyle='-', alpha=0.7)
    plt.plot(thresholds, rate_coin, label='Coincidence Rate', marker='x', linestyle='--', color='black', alpha=0.7)

    
    plt.xlabel("Threshold [V]")
    plt.ylabel("Rate [Hz]")
    plt.title("Rate vs Threshold")
    plt.grid(True, which="both", ls="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig(r".\All_plots_with_raw_data_3Ch\Plots\Rate_vs_Threshold.png", dpi=300)
    plt.show()
    plt.savefig(r".\All_plots_with_raw_data_3Ch\Plots\Rate_vs_Threshold.png", dpi=300)
    plt.close()

    return 0

if __name__ == "__main__":
    print('\nStarting execution.\n')
    main()
