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
v = (13.92 + 14.92)/2 # cm/ns
L = 170
d = 4
h = 1
def main():
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
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    # Points
    top_hits, = ax.plot([], [], 'o', label="Hits", color='red', alpha=0.65)
    bottom_hits, = ax.plot([], [], 'o', color='red', alpha=0.65)
    trajectory, = ax.plot([], [], label="Trajectory", color='blue', alpha=0.65)
    
    # bottom bar
    ax.plot([0,L], [0, 0], label=f"Bars", color='black')
    ax.plot([0,0], [0, h], color='black')
    ax.plot([L,L], [0, h], color='black')
    ax.plot([0,L], [h, h], color='black')
    # top bar
    ax.plot([0,L], [d, d], color='black')
    ax.plot([0,0], [d, d+ 1], color='black')
    ax.plot([L,L], [d, d+ 1], color='black')
    ax.plot([0,L], [d + 1, d + 1], color='black')

    ax.set_xlim(-1, L+1)
    ax.set_ylim(-h/2,d + h*1.5)
    ax.set_xlabel('X (cm)')
    ax.set_ylabel('Y (cm)')
    ax.legend()
    ax.grid(True)
    title = ax.set_title("")

    # ---------------------------------------------------------
    # Animation update function
    # ---------------------------------------------------------
    def update(frame):
        # Get times
        t0 = get_t(ch0[frame], 0.2)
        t1 = get_t(ch1[frame], 0.2)
        t2 = get_t(ch2[frame], 0.2)
        t3 = get_t(ch3[frame], 0.2)

        # Get positions
        x_top = (v*(t1 - t0) + L)/2
        x_bottom = (v*(t3 - t2) + L)/2

        # Plot hits
        top_hits.set_data([x_top], [d + h/2])
        bottom_hits.set_data([x_bottom], [h/2])
        
        # Trajectory line
        x_min, x_max = ax.get_xlim()
        m = (d + h/2 - h/2) / (x_top - x_bottom)
        b = h/2 - m * x_bottom
        x_line = [x_min, x_max]
        y_line = [m*x_min + b, m*x_max + b]
        trajectory.set_data(x_line, y_line)

        # update title
        title.set_text(f'Trajectory reconstruction(Event={frame}; rate={int(round(RATE,0))}Hz)')

        return title, top_hits, bottom_hits, trajectory

    ani = animation.FuncAnimation(
        fig,
        update,
        frames= 100, #From where to where do I plot and in how many steps
        interval = 500, # How much time does the present frame last in ms
        blit = False
    )
    ani.save(r".\All_plots_with_raw_data_4Ch\Plots\TrajectoryReconstructionAnimation.gif", writer="pillow", fps=5)
    plt.show()


if __name__ == "__main__":
    main()