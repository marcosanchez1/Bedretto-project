import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
import ast

def main():
    Voltage = 60
    th_oscilloscope = 0.05 #Run1 in my notes usually is the lowest I took

    # Load the data
    df = pd.read_csv(r".\Data\1Bar_2Chs_processed_data\Run_{}V_Run0_Data_3_10_2026_Ascii.csv".format(Voltage))
    df["channels"] = df["channels"].apply(ast.literal_eval) # Convert string to dict, because our info is stored as string.

    df_filtered = pd.read_csv(r".\Data\1Bar_2Chs_filtered_data\Run_{}V_Run0_Data_3_10_2026_Ascii.csv".format(Voltage))
    df_filtered["channels"] = df_filtered["channels"].apply(ast.literal_eval) # Convert
    
    # Check the conversion
    #print(df_filtered.head())
    #print(df.head())

    # Sampling period (seconds)
    #dt = 312.5e-12
    dt = 1

    # Prepare figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    line1, = ax1.plot([], [], lw=2)
    line1_filtered, = ax1.plot([], [], lw=2, color='orange')

    line2, = ax2.plot([], [], lw=2)
    line2_filtered, = ax2.plot([], [], lw=2, color='orange')
    
    ax1.set_xlabel("Time (ns)")
    ax1.set_ylabel("Voltage (V)")
    
    ax2.set_xlabel("Time (ns)")
    ax2.set_ylabel("Voltage (V)")

    # Precompute time axis we're basically gonna look for the list os samples that has the most data
    t = []
    for row in df["channels"]:
        for ch in row.values():
            if len(ch['samples']) > len(t):
                t = np.arange(len(ch['samples'])) * dt
    # Set axis limits once
    ax1.set_xlim(t[0], t[-1])
    ax2.set_xlim(t[0], t[-1])

    #Now to set the limits of y I'll look for the max value of voltage in all the samples of all the channels and all the events,
    # and the same for the min value, so I can set the limits of y to be the same for all the events and all the channels,
    # so we can compare them better.
    low_limit = 0
    high_limit = 0
    for row in df["channels"]:
        for ch in row.values():
            low_limit = min(low_limit, min(ch['samples']))
            high_limit = max(high_limit, max(ch['samples']))

    ax1.set_ylim(low_limit, high_limit)
    ax2.set_ylim(low_limit, high_limit)

    ax1.grid(True)
    ax2.grid(True)

    #Befor going into the animation I'll get the mean of baselines so it'll be like a mean of means of the baseline
    baseline1 = []
    baseline2 = []
    for i in range(len(df_filtered["channels"])):
        baseline1.append(df_filtered['channels'].iloc[i][0]['baseline'])
        baseline2.append(df_filtered['channels'].iloc[i][1]['baseline'])
    baseline1 = np.mean(baseline1)
    baseline2 = np.mean(baseline2)

    ax1.axhline(y=baseline1, color="red", label = f'Baseline={round(baseline1,3)}')
    ax2.axhline(y=baseline2, color="red", label = f'Baseline={round(baseline2,3)}')

    ax1.axhline(y=th_oscilloscope, color="green", label = f'Threshold Oscilloscope={th_oscilloscope}')
    ax2.axhline(y=th_oscilloscope, color="green", label = f'Threshold Oscilloscope={th_oscilloscope}')

    # Animation update function
    def update(i):

        #Get data for the current event
        samples1 = df["channels"].iloc[i][0]['samples']
        samples1_filtered = df_filtered["channels"].iloc[i][0]['samples']
        t1 = np.arange(len(samples1)) * dt
        start_index = np.argmax(samples1) - np.argmax(samples1_filtered)
        t1_filtered = np.arange(start_index,len(samples1_filtered)+start_index) * dt

        samples2 = df["channels"].iloc[i][1]['samples']
        samples2_filtered = df_filtered["channels"].iloc[i][1]['samples']
        t2 = np.arange(len(samples2)) * dt
        start_index = np.argmax(samples2) - np.argmax(samples2_filtered)
        t2_filtered = np.arange(start_index,len(samples2_filtered)+start_index) * dt
        
        # Update line data
        line1.set_data(t1, samples1)
        line1.set_label("Original")
        line1_filtered.set_data(t1_filtered, samples1_filtered)
        line1_filtered.set_label("Filtered")

        line2.set_data(t2, samples2)
        line2.set_label("Original")
        line2_filtered.set_data(t2_filtered,samples2_filtered)
        line2_filtered.set_label("Filtered")
        
        ax1.set_title("Waveform Animation - Channel 1 - Event {}".format(i))
        ax1.legend(loc="upper right")
        ax2.set_title("Waveform Animation - Channel 2 - Event {}".format(i))
        ax2.legend(loc="upper right")

        return line1, line2

    # Create animation
    ani = animation.FuncAnimation(fig, update, frames=len(df), interval=50, blit=False)

    plt.show()


if __name__ == "__main__":
    main()