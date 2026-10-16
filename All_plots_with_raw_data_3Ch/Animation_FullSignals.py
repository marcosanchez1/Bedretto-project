'''
Data structure:

channel,unix_time
{0:{fit_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90},1:{0:{fitting_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90}},unix_time_0


The meaning of the parameters is in the paper but basically the're A0,A1,A2, etc...

Just as a side note we know that the whole interval of time(t) has 1024 samples, but we only parametrized from 0 to peak+30
samples, from our parameters A1 gives us the position of the peak, say it's 200, then we're gonna plot from 0 to 230.
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

from Functions import get_raw_datFile, get_raw_rootFile, perform_fit_on_dataframe, f

dt = 0.3125 # multiply sample_i by this to get it in ns
max_number_samples = 1024

def main():
    voltage = 55
    trigger = '0.004'
    day = 20
    month = 8
    run = 0

    # Load raw data
    df = get_raw_datFile(fr".\Data\Raw_data\10Bar_3Ch\FollowingCorrectProcedure\TriggerCh0_PS{voltage}V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat")
    trigger = float(trigger)

    total_time = df['unix_time'].iloc[-1] - df['unix_time'].iloc[0]
    RATE = len(df) / total_time

    # Extract raw samples
    ch0 = [np.array(ev[0]) for ev in df["channels"]]
    ch1 = [np.array(ev[1]) for ev in df["channels"]]
    ch2 = [np.array(ev[2]) for ev in df["channels"]]

    # ---------------------------------------------------------
    # Set up animation figure
    # ---------------------------------------------------------
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))
    
    line_0, = axs[0].plot([], [], label="CH0")
    line_1, = axs[0].plot([], [], label="CH1")
    line_2, = axs[1].plot([], [], label="CH2")
    axs[0].set_xlim(-0.1, max_number_samples*dt)
    axs[0].set_ylim((np.min(ch1)>np.min(ch0))*(np.min(ch0))+(np.min(ch1)<np.min(ch0))*(np.min(ch1)) - 0.005,
                    0.1)
    axs[0].axhline(y=trigger, alpha=0.5, color="green", label=f'Trigger_level={round(trigger,3)}')
    axs[0].set_xlabel('Time (ns)')
    axs[0].set_ylabel('Signal (V)')
    axs[0].legend()
    axs[0].grid(True)
    

    #
    axs[1].set_xlabel('Time (ns)')
    axs[1].set_ylabel('Signal (V)')
    axs[1].set_xlim(-0.1, max_number_samples*dt)
    axs[1].set_ylim(np.min(ch2) - 0.005, np.max(ch2) + 0.005)
    axs[1].axhline(y=trigger, alpha=0.5, color="green", label=f'Trigger_level={round(trigger,3)}')
    axs[1].legend()
    axs[1].grid(True)

    fig.tight_layout(rect=[0, 0, 1, 0.97])

    # ---------------------------------------------------------
    # Animation update function
    # ---------------------------------------------------------
    def update(frame):
        # Channel 0
        samples0 = ch0[frame]
        baseline_0 = np.mean(samples0[:100])
        samples0_corr = samples0 - baseline_0
        A0 = np.max(samples0_corr)
        t_ch0 = np.arange(len(samples0))*dt
        
        
        # Channel 1
        samples1 = ch1[frame]
        baseline_1 = np.mean(samples1[:100])
        samples1_corr = samples1 - baseline_1
        A1 = np.max(samples1_corr)
        t_ch1 = np.arange(len(samples1))*dt
        

        # Channel 2
        samples2 = ch2[frame]
        baseline_2 = np.mean(samples2[:100])
        samples2_corr = samples2 - baseline_2
        A2 = np.max(samples2_corr)
        t_ch2 = np.arange(len(samples2))*dt
        

        if True:#A0 > 0.085 or A1 > 0.095 or A2 > 0.045:
            line_0.set_data(t_ch0, samples0)
            line_1.set_data(t_ch1, samples1)
            line_2.set_data(t_ch2, samples2)

        title = axs[0].set_title(f'Waveforms; Event {frame}; rate={int(round(RATE,0))}Hz')

        return line_0, line_1, line_2, title

    ani = animation.FuncAnimation(
        fig,
        update,
        frames= 100, #From where to where do I plot and in how many steps
        interval = 500, # How much time does the present frame last in ms
        blit=False
    )
    ani.save(r".\All_plots_with_raw_data_3Ch\Plots\FullSignalAnimation.gif", writer="pillow", fps=5)
    plt.show()


if __name__ == "__main__":
    main()