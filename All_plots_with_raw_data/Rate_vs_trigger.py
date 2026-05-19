'''
In this script I do a plot a of the rate of events per data set vs the trigger at which the data was taken.

The data structure of the data frames should be something like this:
channels,unix_time
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_0
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_1
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_2
...

'''

import os
import numpy as np
import matplotlib.pyplot as plt
from Functions import get_raw_data, rid_of_muon_signal

dt = 0.3125
def main(route_figure):
    route_files = r".\Data\Raw_data\1Bar_2Chs\57Vcoincidence"
    list_files = os.listdir(route_files)
    
    RATES = []
    TRIGGERS = []

    for file in list_files:
        if file.endswith(".dat"):
            input_path = os.path.join(route_files, file)
            df = get_raw_data(input_path)

            rate = len(df) / (df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
            trigger = float(file.split("_")[1].replace("V",""))
            
            RATES.append(rate)
            TRIGGERS.append(trigger)


    
    '''
    plt.figure(figsize=(10, 6))
    plt.plot(TRIGGERS, RATES, color='blue', alpha=0.7, marker='o', label='Data points')
    plt.title("Rate vs Trigger Voltage")
    plt.xlabel("Trigger Threshold (ADC)")
    plt.ylabel("Rate (Hz)")
    plt.grid(True)
    plt.legend()
    plt.show()
    plt.savefig(os.path.join(route_figure, "Rate_vs_Trigger.png"))
    '''

    return RATES, TRIGGERS

if __name__ == "__main__":
    print("\nStarting execution.\n")

    route_figure = r".\All_plots_with_raw_data\Plots\1Bar_2Chs\57Vcoincidence"
    main(route_figure)
    
    print("\nEnd of execution.\n")