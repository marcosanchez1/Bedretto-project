'''
In this script I'll just plot/animate the signals and compare it with the fitted signals of the new files I'm getting.
The structure of the csv files is like:

     channel,unix_time
     {0:{fit_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90},1:{0:{fitting_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90}},unix_time_0

The meaning of the parameters is in the paper but basically the're A0,A1,A2, etc...
'''

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
import ast
from Functions import get_raw_data

dt = 0.312 # multiply sample_i by this to get it in ns
WINDOW = 30 * dt # We did the fit until max peak +10


def f(t, A):
    A0, A1, A2, A3, A4, A5, A6 = A
    n = t.size
    F = np.zeros(n)
    eps = 1e-12

    for i in range(n):
        ti = t[i]
        if ti <= A1:
            tl = ti - A1
            denom = 2 * (abs(A2) * tl + A3)**2 + eps
            F[i] = A0 * np.exp(-(tl*tl) / denom) + A6 # We remove the baseline term
        else:
            tr = ti - A1
            denom = 2 * (abs(A4) * tr + A5)**2 + eps
            F[i] = A0 * np.exp(-(tr*tr) / denom) + A6
    return F


def main():
    Voltage = 57
    trigger_oscilloscope = -0.950
    run = 0
    day = 16

    # Load raw data
    df_raw = get_raw_data(f".\\Data\\Raw_data\\1Bar_2Chs\\Run_{Voltage}V_Run{run}_Data_3_{day}_2026_Ascii.dat")

    # Load fitted data
    df_fit = pd.read_csv(f".\\Data\\Processed_data\\1Bar_2Chs\\Run_{Voltage}V_Run{run}_Data_3_{day}_2026_Ascii.csv")
    df_fit["channels"] = df_fit["channels"].apply(ast.literal_eval)

    # Extract raw samples
    raw_ch0 = [np.array(ev[0]) for ev in df_raw["channels"]] #Baseline is around -1 for the 57V
    raw_ch1 = [np.array(ev[1]) for ev in df_raw["channels"]] # files I've been working.

    RATE = len(raw_ch0) / (df_fit['unix_time'].iloc[-1] - df_fit['unix_time'].iloc[0])

    # Extract fitted parameters
    fit_ch0 = [np.array(ev[0]['fit_parameters']) for ev in df_fit["channels"]]
    fit_ch1 = [np.array(ev[1]['fit_parameters']) for ev in df_fit["channels"]]

    mean_baseline_0 = []
    mean_baseline_1 = []
    for i in range(len(fit_ch0)):
        mean_baseline_0.append(fit_ch0[i][6])
        mean_baseline_1.append(fit_ch1[i][6])
    mean_baseline_0 = np.mean(mean_baseline_0)
    mean_baseline_1 = np.mean(mean_baseline_1)

    # Time axis (sample index)
    t_full = np.arange(len(raw_ch0[0])) * dt

    # ---------------------------------------------------------
    # Set up animation figure
    # ---------------------------------------------------------
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))

    line_raw_0, = axs[0].plot([], [], label="Original_Data_Ch-0")
    line_fit_0, = axs[0].plot([], [], color='orange', ls = '--', lw=2, label="Fit_Ch-0")
    axs[0].set_xlim(0, len(raw_ch0[0])*dt)
    axs[0].set_ylim(min( [min(raw_ch0[i]) for i in range(len(raw_ch0))] )-0.1, max( [max(raw_ch0[i]) for i in range(len(raw_ch0))] )+0.1)
    axs[0].set_xlabel('Time (ns)')
    axs[0].set_ylabel('Signal (V)')
    axs[0].axhline(y=mean_baseline_0, alpha=0.5, color="red", label=f'Baseline={round(mean_baseline_0,3)}')
    axs[0].axhline(y=trigger_oscilloscope, alpha=0.5, color="green", label=f'Trigger_level={round(trigger_oscilloscope,3)}')
    axs[0].legend()
    axs[0].grid(True)

    line_raw_1, = axs[1].plot([], [], label="Original_Data_Ch1")
    line_fit_1, = axs[1].plot([], [], color='orange', ls = '--', lw=2, label="Fit_Ch1")
    axs[1].set_xlabel('Time (ns)')
    axs[1].set_ylabel('Signal (V)')
    axs[1].set_xlim(0, len(raw_ch1[0])*dt)
    axs[1].set_ylim(min( [min(raw_ch1[i]) for i in range(len(raw_ch1))] )-0.1, max( [max(raw_ch1[i]) for i in range(len(raw_ch1))] )+0.1)
    axs[1].axhline(y=mean_baseline_1, alpha=0.5, color="red", label=f'Baseline={round(mean_baseline_1,3)}')
    axs[1].axhline(y=trigger_oscilloscope, alpha=0.5, color="green", label=f'Trigger_level={round(trigger_oscilloscope,3)}')
    axs[1].legend()
    axs[1].grid(True)

    fig.tight_layout(rect=[0, 0, 1, 0.97])

    # ---------------------------------------------------------
    # Animation update function
    # ---------------------------------------------------------
    def update(frame):

        params0 = fit_ch0[frame]
        params1 = fit_ch1[frame]

        end = np.argmax(raw_ch0[frame])
        t_fit = np.arange(end)*dt

        # Channel 0
        samples0 = raw_ch0[frame]
        fit0 = f(t_fit, params0)

        line_raw_0.set_data(t_full, samples0)
        line_fit_0.set_data(t_fit, fit0)

        title = axs[0].set_title(f'Raw vs Fitted Waveforms; Event {frame}; rate={int(round(RATE,0))}events/s')

        end = np.argmax(raw_ch1[frame])
        t_fit = np.arange(end)*dt

        # Channel 1
        samples1 = raw_ch1[frame]
        fit1 = f(t_fit, params1)

        line_raw_1.set_data(t_full, samples1)
        line_fit_1.set_data(t_fit, fit1)

        return line_raw_0, line_fit_0, line_raw_1, line_fit_1, title

    frames_to_animate = []
    for i in range(len(fit_ch0)):
        t0 = df_fit["channels"].iloc[i][0]['t_10'] # We take the t_10 of the first channel as reference time for the event.
        t1 = df_fit["channels"].iloc[i][1]['t_10'] # We take the t_10 of the second channel as reference time for the event.
        time_difference = t0 - t1

        if True:#time_difference < -9: # We choose which events/frames to animate based on this condition in the time of signals.
            frames_to_animate.append(i)

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=frames_to_animate, #From where to where do I plot and in how many steps
        interval=500, # How much time does the present frame last in ms
        blit=False
    )
    #ani.save("signal_animation_fitted.gif", writer="pillow", fps=5)
    plt.show()


if __name__ == "__main__":
    main()