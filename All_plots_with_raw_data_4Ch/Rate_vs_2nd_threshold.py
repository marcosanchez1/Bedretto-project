'''
In this script I'll do one plot: the rate of events vs sofwtare trheshold that I'll apply to this data set but
taking the data that are above the threshold.

The data structure of the data frames should be something like this:
channels,unix_time
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_0
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_1
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_2
...

'''

import numpy as np
import matplotlib.pyplot as plt
from Functions import get_raw_data

dt = 0.3125
def main(df, route_figure):

    thresholds = np.linspace(0.065, 1, 100) # Thresholds to test
    rates = []

    for th in thresholds:
        # Count events above the threshold
        count = 0
        for row in df['channels']:
            ch0 = np.array(row[0])
            ch1 = np.array(row[1])
            if np.max(ch0) > th and np.max(ch1) > th:
                count += 1
        rate = count / (df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
        rates.append(rate)

    plt.figure(figsize=(10, 6))
    plt.plot(thresholds, rates, marker='o')
    plt.title("Rate vs Threshold(0.065 <= threshold < max(ch0 and ch1))")
    plt.xlabel("Threshold (ADC)")
    plt.ylabel("Rate (Hz)")
    plt.grid(True)
    plt.show()

    return 0

if __name__ == "__main__":

    print("\nStarting execution.\n")

    voltage = '0.065'
    run = '22'
    day = '11'
    month = '5'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_raw_data\Plots\1Bar_2Chs\57Vcoincidence\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\1Bar_2Chs\57Vcoincidence\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df = get_raw_data(route_data)

    main(df, route_figure)
    
    print("\nEnd of execution.\n")