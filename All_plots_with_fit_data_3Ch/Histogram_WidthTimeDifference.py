'''
The data structure of the data frames should be something like this:
channels,unix_time
{0:[A0, A1, A2, ...],1:[A]},unix_time_event_0
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

def chunk_list(lst, size=100):
    return [lst[i:i+size] for i in range(0, len(lst), size)]

def histogram_width(values, bins=10):
    counts, bin_edges = np.histogram(values, bins=bins)
    right_edge = bin_edges[-1]
    left_edge = bin_edges[0]
    return right_edge - left_edge

dt = 0.3125
def main(df, rate, route_figure):
    time_diff_01 = []
    for row in df['channels']:
        t0 = get_t_with_fit(row[0], 0.1) - 0.31
        t1 = get_t_with_fit(row[1], 0.1)

        #if np.max(row[0]) > 0.03 and np.max(row[1]) > 0.04 and np.max(row[2]) > 0.04 and np.max(row[3]) > 0.05:
        time_diff_01.append(t1 - t0)
    
    chunks_01 = chunk_list(time_diff_01, 100)
    
    widths_01 = []
    for chunk in chunks_01:
        w = histogram_width(chunk)
        if w is not None:
            widths_01.append(w)

    question = 'y'
    N = 1
    while question.lower() == 'y':
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))

        bins = int(round( N * np.sqrt(len(widths_01)),0))
        h0 = ax.hist(
                widths_01,
                bins=bins,
                alpha=0.7,
                label=f'bins={bins};std={np.std(widths_01):.2f} ns',
                range=[min(widths_01), max(widths_01)],
                histtype='step'
                )
        ax.axvline(np.mean(widths_01), color='r', linestyle='dashed', linewidth=1, label=f'Mean={np.mean(widths_01):.2f} ns')
        ax.set_title(f"widths of t1-t0 distribution (samples={len(widths_01)})")
        ax.set_ylabel("Counts")
        ax.set_xlabel("widths (ns)")
        ax.legend()
        ax.grid(True)

        plt.tight_layout()
        plt.savefig(f"{route_figure}\\Widths_of_time_difference_Histograms.png")
        plt.show()
        plt.close()

        print('Do you want to continue? (y/n)')
        question = input()

        if question.lower() == 'y':
            N = float(input('Enter a new value for N (default is 1): '))

    return 0

if __name__ == "__main__":

    trigger = '0.015'
    voltage = '57'
    run = '0'
    day = '17'
    month = '8'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_fit_data_3Ch\Plots"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\10Bar_3Ch\coincidenceCh0Ch1Ch2_PS{voltage}V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df = get_raw_datFile(route_data)
    
    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    df_fit = perform_fit_on_dataframe(df)
    main(df_fit, RATE, route_figure)

    print("\nEnd of execution.\n")