'''
In this script I'll perform an animation to compare the data we're getting with the algorithm I though of for the
static nosie line before the muon peaks on each channel.

The data structure of the data frames should be something like this:
channels,unix_time
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_0
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_1
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_2
...

'''

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd

# My proper scripts
from Functions import get_raw_data, rid_of_muon_signal

dt = 0.3125 # multiply sample_i by this to get it in ns
max_number_samples = 1024
def main():
    Voltage = '57'
    trigger_oscilloscope = 0.02
    run = 4
    day = 15 # For some reason for day 16 we have 272 samples in the raw files? It's not something I did I checked, the raw files simply are like that.
    month = 4

    # Load raw data
    #df_raw = get_raw_data(f".\\Data\\Raw_data\\1Bar_2Chs\\57V_varying_gatelength_and_trigger_only\\Run_{Voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat")
    df_raw = get_raw_data(f".\\Data\\Raw_data\\1Bar_2Chs\\Run_{Voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat")
    
    # It's working well just take into account that I'm taking a bit of the 10% of the muon peak.
    df_noise = rid_of_muon_signal(df_raw)

    RATE = len(df_raw) / (df_raw['unix_time'].iloc[-1] - df_raw['unix_time'].iloc[0])

    # Extract raw samples
    raw_ch0 = [np.array(ev[0]) for ev in df_raw["channels"]] #Baseline is around -1 for the 57V
    raw_ch1 = [np.array(ev[1]) for ev in df_raw["channels"]] # files I've been working.

    noise_ch0 = [np.array(ev[0]) for ev in df_noise["channels"]] #Baseline is around -1 for the 57V
    noise_ch1 = [np.array(ev[1]) for ev in df_noise["channels"]] # files I've been working.

    # ---------------------------------------------------------
    # Set up animation figure
    # ---------------------------------------------------------
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))

    line_raw_0, = axs[0].plot([], [], label="Original_CH0")
    line_noise_0, = axs[0].plot([], [], label="Noise_CH0")
    axs[0].set_xlim(-0.1, max_number_samples*dt)
    axs[0].set_ylim(np.min(noise_ch0[0])*1.1, np.max(noise_ch0[0])*1.5)
    axs[0].set_xlabel('Time (ns)')
    axs[0].set_ylabel('Signal (ADC)')
    axs[0].legend()
    axs[0].grid(True)

    line_raw_1, = axs[1].plot([], [], label="Original_CH1")
    line_noise_1, = axs[1].plot([], [], label="Noise_CH1")
    axs[1].set_xlabel('Time (ns)')
    axs[1].set_ylabel('Signal (ADC)')
    axs[1].set_xlim(-0.1, max_number_samples*dt)
    axs[1].set_ylim(np.min(noise_ch1[0])*1.1, np.max(noise_ch1[0])*1.5)
    axs[1].legend()
    axs[1].grid(True)

    fig.tight_layout(rect=[0, 0, 1, 0.97])

    # ---------------------------------------------------------
    # Animation update function
    # ---------------------------------------------------------
    def update(frame):
        # Channel 0
        samples0 = raw_ch0[frame]
        t_ch0 = np.arange(len(samples0))*dt
        line_raw_0.set_data(t_ch0, samples0)

        noise0 = noise_ch0[frame]
        t_ch0 = np.arange(len(noise0))*dt
        line_noise_0.set_data(t_ch0, noise0)


        title = axs[0].set_title(f'Raw vs Fitted Waveforms; Event {frame}; rate={int(round(RATE,0))}Hz')

        # Channel 1
        samples1 = raw_ch1[frame]
        t_ch1 = np.arange(len(samples1))*dt
        line_raw_1.set_data(t_ch1, samples1)

        noise1 = noise_ch1[frame]
        t_ch1 = np.arange(len(noise1))*dt
        line_noise_1.set_data(t_ch1, noise1)

        return line_raw_0, line_noise_0, line_raw_1, line_noise_1, title

    ani = animation.FuncAnimation(
        fig,
        update,
        frames= 100, #From where to where do I plot and in how many steps
        interval = 500, # How much time does the present frame last in ms
        blit=False
    )
    #ani.save(r".\All_plots_with_raw_data\NoiseSignalAnimation.gif", writer="pillow", fps=5)
    plt.show()


if __name__ == "__main__":
    main()