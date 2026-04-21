'''
In this script I'll just do all the plots we're interested in making and save them in a single folder.

The struture of the processed data is as follows:
{0:{fit_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90},1:{0:{fitting_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90}},unix_time_0

'''

# Standard python libraries
import ast
import pandas as pd

from Functions import discriminated_df, compare_df, get_raw_data

# Scripts I did for plotting and saving plots
from Histograms1D_Charge_amplitudes_mk1 import main as charge_histogram
from Plot2D_Charge_vs_TimeDifference import main as main_charge_vs_time
from Plot2D_RatioCharges_vs_TimeDifference import main as ratio_charge_vs_time
from Plot2D_RiseTime_vs_TimeDifference import main as rise_time_vs_time_difference
from Plot2D_charge_vs_charge import main as charge_vs_charge
from Histogram_TimeDifference import main as histogram_time_difference
from Plot2D_Amplitude_vs_TimeDifference import main as amplitude_vs_time_difference
from RatioAmplitudes_vs_TimeDifference import main as ratio_amplitude_vs_time_difference
from FWHM_vs_time_difference import main as FWHM_vs_time_difference

def main():
    voltage = '57' # In 58 we just begin to distinguish the muon mountain
    run = '5'
    gate_length = '15' # in ns
    channel_source = '0'
    trigger = '0.02' # in volts.
    day = '15'
    month = '4'

    #route of folder where to save the figures
    route_figure = fr".\Plots\1Bar_2Chs\Tests"

    # route of data
    route_fit_data = f".\\Data\\Processed_data\\1Bar_2Chs\\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.csv"
    df_fit = pd.read_csv(route_fit_data)
    df_fit["channels"] = df_fit["channels"].apply(ast.literal_eval)

    # route of original data, will only use it to compare with the fit and discriminate events
    route_og_data = f".\\Data\\Raw_data\\1Bar_2Chs\\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df_raw = get_raw_data(route_og_data)

    df = compare_df(df_fit,df_raw)

    #df = discriminated_df(df, float(trigger))

    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    # Make all the plots
    charge_histogram(df, RATE, route_figure)
    ratio_charge_vs_time(df, RATE, route_figure)
    ratio_amplitude_vs_time_difference(df, RATE, route_figure)
    charge_vs_charge(df, RATE, route_figure)
    histogram_time_difference(df, RATE, route_figure)
    for i in [0,1]:
        main_charge_vs_time(df, RATE, route_figure, i)
        rise_time_vs_time_difference(df, RATE, route_figure, i)
        amplitude_vs_time_difference(df, RATE, route_figure, i)
        FWHM_vs_time_difference(df, RATE, route_figure, i)

    return 0

if __name__ == "__main__":
    main()
    print("\nEnd of execution.\n")