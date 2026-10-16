'''
The data structure of the data frames should be something like this:
channels,unix_time
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_0
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_1
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_2
...

'''
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from Functions import get_raw_datFile, get_raw_rootFile, perform_fit_on_dataframe, get_t_with_fit

dt = 0.3125
def main(df, rate, route_figure):
    X_bottom = []
    X_top = []
    L = 170
    v = 15.95

    for row in df['channels']:
        t0 = get_t_with_fit(row[0], 0.1)
        t1 = get_t_with_fit(row[1], 0.1)
        t2 = get_t_with_fit(row[2], 0.1)
        t3 = get_t_with_fit(row[3], 0.1)

        X_top.append((v*(t3 - t2) + L)/2)
        X_bottom.append((v*(t1 - t0) + L)/2)

    fig, ax = plt.subplots(2, 1, figsize=(10, 10))

    # Histogram (density=False so we fit counts)
    N = 0.2
    bins = int(round(N * np.sqrt(len(X_bottom)),0))

    # Plot histogram
    print("min(X_top)", min(X_top))
    print("max(X_top)", max(X_top))
    ax[0].hist(X_top, bins=bins, histtype='step', density=False, label=f"bins={bins}")
    ax[0].set_title(f"X_top Distribution (events={len(X_top)}, rate={rate} Hz)")
    ax[0].set_xlabel("X (cm)")
    ax[0].set_ylabel("Counts")
    ax[0].legend()
    ax[0].grid(True)

    print("min(X_bottom)", min(X_bottom))
    print("max(X_bottom)", max(X_bottom))
    ax[1].hist(X_bottom, bins=bins, histtype='step', density=False, label=f"bins={bins}")
    ax[1].set_title(f"X_bottom Distribution (events={len(X_bottom)}, rate={rate} Hz)")
    ax[1].set_xlabel("X (cm)")
    ax[1].set_ylabel("Counts")
    ax[1].legend()
    ax[1].grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}/Histogram_X_Distribution.png", dpi=300)
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":
    print("\nStarting execution\n")

    voltage = '0.020'
    run = '5'
    day = '25'
    month = '6'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_fit_data_4Ch\Plots"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\2Bar_4Ch\CoincidenceMode\COIN_CH0123_PS57V_GL15ns\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df = get_raw_datFile(route_data)

    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    df_fit = perform_fit_on_dataframe(df)

    main(df_fit, RATE, route_figure)
    
    print("\nEnd of execution.\n")