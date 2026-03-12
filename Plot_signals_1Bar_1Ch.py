'''
Now the filtered data looks like

channel
{0:{'baseline':baseline_event1_channel0,'samples':[]},1:{'baseline_event1_channel1':[],'samples':[]}},...}
{0:{'baseline':baseline_event2_channel0,'samples':[]},1:{'baseline_event2_channel1':[],'samples':[]}},...}
{0:{'baseline':baseline_event3_channel0,'samples':[]},1:{'baseline_event3_channel1':[],'samples':[]}},...}
...

While processed data looks like
event_id,unix_time,channel,event_id_check,baseline,amplitude,charge_pC,samples
1,1772462970.525,0,1,0.0,0.0,0.0,"[0.00104, 0.002771, 0.000162, -0.002077, -0.000957, -2...]"

So just be carfeul now with how we work with the filtered data.
'''

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
import ast

def main():
    # Load the data
    df = pd.read_csv(r".\Data\1Bar_1Ch_processed_data\Run_53.91V_Run1_Data_3_2_2026_Ascii.csv")

    # Convert "samples" from string to list
    df["samples"] = df["samples"].apply(ast.literal_eval)

    # We create this new filtered df that we'll compare with the original.
    # it contains only the samples so the rest of the data is lost, but we
    # care for the samples.
    df_filtered = pd.read_csv(r".\Data\1Bar_1Ch_filtered_data\Run_53.91V_Run1_Data_3_2_2026_Ascii.csv")
    df_filtered["channel"] = df_filtered["channel"].apply(ast.literal_eval)
    
    # Sampling period (seconds)
    #dt = 312.5e-12
    dt = 1 #sampling in ps

    # Prepare figure
    fig, ax = plt.subplots()
    line_original, = ax.plot([], [], lw=2, color='blue', alpha=0.5, label='Original')
    line_filtered, = ax.plot([], [], lw=2, color='green', alpha=0.5, label='Filtered')

    # Precompute time axis (same for all events)
    t = np.arange(len(df.loc[0, "samples"])) * dt

    # Set axis limits once, it's only necessary to adjust it with respecto to the 
    # originaal, the filtered will be inside the original.
    ax.set_xlim(t[0], t[-1])
    ax.set_ylim(df["samples"].apply(min).min(), df["samples"].apply(max).max())
    ax.grid(True)

    #Before animating we get the mean of all baselines.
    baseline = []
    for i in range(len(df_filtered["channel"])):
        baseline.append(df_filtered['channel'].iloc[i][0]['baseline'])
    baseline = np.mean(baseline)

    ax.axhline(y=baseline, color="red", label = f'Baseline={baseline}')
    ax.set_xlabel("Time (ps)")
    ax.set_ylabel("Voltage (V)")
    ax.legend()

    # Animation update function
    def update(i):
        samples = df['samples'].iloc[i]
        samples_filtered = df_filtered['channel'].iloc[i][0]['samples']
        
        #To shift the filtered signal to match the original, we need to move the
        # time axis of the filtered signal to the right by the number of samples
        # we cut from the left.
        t_filtered = np.arange(len(df_filtered['channel'].iloc[i][0]['samples']))
        start_index = np.argmax(samples) - np.argmax(samples_filtered)
        t_filtered_shifted = (t_filtered + (start_index)) * dt

        line_original.set_data(t[:len(samples)], samples)
        line_filtered.set_data(t_filtered_shifted[:len(samples_filtered)], samples_filtered)

        #add baseline


        ax.set_title(f"Waveform - Event {i}")
        return line_original, line_filtered

    # Create animation
    ani = animation.FuncAnimation(fig, update,
                                  interval=50,
                                  frames=range(0, len(df), 1000),
                                  blit=False)

    plt.show()


if __name__ == "__main__":
    main()