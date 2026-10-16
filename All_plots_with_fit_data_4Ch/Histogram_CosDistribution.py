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
from scipy.optimize import curve_fit
import os
import sys

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from Functions import get_raw_datFile, get_raw_rootFile, perform_fit_on_dataframe, get_t_with_fit

dt = 0.3125
v = 15.95
c = 30
L = 170
d = 4


def main(df, rate, route_figure):
    COS = []
    COS2 = []
    THETA = []
    X = []
    X_p = []
    for row in df['channels']:
        t0 = get_t_with_fit(row[0],0.1)
        t1 = get_t_with_fit(row[1],0.1)
        t2 = get_t_with_fit(row[2],0.1)
        t3 = get_t_with_fit(row[3],0.1)

        x = (v*(t3 - t2) + L)/2
        x_p = (v*(t1 - t0) + L)/2

        X.append(x)
        X_p.append(x_p)

        cos = d/(d**2 + (x-x_p)**2)**0.5
        COS.append(cos)
        
        cos2 = cos**2
        COS2.append(cos2)

        theta = np.arccos(cos) * 180/np.pi # just to convert to degrees
        theta = (x > x_p) * theta + (x <= x_p) * -theta
        THETA.append(theta)

    COS = np.array(COS)
    THETA = np.array(THETA)
    COS2 = np.array(COS2)
    X = np.array(X)
    X_p = np.array(X_p)

    fig, ax = plt.subplots(2, 2, figsize=(10, 10))

    # Histogram
    N = 1
    n_bins = int(round(N * np.sqrt(len(COS)),0))

    ax[0, 0].hist(
        COS2,
        bins=n_bins,
        alpha=0.7,
        label=f'Data; bins={n_bins}',
        range=[min(COS2), max(COS2)],
        histtype='step',
        density=False,
    )
    ax[0, 0].set_title(f"COS² distribution (samples={len(COS2)}; rate={rate} Hz)")
    ax[0, 0].set_ylabel("Counts")
    ax[0, 0].set_xlabel("COS² (a.u.)")
    ax[0, 0].legend()
    ax[0, 0].grid(True)
    
    ax[0, 1].hist(
        COS,
        bins=n_bins,
        alpha=0.7,
        label=f'Data; bins={n_bins}',
        range=[min(COS), max(COS)],
        histtype='step',
        density=False,
    )
    ax[0, 1].set_title(f"COS distribution (samples={len(COS)})")
    ax[0, 1].set_ylabel("Counts")
    ax[0, 1].set_xlabel("COS (a.u.)")
    ax[0, 1].legend()
    ax[0, 1].grid(True)
    
    ax[1, 0].hist(
        THETA,
        bins=n_bins,
        alpha=0.7,
        label=f'Data; bins={n_bins}',
        range=[min(THETA), max(THETA)],
        histtype='step',
        density=False,
    )
    ax[1, 0].set_title(f"THETA distribution (samples={len(THETA)})")
    ax[1, 0].set_ylabel("Counts")
    ax[1, 0].set_xlabel("THETA (°)")
    ax[1, 0].legend()
    ax[1, 0].grid(True)

    n_bins = 35
    ax[1, 1].hist(
        X,
        bins=n_bins,
        alpha=0.7,
        label=f'X_top; bins={n_bins}',
        range=[min(X), max(X)],
        histtype='step',
        density=False,
    )
    ax[1, 1].hist(
        X_p,
        bins=n_bins,
        alpha=0.7,
        label=f'X_bottom; bins={n_bins}',
        range=[min(X_p), max(X_p)],
        histtype='step',
        density=False,
    )
    ax[1, 1].set_title(f"X distribution (samples={len(X)})")
    ax[1, 1].set_ylabel("Counts")
    ax[1, 1].set_xlabel("X (cm)")
    ax[1, 1].legend()
    ax[1, 1].grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Cos_Histogram.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":

    voltage = '0.020'
    run = '5'
    day = '25'
    month = '6'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_fit_data_4Ch\Plots"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\2Bar_4Ch\CoincidenceMode\COIN_CH0123_PS57V_GL15ns\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    
    df = perform_fit_on_dataframe(get_raw_datFile(route_data))
        
    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")