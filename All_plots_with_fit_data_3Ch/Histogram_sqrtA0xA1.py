'''
In this script I'll do a 1D histogram of the amplitudes of the signals.

The data structure of the data frames should be something like this:
channels,unix_time
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_0
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_1
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_2
...

'''
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from Functions import get_raw_datFile, get_raw_rootFile, perform_fit_on_dataframe, get_t_with_fit

def main(df, rate, route_figure):
    sqrtA0A1 = []
    for row in df['channels']:
        sqrtA0A1.append(np.sqrt(row[0][0] * row[1][0]))

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    N = 2
    bins = int(round(N * np.sqrt(len(sqrtA0A1)),0))
    h0 = ax.hist(
            sqrtA0A1,
            bins=bins,
            alpha=0.7,
            label=f'bins={bins}',
            range=[min(sqrtA0A1), max(sqrtA0A1)],
            histtype='step'
            )
    ax.set_title(f"Sqrt(A0*A1) distribution (samples={len(sqrtA0A1)};rate={rate}Hz)")
    ax.set_ylabel("Counts")
    ax.set_xlabel("sqrt(A0*A1) (V)")
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\sqrtA0A1_Histograms_Bars.png")
    plt.show()
    plt.close()

    return 0

if __name__ == "__main__":

    trigger = '0.020'
    voltage = '57'
    run = '0'
    day = '17'
    month = '8'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_fit_data_3Ch\Plots"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\10Bar_3Ch\coincidenceCh0Ch1Ch2_PS{voltage}V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii"
    
    # Get data frame from .dat or .root file
    df = get_raw_datFile(route_data + ".dat")
    df = perform_fit_on_dataframe(df)
        
    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")