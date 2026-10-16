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
import sys
import os

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from Functions import get_raw_datFile, perform_fit_on_dataframe, f, get_t_with_fit

dt = 0.3125 # multiply sample_i by this to get it in ns
max_number_samples = 1024
def main():
    voltage = 57
    trigger = '-0.005'
    day = 12
    month = 10
    run = 0

    # Load raw data
    df = get_raw_datFile(fr".\Data\Raw_data\ExternalTriggerTests\TriggerCh0_{trigger}_NoCoincidence\Run_900V_Run1_Data_10_13_2026_Ascii.dat")
    df_fit = perform_fit_on_dataframe(df)
    #df = perform_fit_on_dataframe(get_raw_rootFile(fr".\Data\Raw_data\MIDAS\run02594.root"))

    trigger = float(trigger)

    total_time = df['unix_time'].iloc[-1] - df['unix_time'].iloc[0]
    RATE = len(df) / total_time

    # Extract raw samples
    ch0 = [np.array(ev[4]) for ev in df["channels"]]
    ch1 = [np.array(ev[5]) for ev in df["channels"]]
    ch2 = [np.array(ev[6]) for ev in df["channels"]]
    ch3 = [np.array(ev[7]) for ev in df["channels"]]

    # ---------------------------------------------------------
    # Set up animation figure
    # ---------------------------------------------------------
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))
    
    line_0, = axs[0].plot([], [], label=f"CH4")
    line_1, = axs[0].plot([], [], label=f"CH5")
    line_0_fit, = axs[0].plot([], [], label=f"CH4 fit")
    line_1_fit, = axs[0].plot([], [], label=f"CH5 fit")
    axs[0].set_xlim(-0.1, max_number_samples*dt)
    axs[0].set_ylim((np.min(ch1)>np.min(ch0))*(np.min(ch0))+(np.min(ch1)<np.min(ch0))*(np.min(ch1)) - 0.005,
                    np.max(ch1)*(np.max(ch1)>np.max(ch0)) + np.max(ch0)*(np.max(ch1)<np.max(ch0)) + 0.005)
    axs[0].set_xlabel('Time (ns)')
    axs[0].set_ylabel('Signal (V)')
    axs[0].axhline(y=trigger, alpha=0.5, color="green", label=f'Trigger_level={round(trigger,3)}')
    axs[0].legend()
    axs[0].grid(True)
    

    line_2, = axs[1].plot([], [], label=f"CH6")
    line_2_fit, = axs[1].plot([], [], label=f"CH6_fit")
    line_3, = axs[1].plot([], [], label=f"CH7")
    line_3_fit, = axs[1].plot([], [], label=f"CH7_fit")
    axs[1].set_xlabel('Time (ns)')
    axs[1].set_ylabel('Signal (V)')
    axs[1].set_xlim(-0.1, max_number_samples*dt)
    axs[1].set_ylim((np.min(ch3)>np.min(ch2))*(np.min(ch2))+(np.min(ch3)<np.min(ch2))*(np.min(ch3)) - 0.005,
                    np.max(ch3)*(np.max(ch3)>np.max(ch2)) + np.max(ch2)*(np.max(ch3)<np.max(ch2)) + 0.005)
    axs[1].axhline(y=trigger, alpha=0.5, color="green", label=f'Trigger_level={round(trigger,3)}')
    axs[1].legend()
    axs[1].grid(True)

    fig.tight_layout(rect=[0, 0, 1, 0.97])

    # ---------------------------------------------------------
    # Animation update function
    # ---------------------------------------------------------
    def update(frame):
        # Channel 4
        samples0 = ch0[frame]
        t_ch0 = np.arange(len(samples0))*dt
        line_0.set_data(t_ch0, samples0)
        line_0_fit.set_data(t_ch0, f(t_ch0, df_fit['channels'].iloc[frame][4]))
        
        # Channel 4
        samples1 = ch1[frame]
        t_ch1 = np.arange(len(samples1))*dt
        line_1.set_data(t_ch1, samples1)
        line_1_fit.set_data(t_ch1, f(t_ch1, df_fit['channels'].iloc[frame][4]))

        # Channel 6
        samples2 = ch2[frame]
        t_ch2 = np.arange(len(samples2))*dt
        line_2.set_data(t_ch2, samples2)
        line_2_fit.set_data(t_ch2, f(t_ch2, df_fit['channels'].iloc[frame][6]))

        # Channel 7
        samples3 = ch3[frame]
        t_ch3 = np.arange(len(samples3))*dt
        line_3.set_data(t_ch3, samples3)
        line_3_fit.set_data(t_ch3, f(t_ch3, df_fit['channels'].iloc[frame][7]))

        title = axs[0].set_title(f'Waveforms; Event {frame}; rate={round(RATE, 3)}Hz')

        return line_0, line_1, line_2, line_3, title, line_0_fit, line_1_fit, line_2_fit, line_3_fit

    ani = animation.FuncAnimation(
        fig,
        update,
        frames= len(df), #From where to where do I plot and in how many steps
        interval = 500, # How much time does the present frame last in ms
        blit=False
    )
    #ani.save(r".\External_Trigger_Tests_Scripts\Plots\FullSignalAnimation.gif", writer="pillow", fps=5)
    plt.show()
    plt.close()


if __name__ == "__main__":
    main()