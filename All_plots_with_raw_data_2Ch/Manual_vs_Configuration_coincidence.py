'''
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
from Rate_vs_trigger import main as configuration_coincidence
import os

dt = 0.3125e-9
def get_manual_coincidences():
    route_files = r".\Data\Raw_data\1Bar_2Chs\57V_TriggerCh0_VaryTrigger"
    list_files = os.listdir(route_files)
    
    RATES_L = []
    RATES_R = []
    TRIGGERS = []

    for file in list_files:
        if file.endswith(".dat"):
            input_path = os.path.join(route_files, file)
            df = get_raw_data(input_path)
            total_time = df['unix_time'].iloc[-1] - df['unix_time'].iloc[0]
            trigger = float(file.split("_")[1].replace("V",""))

            counts_l = 0
            counts_r = 0
            for row in df['channels']:
                ch0 = row[0]
                ch1 = row[1]

                # First we look at the max in the samples of both ch0 and ch1 to say if we have coincidence
                if np.max(ch1) >= trigger and np.max(ch0) >= trigger:
                    time_difference = (np.argmax(ch0) - np.argmax(ch1))*dt
                    # Then we check if the time difference between peaks is between the window we want
                    if abs(time_difference) <= 15e-9:
                        if time_difference > 0:
                            counts_l += 1
                        elif time_difference < 0:
                            counts_r += 1
            RATES_L.append(counts_l/total_time)
            RATES_R.append(counts_r/total_time)
            TRIGGERS.append(trigger)

    return RATES_L, RATES_R, TRIGGERS

def main():

    manual_rate_L, manual_rate_R, manual_thresholds = get_manual_coincidences()
    configuration_rate, configuration_thresholds = configuration_coincidence(None)
    
    plt.plot(manual_thresholds, manual_rate_R, label=f'Manual right coincidence', marker = 'o', linestyle='-', alpha=0.7)
    plt.plot(manual_thresholds, manual_rate_L, label=f'Manual left coincidence', marker = 'o', linestyle='-', alpha=0.7)
    plt.plot(manual_thresholds, np.array(manual_rate_L) + np.array(manual_rate_R), label=f'Sum left+right', marker = 'o', linestyle='-', alpha=0.7)
    plt.plot(configuration_thresholds, configuration_rate, label=f'Configuration coincidence', marker = 'o', linestyle='-', alpha=0.7)
    
    plt.xlabel('Thresholds')
    plt.ylabel('Rates(Hz)')
    plt.title('Coincidences manual and configuration vs thresholds')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    return 0

if __name__ == "__main__":
    print('\nStart execution.\n')
    main()
    print("\nFinish execution\n")
