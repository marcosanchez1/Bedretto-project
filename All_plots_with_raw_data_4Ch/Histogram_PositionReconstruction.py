'''
I define time of arrival at 10% of the amplitude, and I want to see the distribution of these.

The data structure of the data frames should be something like this:
channels,unix_time
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_0
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_1
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_2
...

'''
import numpy as np
import matplotlib.pyplot as plt
from Functions import get_t, get_raw_datFile
dt = 0.3125
def main(df, rate, route_figure):
    X_bottom = []
    X_top = []
    L = 170
    v = (13.92 + 14.92)/2

    for row in df['channels']:
        X_top.append((v*(get_t(row[3], 0.2) - get_t(row[2], 0.2)) + L)/2)
        X_bottom.append((v*(get_t(row[1], 0.2) - get_t(row[0], 0.2)) + L)/2)

    fig, ax = plt.subplots(2, 1, figsize=(10, 10))

    # Histogram (density=False so we fit counts)
    N = 0.4
    bins = int(round(N * np.sqrt(len(X_bottom)),0))

    # Plot histogram
    ax[0].hist(X_bottom, bins=bins, histtype='step', density=False, label=f"bins={bins}")
    ax[0].set_title(f"X Distribution (events={len(X_bottom)}, rate={rate} Hz)")
    ax[0].set_xlabel("X (cm)")
    ax[0].set_ylabel("Counts")
    ax[0].legend()
    ax[0].grid(True)

    ax[1].hist(X_top, bins=bins, histtype='step', density=False, label=f"bins={bins}")
    ax[1].set_title(f"X Distribution (events={len(X_top)}, rate={rate} Hz)")
    ax[1].set_xlabel("X (cm)")
    ax[1].set_ylabel("Counts")
    ax[1].legend()
    ax[1].grid(True)

    plt.tight_layout()
    plt.show()
    plt.savefig(f"{route_figure}/Histogram_X_Distribution.png", dpi=300)

    return 0

if __name__ == "__main__":
    print("\nStarting execution\n")

    voltage = '0.020'
    run = '4'
    day = '25'
    month = '6'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_raw_data_4Ch\Plots"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\2Bar_4Ch\CoincidenceMode\COIN_CH0123_PS57V_GL15ns\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df = get_raw_datFile(route_data)

    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")