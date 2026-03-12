import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import ast

def main():
    #Create charge list to store the charge of each event.
    charge_pc = []
    #dt = 312e-12 to get it in seconds
    dt = 1 #in units of ps

    #df = pd.read_csv(r".\Data\1Bar_1Ch_filtered_data\Run_56.88V_Run3_Data_3_2_2026_Ascii.csv")
    #df["samples"] = df["samples"].apply(ast.literal_eval)  # Convert string to list

    df = pd.read_csv(r".\Data\1Bar_1Ch_filtered_data\Run_53.91V_Run1_Data_3_2_2026_Ascii.csv")
    df["channel"] = df["channel"].apply(ast.literal_eval)

    # Integrate the signal to get charge
    for index, row in df.iterrows():
        
        # the 0 is the channel numbers
        row = row['channel'][0]  # No need to eval since we already converted to list
        samples = row['samples']
        baseline = row['baseline']

        # So here we're taking into consideration the baseline for this sample.
        samples = [samples[i]-baseline for i in range(len(samples))]
        charge = np.sum(samples) * dt  # Integrate discritely and convert to pC
        #charge = charge/(50) # Convert to pC assuming 50 ohm impedance
        
        # Say we try with just the maximum value, and for now I'll just assume is the max
        # the only thing we need/want.
        #charge = np.max(samples) * dt
        #charge = charge/(50) # Convert to pC assuming 50 ohm impedance

        charge_pc.append(charge)

    # Now just plot the charge distribution
    plt.figure(figsize=(10, 6))
    plt.hist(charge_pc, bins=100, color='blue', density=False, alpha=0.5, log=False, range=(min(charge_pc),max(charge_pc)))
    plt.xlabel("Charge (pC)")
    plt.ylabel("Events")
    plt.title("Charge Distribution")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()