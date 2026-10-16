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
from Functions import get_t, get_raw_datFile
from scipy.optimize import curve_fit

def gaussian(x, A, mu, sigma):
    return A * np.exp(-(x - mu)**2 / (2 * sigma**2))

def main(df, rate, route_figure):
    # Time sampling
    dt = 0.3125
    # Dimension of bar
    L = 170
    h = 1
    # Distance between center of bars
    d = 4
    # Speed of light in bar
    v = (13.92 + 14.92)/2

    X = []
    Y = []

    for row in df['channels']:

        # Bottom bar hit
        x_bottom = (v*(get_t(row[1], 0.2) - get_t(row[0], 0.2)) + L)/2
        X.append(x_bottom)
        Y.append(h/2)

        # Top bar hit
        x_top = (v*(get_t(row[3], 0.2) - get_t(row[2], 0.2)) + L)/2
        X.append(x_top)
        Y.append(h/2 + d)

    X = np.array(X)
    Y = np.array(Y)

    fig, ax = plt.subplots(figsize=(14, 10))

    # 2D histogram
    h = ax.hist2d(
        X, Y,
        bins=[70, 5],        # X bins, Y bins
        range=[[0, L], [0, h + d]],
        cmap='turbo'
    )

    ax.set_xlabel("X position along bar (cm)")
    ax.set_ylabel("Y position (cm)")
    ax.set_title(f"2D Hit Distribution (events={len(df)}; rate={rate} Hz)")
    ax.grid(True)

    # Colorbar
    cbar = plt.colorbar(h[3], ax=ax)
    cbar.set_label("Counts")

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Hit_Distribution_2D.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":

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