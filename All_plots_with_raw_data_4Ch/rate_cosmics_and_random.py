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

def rate_model(V, a, b, c, d, e, f, g, h):
    return a*V**5 + b*V**4 + c*V**3 + d*V**2 + e*V + f + g*np.exp(-h*V)

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

def quadratic(A, B, C, sign):
    if sign == "+":
        return (-B + np.sqrt(B**2 - 4*A*C)) / (2*A)
    elif sign == "-":
        return (-B - np.sqrt(B**2 - 4*A*C)) / (2*A)
def main():
    filename = fr".\Data\Raw_data\1Bar_2Chs\57Vcoincidence_GateLength_15ns\rate_vs_threshold\Test_time5s_steps500_0.001_to_0.06.dat"

    # obtain data
    thresholds, rates_ch0, rates_ch1 = read_rate_vs_threshold(filename)
    idx = np.where( thresholds == 0.005)
    i, step = int(idx[0][0]), 1
    thresholds_fit, rates_ch0_fit, rates_ch1_fit = thresholds[i::step], rates_ch0[i::step], rates_ch1[i::step]
    
    rate_coin, triggers = manual_runs(None)
    rate_coin_fit, triggers_fit = rate_coin[4::], triggers[4::] # Here's where trigger=0.005 the "sweet spot" as I call it :p

    # Perform fits: We may try to fit/give only like 100 points for the  first two.
    P_CH0 = perform_fit(np.array(thresholds_fit), np.array(rates_ch0_fit))
    P_CH1 = perform_fit(np.array(thresholds_fit), np.array(rates_ch1_fit))
    P_COIN = perform_fit(np.array(triggers_fit), np.array(rate_coin_fit))

    CH0 = lambda x: rate_model(x, *P_CH0)
    CH1 = lambda x: rate_model(x, *P_CH1)
    COIN = lambda x: rate_model(x, *P_COIN)

    window = 15e-9 #This in oscilloscope is 15ns but I'll try with what Federico told me.
    epsilon = 0.8
    # The second root was the only one that made sense
    CS = lambda x: quadratic(window*(1-2*epsilon),
                             epsilon-(1-epsilon)*window*(CH0(x) + CH1(x)),
                             window*CH0(x)*CH1(x) - COIN(x),
                             "+")
    R0 = lambda x: CH0(x) - CS(x)
    R1 = lambda x: CH1(x) - CS(x)

    # Plot
    plt.figure(figsize=(10,6))
    domain = thresholds_fit

    plt.plot(domain, rates_ch0_fit, label='CH0 rate data', marker='o', linestyle='-', alpha=0.7)
    plt.plot(domain, rates_ch1_fit, label='CH1 rate data', marker='s', linestyle='-', alpha=0.7)
    plt.plot(triggers_fit, rate_coin_fit, label='Coincidence rate data', marker='x', linestyle='-', alpha=0.7)

    plt.plot(domain, [CH0(x) for x in domain], label='CH0 Rate fit', linestyle='-', alpha=0.7)
    plt.plot(domain, [CH1(x) for x in domain], label='CH1 Rate fit', linestyle='-', alpha=0.7)
    plt.plot(domain, [COIN(x) for x in domain], label='COIN Rate fit', linestyle='-', alpha=0.7)

    plt.plot(domain, [CS(x) for x in domain], label='CS', linestyle='--', alpha=0.7)
    plt.plot(domain, [R0(x) for x in domain], label='R0', linestyle='--', alpha=0.7)
    plt.plot(domain, [R1(x) for x in domain], label='R1', linestyle='--', alpha=0.7)

    plt.xlabel("Threshold [V]")
    plt.ylabel("Rate [Hz]")
    plt.title(f"Rate vs Threshold(\u03B5={epsilon})")
    plt.grid(True, which="both", ls="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()

    return 0

if __name__ == "__main__":
    print('\nStarting execution.\n')
    main()
