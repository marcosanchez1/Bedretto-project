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

# My proper scripts
from Functions import get_raw_datFile, get_raw_rootFile, get_t

dt = 0.3125 # multiply sample_i by this to get it in ns
max_number_samples = 1024
def main():
    trigger_oscilloscope = 0.015

    # Load raw data
    df = get_raw_datFile(fr".\Data\Raw_data\2Bar_4Ch\CoincidenceMode\COIN_CH0123_PS57V_GL15ns\Run_0.015V_Run3_Data_6_9_2026_Ascii.dat")
    #df = get_raw_rootFile(fr".\Data\Raw_data\MIDAS\NormalMode\run02550.root")

    total_time = df['unix_time'].iloc[-1] - df['unix_time'].iloc[0]
    RATE = len(df) / total_time

    # Extract raw samples
    ch0 = [np.array(ev[0]) for ev in df["channels"]] #Baseline is around -1 for the 57V
    ch1 = [np.array(ev[1]) for ev in df["channels"]] # files I've been working.
    ch2 = [np.array(ev[2]) for ev in df["channels"]]
    ch3 = [np.array(ev[3]) for ev in df["channels"]]

    # ---------------------------------------------------------
    # Set up animation figure
    # ---------------------------------------------------------
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))
    
    line_0, = axs[0].plot([], [], label=f"CH0")
    line_1, = axs[0].plot([], [], label=f"CH1")
    axs[0].set_xlim(-0.1, max_number_samples*dt)
    axs[0].set_ylim((np.min(ch1)>np.min(ch0))*(np.min(ch0))+(np.min(ch1)<np.min(ch0))*(np.min(ch1)) - 0.005,
                    (np.max(ch1)>np.max(ch0))*(np.max(ch1))+(np.max(ch1)<np.max(ch0))*(np.max(ch0)) + 0.005)
    axs[0].set_xlabel('Time (ns)')
    axs[0].set_ylabel('Signal (V)')
    axs[0].axhline(y=trigger_oscilloscope, alpha=0.5, color="green", label=f'Trigger_level={round(trigger_oscilloscope,3)}')
    axs[0].legend()
    axs[0].grid(True)
    

    line_2, = axs[1].plot([], [], label=f"CH2")
    line_3, = axs[1].plot([], [], label=f"CH3")
    axs[1].set_xlabel('Time (ns)')
    axs[1].set_ylabel('Signal (V)')
    axs[1].set_xlim(-0.1, max_number_samples*dt)
    axs[1].set_ylim((np.min(ch3)>np.min(ch2))*(np.min(ch2))+(np.min(ch3)<np.min(ch2))*(np.min(ch3)) - 0.005,
                    (np.max(ch3)>np.max(ch2))*(np.max(ch3))+(np.max(ch3)<np.max(ch2))*(np.max(ch2)) + 0.005)
    #axs[1].axhline(y=baseline2, alpha=0.5, color="red", label=f'Baseline={round(baseline2,3)}')
    axs[1].axhline(y=trigger_oscilloscope, alpha=0.5, color="green", label=f'Trigger_level={round(trigger_oscilloscope,3)}')
    axs[1].legend()
    axs[1].grid(True)

    fig.tight_layout(rect=[0, 0, 1, 0.97])

    # ---------------------------------------------------------
    # Animation update function
    # ---------------------------------------------------------
    def update(frame):
        # Channel 0
        samples0 = ch0[frame]
        t_ch0 = np.arange(len(samples0))*dt
        line_0.set_data(t_ch0, samples0)
        
        # Channel 1
        samples1 = ch1[frame]
        t_ch1 = np.arange(len(samples1))*dt
        line_1.set_data(t_ch1, samples1)

        # Channel 2
        samples2 = ch2[frame]
        t_ch2 = np.arange(len(samples2))*dt
        line_2.set_data(t_ch2, samples2)

        # Channel 3
        samples3 = ch3[frame]
        t_ch3 = np.arange(len(samples3))*dt
        line_3.set_data(t_ch3, samples3)

        title = axs[0].set_title(f'Waveforms; Event {frame}; rate={int(round(RATE,0))}Hz')

        return line_0, line_1, line_2, line_3, title

    ani = animation.FuncAnimation(
        fig,
        update,
        frames= 100, #From where to where do I plot and in how many steps
        interval = 500, # How much time does the present frame last in ms
        blit=False
    )
    #ani.save(r".\All_plots_with_raw_data_4Ch\Plots\FullSignalAnimation.gif", writer="pillow", fps=5)
    plt.show()


if __name__ == "__main__":
    main()