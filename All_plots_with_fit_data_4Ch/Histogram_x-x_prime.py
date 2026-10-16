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
import os
import sys

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from Functions import get_raw_datFile, get_raw_rootFile, get_t_with_fit, perform_fit_on_dataframe, f, get_t_with_samples

dt = 0.3125
v = 15.95
L = 170
d = 4
def main(df, rate, route_figure):
    x = []
    x_p = []
    difference_x = []
    for row in df['channels']:
        t0 = get_t_with_fit(row[0],0.1)
        t1 = get_t_with_fit(row[1],0.1)
        t2 = get_t_with_fit(row[2],0.1)
        t3 = get_t_with_fit(row[3],0.1)

        x_aux = (v*(t3-t2) + L)/2
        x_p_aux = (v*(t1-t0) + L)/2

        x.append(x_aux)
        x_p.append(x_p_aux)
        difference_x.append(x_aux - x_p_aux)

    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    ax0, ax1, ax2, ax3 = ax.flatten()
    
    N = 0.2
    bins0 = int(round( N * np.sqrt(len(x)),0))
    h0 = ax0.hist(
            x,
            bins=bins0,
            alpha=0.7,
            label=f'bins={bins0}',
            range=[min(x), max(x)],
            histtype='step'
            )
    ax0.set_title(f"x distribution (samples={len(x)};rate={rate}Hz)")
    ax0.set_ylabel("Counts")
    ax0.set_xlabel("x (cm)")
    ax0.legend()
    ax0.grid(True)

    bins1 = int(round(N * np.sqrt(len(x_p)),0))
    h1 = ax1.hist(
            x_p,
            bins=bins1,
            alpha=0.7,
            label=f'bins={bins1}',
            range=[min(x_p), max(x_p)],
            histtype='step'
            )
    ax1.set_title(f"x' distribution (samples={len(x_p)};rate={rate}Hz)")
    ax1.set_ylabel("Counts")
    ax1.set_xlabel("x' (cm)")
    ax1.legend()
    ax1.grid(True)

    bins2 = 50#int(round( N * np.sqrt(len(difference_x)),0))
    h2 = ax2.hist(
            difference_x,
            bins=bins2,
            alpha=0.7,
            label=f'bins={bins2}',
            range=[min(difference_x), max(difference_x)],
            histtype='step'
            )
    ax2.set_title(f"x-x' distribution (samples={len(difference_x)};rate={rate}Hz)")
    ax2.set_ylabel("Counts")
    ax2.set_xlabel("x-x' (cm)")
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\x_and_x_prime_Histograms.png")
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
    df = get_raw_datFile(route_data)
    
    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    df_fit = perform_fit_on_dataframe(df)
    main(df_fit, RATE, route_figure)

    print("\nEnd of execution.\n")