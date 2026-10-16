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
from scipy.optimize import curve_fit

dt = 0.3125

def gaussian(x, A, mu, sigma):
    return A * np.exp(-(x - mu)**2 / (2 * sigma**2))

def main(df, rate, route_figure):
    X = []
    L = 170
    v = 13.49
    for row in df['channels']:
        X.append((v*(get_t(row[1], 0.2) - get_t(row[0], 0.2)) + L)/2)

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    # Histogram (density=False so we fit counts)
    N = 0.4
    bins = int(round(N * np.sqrt(len(X))))

    # Plot histogram
    ax.hist(X, bins=bins, histtype='step', density=False, label=f"bins={bins}")

    ax.set_title(f"X Distribution (events={len(X)}, rate={rate} Hz)")
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Counts")
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    plt.show()

    return 0

if __name__ == "__main__":

    voltage = '0.020'
    run = '10'
    day = '5'
    month = '5'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_raw_data\Plots\1Bar_2Ch\57Vcoincidence_GateLEngth_15ns\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\1Bar_2Ch\57Vcoincidence_GateLEngth_15ns\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df = get_raw_datFile(route_data)

    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")