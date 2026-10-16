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
from Functions import get_raw_datFile, perform_fit_on_dataframe, get_t_with_fit

def main(df1, df2, route_figure):
        time_diff_01_df1 = []
        time_diff_01_df2 = []
        for row in df1['channels']:
                t0 = get_t_with_fit(row[0], 0.1)
                t1 = get_t_with_fit(row[1], 0.1)

                time_diff_01_df1.append(t1-t0)
        rate1 = int(round(len(df1)/(df1['unix_time'].iloc[-1] - df1['unix_time'].iloc[0]), 0))
        for row in df2['channels']:
                t0 = get_t_with_fit(row[0], 0.1)
                t1 = get_t_with_fit(row[1], 0.1)
                time_diff_01_df2.append(t1-t0)
        rate2 = int(round(len(df2)/(df2['unix_time'].iloc[-1] - df2['unix_time'].iloc[0]), 0))

        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        
        N = 0.5
        bins = int(round( N * np.sqrt(len(time_diff_01_df1)),0))
        h1 = ax.hist(
                time_diff_01_df1,
                bins=bins,
                alpha=0.7,
                label=f'bins={bins};rate={rate1}Hz',
                range=[min(time_diff_01_df1), max(time_diff_01_df1)],
                histtype='step',
                density=False
                )
        counts, bin_edges, _ = h1

        # index of the bin with the highest count
        idx_max = np.argmax(counts)

        # compute the bin center
        bin_center = 0.5 * (bin_edges[idx_max] + bin_edges[idx_max + 1])
        ax.axvline(x=bin_center, alpha=0.5, linestyle='--', color="blue", label=f'Center Value({bin_center:.2f})')

        h2 = ax.hist(
                time_diff_01_df2,
                bins=bins,
                alpha=0.7,
                label=f'bins={bins};rate={rate2}Hz; Swapped Cables',
                range=[min(time_diff_01_df2), max(time_diff_01_df2)],
                histtype='step',
                density=False
                )
        counts, bin_edges, _ = h2
        # index of the bin with the highest count
        idx_max = np.argmax(counts)
        # compute the bin center
        bin_center = 0.5 * (bin_edges[idx_max] + bin_edges[idx_max + 1])
        ax.axvline(x=bin_center, alpha=0.5, linestyle='--', color="orange", label=f'Center Value({bin_center:.2f})')

        ax.set_title(f"t1-t0 distribution (samples={len(time_diff_01_df1)})") #samples should be the same for both.
        ax.set_ylabel("Counts")
        ax.set_xlabel("t1-t0 (ns)")
        ax.legend()
        ax.grid(True)

        plt.tight_layout()
        plt.savefig(f"{route_figure}\\TimeDifference_ChangedCableChannel1_Histograms.png")
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
    route_data1 = fr".\Data\Raw_data\10Bar_3Ch\coincidenceCh0Ch1Ch2_PS{voltage}V\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    #route_data2 = fr".\Data\Raw_data\10Bar_3Ch\coincidenceCh0Ch1Ch2_PS{voltage}V\Run_{trigger}V_Run{run}_Data_{month}_18_2026_Ascii.dat"
    route_data2 = fr".\Data\Raw_data\10Bar_3Ch\coincidenceCh0Ch1Ch2_PS{voltage}V\Run_0.020V_Run0(swappedch0andch1)_Data_8_17_2026_Ascii.dat"

    df1 = get_raw_datFile(route_data1)
    df1 = perform_fit_on_dataframe(df1)

    df2 = get_raw_datFile(route_data2)
    df2 = perform_fit_on_dataframe(df2)

    main(df1, df2, route_figure)
          
    
    print("\nEnd of execution.\n")