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
from Functions import get_raw_data

def main():

    # And declare the threshold we're working with, it's in the name of the file
    th = '0.010'
    run = 2

    # we declare the time resolution of the oscilloscope in nano seconds
    dt = 0.3125

    # Declare route of the file
    filename = fr".\Data\Raw_data\1Bar_2Chs\57V_TriggerCh0_VaryTrigger\Run_{th}V_Run{run}_Data_3_22_2026_Ascii.dat"

    # We get the data frame of the data set we're analyzing
    df = get_raw_data(filename)
    
    # Create figure before cycle starts
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))

    # Just convert it to float for posterior numerical use.
    th = float(th)
    th_f = th + 0.005
    
    # We create an array of gate lengths
    DELTA_T = np.linspace(0,20,100) # About in 20 we observe a saturation next time I can put the limit there maybe I would put it in like 40 or 30.
    
    # We get the total time it took to gather this data in seconds
    TOTAL_TIME = df['unix_time'].iloc[-1] - df['unix_time'].iloc[0]
    
    while th <= th_f:
        # Create array of counts right and left
        COINCIDENCE = np.array([0 for _ in DELTA_T])

        for i,delta_t in enumerate(DELTA_T):
            # we declare two counts because I want to know the rate of coincidences to the left or to the right
            counts = 0
            for row in df['channels']:
                ch0 = row[0]
                ch1 = row[1]

                # First we look at the max in the samples of both ch0 and ch1 to say if we have coincidence
                if np.max(ch1) >= th and np.max(ch0) >= th:
                    time_difference = (np.argmax(ch0) - np.argmax(ch1))*dt
                    # Then we check if the time difference between peaks is between the window we want
                    if abs(time_difference) <= delta_t:
                        counts += 1
        
            COINCIDENCE[i] = counts/TOTAL_TIME
        ax.plot(DELTA_T, COINCIDENCE, label=f'Th={round(th,4)}', marker = 'o', linestyle='-', alpha=0.7)
        th += 0.001
        
    ax.set_title(f'Coincidences vs Delta_t')
    ax.set_xlabel('Delta_t (ns)')
    ax.set_ylabel('Rate (Hz)')
    ax.legend()
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig(fr'.\All_plots_with_raw_data\Plots\1Bar_2Chs\57V_TriggerCh0_VaryTrigger\Run{run}_Th{round(th-0.005,4)}.png')
    #plt.show()

    return 0

if __name__ == "__main__":
    print('\nStart execution.\n')
    main()
    print("\nFinish execution\n")
