'''
In this script I'll just do all the plots we're interested in making and save them in a single folder.

The struture of the processed data is as follows:
{0:{fit_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90},1:{0:{fitting_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90}},unix_time_0

'''

# Scripts I did before to plot
from Histograms1D_Charge_amplitudes_mk1 import main as main_histograms
from Plot2D_Charge_vs_TimeDifference import main as main_charge_vs_time
from Plot2D_RatioCharges_vs_TimeDifference import main as main_ratio_charge_vs_time
from Plot2D_RiseTime_vs_TimeDifference import main as main_rise_time_vs_time_difference
from Plot2D_charge_vs_charge import main as main_charge_vs_charge
from Histogram_TimeDifference import main as main_histogram_time_difference

def main():
    voltage = '57' # In 58 we just begin to distinguish the muon mountain
    run = '1'
    gate_length = '15' # in ns
    trigger = '0.05' # in volts.
    day = '9'
    month = '3'

    # route of data
    route_data = f".\\Data\\Processed_data\\1Bar_2Chs\\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.csv"
    #route_data = f".\\Data\\Processed_data\\1Bar_2Chs\\57V_varying_gatelength_and_trigger_only\\Run_{trigger}V_Run{run}_Data_{month}_{day}_2026_Ascii.csv"
    
    #route of folder where to save the figures
    #route_figure = fr".\Plots\1Bar_2Chs\57V_Run1_triggerNormal_0.05_gate_15ns_tr"
    #route_figure = fr".\Plots\1Bar_2Chs\VaryingTriggerGate\{trigger} with {gate_length}ns"
    route_figure = fr".\Plots\1Bar_2Chs\57V_Run1_triggerNormal_0.05_gate_15ns_tr\Scan_RefCh0_Ch1Above10mV"

    # Make all the plots
    main_histograms(route_data, route_figure, float(trigger))
    main_ratio_charge_vs_time(route_data, route_figure, float(trigger))
    main_charge_vs_charge(route_data, route_figure, float(trigger))
    main_histogram_time_difference(route_data, route_figure, float(trigger))
    for i in [0,1]:
        main_charge_vs_time(route_data, route_figure, i, float(trigger))
        main_rise_time_vs_time_difference(route_data, route_figure, i, float(trigger))

    return 0

if __name__ == "__main__":
    main()
    print("\nEnd of execution.\n")