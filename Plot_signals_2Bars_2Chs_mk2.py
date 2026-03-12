import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
import ast

def main():
    Voltage = 60
    th_oscilloscope = -0.99
    run = 0
    day = 10

    # Load data
    df = pd.read_csv(f".\\Data\\1Bar_2Chs_processed_data\\Run_{Voltage}V_Run{run}_Data_3_{day}_2026_Ascii.csv")
    df["channels"] = df["channels"].apply(ast.literal_eval)

    df_filtered = pd.read_csv(f".\\Data\\1Bar_2Chs_filtered_data\\Run_{Voltage}V_Run{run}_Data_3_{day}_2026_Ascii.csv")
    df_filtered["channels"] = df_filtered["channels"].apply(ast.literal_eval)

    dt = 1  # sampling in ps. 312e-12 to get it in seconds.

    RATE = len(df_filtered["unix_time"]) / (df_filtered['unix_time'].iloc[-1] - df_filtered['unix_time'].iloc[0])

    # Convert all samples to NumPy arrays for speed
    samples_ch1 = [np.array(ev[0]["samples"]) for ev in df["channels"]]
    samples_ch2 = [np.array(ev[1]["samples"]) for ev in df["channels"]]

    filtered_ch1 = [np.array(ev[0]["samples"]) for ev in df_filtered["channels"]]
    filtered_ch2 = [np.array(ev[1]["samples"]) for ev in df_filtered["channels"]]

    # Precompute time axes
    max_len = max(max(len(s) for s in samples_ch1),
                  max(len(s) for s in samples_ch2))
    t = np.arange(max_len) * dt

    # Precompute filtered time shifts
    t1_shifted = []
    t2_shifted = []

    for s, sf in zip(samples_ch1, filtered_ch1):
        shift = np.argmax(s) - np.argmax(sf)
        t1_shifted.append((np.arange(len(sf)) + shift) * dt)

    for s, sf in zip(samples_ch2, filtered_ch2):
        shift = np.argmax(s) - np.argmax(sf)
        t2_shifted.append((np.arange(len(sf)) + shift) * dt)

    # Compute global y-limits (fast)
    all_samples = np.concatenate(samples_ch1 + samples_ch2)
    ymin, ymax = all_samples.min(), all_samples.max()

    # Compute baselines
    baseline1 = np.mean([ev[0]["baseline"] for ev in df_filtered["channels"]])
    baseline2 = np.mean([ev[1]["baseline"] for ev in df_filtered["channels"]])

    # Prepare figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    line1, = ax1.plot([], [], lw=2, label="Original")
    line1_f, = ax1.plot([], [], lw=2, color="orange", label="Filtered")

    line2, = ax2.plot([], [], lw=2, label="Original")
    line2_f, = ax2.plot([], [], lw=2, color="orange", label="Filtered")

    # Set static axes
    for ax, baseline in [(ax1, baseline1), (ax2, baseline2)]:
        ax.set_xlim(0, t[-1])
        ax.set_ylim(ymin, ymax)
        ax.grid(True)
        ax.axhline(y=baseline, color="red", label=f'Baseline={round(baseline,3)}')
        ax.axhline(y=th_oscilloscope, color="green", label=f'Threshold_oscilloscope={th_oscilloscope}')
        ax.legend()

    # Lightweight update function
    def update(i):
        line1.set_data(np.arange(len(samples_ch1[i])) * dt, samples_ch1[i])
        line1_f.set_data(t1_shifted[i], filtered_ch1[i])

        line2.set_data(np.arange(len(samples_ch2[i])) * dt, samples_ch2[i])
        line2_f.set_data(t2_shifted[i], filtered_ch2[i])

        title1 = ax1.set_title(f"Channel 1 - Event {i} - Rate {int(round(RATE,0))}")
        title2 = ax2.set_title(f"Channel 2 - Event {i} - Rate {int(round(RATE,0))}")

        return line1, line1_f, line2, line2_f, title1, title2

    # I will not animate the whole thing we skip 1000 frames per image or something like that
    # this so that we can save the animation and doesn't take too long
    ani = animation.FuncAnimation(fig,
                                  update,
                                  frames=range(0,len(df),500),
                                  interval=30,
                                  blit=False)
    ani.save("signal_animation.gif", writer="pillow", fps=30)

    plt.show()

if __name__ == "__main__":
    main()