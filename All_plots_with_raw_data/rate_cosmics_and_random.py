'''
In this script I'll just take the data of the special run and plot it, by special run I mean that I did a run
just to measure the rate without taking wf data, this should be more accurate to measure the rate.

The data structure of the data frames should be something like this:
channels,unix_time
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_0
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_1
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_2
...

'''

import numpy as np
import matplotlib.pyplot as plt
from Rate_vs_trigger import main as manual_runs
from scipy.optimize import curve_fit

def rate_model(V, a, b, c, d, e, f):
    return a*V**5 + b*V**4 + c*V**3 + d*V**2 + e*V + f

def perform_fit(thresholds, rates):
    # Remove zeros or negative values (log-fit stability)
    mask = rates > 0 # Although for what I see we have no zeros.
    V_fit = thresholds[mask] # V_fit is threshold values
    R_fit = rates[mask] # R_fit is the corresponding rates for those thresholds

    # Fit
    params, cov = curve_fit(rate_model, V_fit, R_fit) # Constrain parameters to be positive
    P = params # Extract fitted parameters: Rmu is muon plateau, A is dark amplitude, k is slope of exponential decay
    
    return P

def read_rate_vs_threshold(filename):
    thresholds = []
    rates_ch0 = []
    rates_ch1 = []

    reading_x = False
    reading_y0 = False
    reading_y1 = False

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()

            # Detect section starts
            if "X AXIS" in line:
                reading_x = True
                reading_y0 = False
                reading_y1 = False
                continue

            if "Y AXIS" in line and "CHANNEL : 0" in line:
                reading_x = False
                reading_y0 = True
                reading_y1 = False
                continue

            if "Y AXIS" in line and "CHANNEL : 1" in line:
                reading_x = False
                reading_y0 = False
                reading_y1 = True
                continue

            # Stop reading when a new header appears
            if line.startswith("=="):
                reading_x = False
                reading_y0 = False
                reading_y1 = False
                continue

            # Read numbers
            if reading_x:
                thresholds.extend([float(x) for x in line.split()])

            if reading_y0:
                rates_ch0.extend([float(x) for x in line.split()])

            if reading_y1:
                rates_ch1.extend([float(x) for x in line.split()])

    return np.array(thresholds), np.array(rates_ch0), np.array(rates_ch1)


def main():
    filename = fr".\Data\Raw_data\1Bar_2Chs\57Vcoincidence\rate_vs_threshold\Test_time5s_steps500_0.001_to_0.06.dat"

    # obtain data
    thresholds, rates_ch0, rates_ch1 = read_rate_vs_threshold(filename)
    idx = np.where( thresholds == 0.005)
    i, step = int(idx[0][0]), 5
    thresholds_fit, rates_ch0_fit, rates_ch1_fit = thresholds[i::step], rates_ch0[i::step], rates_ch1[i::step]
    
    rate_coin, triggers = manual_runs(None)
    rate_coin_fit, triggers_fit = rate_coin[4::], triggers[4::] # Here's where trigger=0.005 the "sweet spot" as I call it :p

    # Perform fits: We may try to fit/give only like 100 points for the  first two.
    P_CH0 = perform_fit(np.array(thresholds_fit), np.array(rates_ch0_fit))
    P_CH1 = perform_fit(np.array(thresholds_fit), np.array(rates_ch1_fit))
    P_COIN = perform_fit(np.array(triggers_fit), np.array(rate_coin_fit))

    CH0 = lambda x: P_CH0[0]* np.power(x,5) + P_CH0[1]*np.power(x,4) + P_CH0[2]*np.power(x,3) + P_CH0[3]*np.power(x,2) + P_CH0[4]*np.power(x,1) + P_CH0[5]
    CH1 = lambda x: P_CH1[0]*np.power(x,5) + P_CH1[1]*np.power(x,4) + P_CH1[2]*np.power(x,3) + P_CH1[3]*np.power(x,2) + P_CH1[4]*np.power(x,1) + P_CH1[5]
    COIN = lambda x: P_COIN[0]*np.power(x,5) + P_COIN[1]*np.power(x,4) + P_COIN[2]*np.power(x,3) + P_COIN[3]*np.power(x,2) + P_COIN[4]*np.power(x,1) + P_COIN[5]

    window = 20e-9 #This in oscilloscope is 15ns but I'll try with what Federico told me.
    R2_plus = lambda x: ((1 - window*(CH0(x) - CH1(x))) + np.sqrt( np.power(1-window*(CH0(x) - CH1(x)),2) - 4*window*(CH1(x) - COIN(x)) ))/2*window
    R2_minus = lambda x: ((1 - window*(CH0(x) - CH1(x))) - np.sqrt( np.power(1-window*(CH0(x) - CH1(x)),2) - 4*window*(CH1(x) - COIN(x)) ))/2*window

    R1_plus = lambda x: ((1 - window*(CH1(x) - CH0(x))) + np.sqrt( np.power(1-window*(CH1(x) - CH0(x)),2) - 4*window*(CH0(x) - COIN(x)) ))/2*window
    R1_minus = lambda x: ((1 - window*(CH1(x) - CH0(x))) - np.sqrt( np.power(1-window*(CH1(x) - CH0(x)),2) - 4*window*(CH0(x) - COIN(x)) ))/2*window
    
    cosmics_plus = lambda x: COIN(x) - R1_plus(x)*R2_plus(x)*window
    cosmics_minus = lambda x: COIN(x) - R1_minus(x)*R2_minus(x)*window
    
    # Plot
    plt.figure(figsize=(10,6))
    #plt.plot(thresholds_fit, CH0(thresholds_fit), label='CH0 Rate', linestyle='-', alpha=0.7)
    #plt.plot(thresholds_fit, CH1(thresholds_fit), label='CH1 Rate', linestyle='-', alpha=0.7)
    plt.plot(thresholds_fit, COIN(thresholds_fit), label='Coincidence rate', linestyle='-', alpha=0.7)

    #plt.plot(thresholds_fit, R2_plus(thresholds_fit), label='R2(+)', linestyle='--', alpha=0.7)
    #plt.plot(thresholds_fit, R2_minus(thresholds_fit), label='R2(-)', linestyle='--', alpha=0.7)
    
    #plt.plot(thresholds_fit, R1_plus(thresholds_fit), label='R1(+)', linestyle='--', alpha=0.7)
    #plt.plot(thresholds_fit, R1_minus(thresholds_fit), label='R1(-)', linestyle='--', alpha=0.7)
    
    plt.plot(thresholds_fit, cosmics_plus(thresholds_fit), label='cosmics(++)', linestyle='--', alpha=0.7)
    plt.plot(thresholds_fit, cosmics_minus(thresholds_fit), label='cosmics(--)', linestyle='--', alpha=0.7)
    
    plt.xlabel("Threshold [V]")
    plt.ylabel("Rate [Hz]")
    plt.title("Rate vs Threshold")
    plt.grid(True, which="both", ls="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()

    return 0

if __name__ == "__main__":
    print('\nStarting execution.\n')
    main()
