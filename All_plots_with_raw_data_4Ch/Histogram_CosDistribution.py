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
from Functions import get_raw_datFile, get_t

dt = 0.3125
v = (13.92 + 14.92)/2
L = 170
d = 5

def model(u, A):
    return A * np.cos(u)**2

def main(df, rate, route_figure):
    COS = []
    for row in df['channels']:
        t0 = get_t(row[0],0.2)
        t1 = get_t(row[1],0.2)
        t2 = get_t(row[2],0.2)
        t3 = get_t(row[3],0.2)

        x_top = ( v*(t1 - t0)+ L)/2
        x_bottom = ( v*(t3 - t2)+ L)/2
        dx = x_bottom - x_top

        cos2 = (dx/np.sqrt(dx**2 + d**2))**2
        COS.append(cos2)

    COS = np.array(COS)

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    # Histogram
    N = 1
    bins0 = int(round(N * np.sqrt(len(COS)),0))
    counts, bin_edges, _ = ax.hist(
        COS,
        bins=bins0,
        alpha=0.7,
        label=f'Data; bins={bins0}',
        range=[min(COS), max(COS)],
        histtype='step',
        density=True
    )

    # Bin centers
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    # Fit
    popt, pcov = curve_fit(model, bin_centers, counts)
    A_fit = popt[0]

    # Plot fitted model
    X = np.linspace(0, 1, 200)
    #ax.plot(X, model(X, 1), color='red', alpha=0.8,
    #        label=f'Fit: A·cos²θ,  A={A_fit:.3f}')

    ax.set_title(f"COS² distribution (samples={len(COS)}; rate={rate} Hz)")
    ax.set_ylabel("Counts")
    ax.set_xlabel("COS² (a.u.)")
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\Cos_Histogram.png")
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