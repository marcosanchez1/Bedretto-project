import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import ast

def main():
    voltage = 60
    th_oscilloscope = 0.05
    #dt = 312e-12 #to get it in units of s
    dt = 1 #in units of ps
    
    df = pd.read_csv(r".\Data\1Bar_2Chs_filtered_data\Run_{}V_Run1_Data_3_9_2026_Ascii.csv".format(voltage))
    df["channels"] = df["channels"].apply(ast.literal_eval)

    # Aggregate charge_pC from all processed CSV files
    charge_ch1_pc = []
    charge_ch2_pc = []

    mean_baseline1 = []
    mean_baseline2 = []

    # Integrate the signal to get charge
    for index, row in df.iterrows():
        
        # First get data for channel 1.
        samples_ch1 = row['channels'][0]['samples']
        baseline1 = row['channels'][0]['baseline']
        
        samples_ch1 = [samples_ch1[i] - baseline1 for i in range(len(samples_ch1))] #We take into consideration the baseline.
        #charge_ch1 = np.sum(samples_ch1) * dt # This would be strictly the integral
        charge_ch1 = np.max(samples_ch1) * dt  # This is taking only max as integral which is a fair assumption
        
        charge_ch1_pc.append(charge_ch1)
        mean_baseline1.append(baseline1)

        # Now let's get the data for channel 2
        samples_ch2 = row['channels'][1]['samples']
        baseline2 = row['channels'][1]['baseline']
        
        samples_ch2 = [samples_ch2[i] - baseline2 for i in range(len(samples_ch2))]
        #charge_ch2 = np.sum(samples_ch2)* dt # This would be strictly the integral
        charge_ch2 = np.max(samples_ch2)* dt # This is taking only max as integral which is a fair assumption
        
        charge_ch2_pc.append(charge_ch2)
        mean_baseline2.append(baseline2)

    mean_baseline1 = np.mean(mean_baseline1)
    mean_baseline2 = np.mean(mean_baseline2)
    # Now just plot the charge distribution
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.hist(charge_ch1_pc, bins=int(len(charge_ch1_pc)**0.5), alpha=0.7, label='Channel 1', range=(min(charge_ch1_pc), max(charge_ch1_pc)))
    #ax1.hist(charge_ch1_pc, bins=200, alpha=0.7, label='Channel 1', range=(min(charge_ch1_pc),20))
    ax1.set_xlabel('Charge (pC)')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Charge Distribution - Channel 1')
    ax1.axvline(x=th_oscilloscope, color="green", label = f'Threshold Oscilloscope={th_oscilloscope}')
    ax1.axvline(x=mean_baseline1, color="red", label = f'Baseline={round(mean_baseline1,3)}')
    ax1.legend()
    ax1.grid(True)
    

    ax2.hist(charge_ch2_pc, bins=int(len(charge_ch2_pc)**0.5), alpha=0.7, label='Channel 2', range=(min(charge_ch2_pc), max(charge_ch2_pc)))
    #ax2.hist(charge_ch2_pc, bins=200, alpha=0.7, label='Channel 2', range=(min(charge_ch2_pc), 25))
    ax2.set_xlabel('Charge (pC)')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Charge Distribution - Channel 2')
    ax2.axvline(x=th_oscilloscope, color="green", label = f'Threshold Oscilloscope={th_oscilloscope}')
    ax2.axvline(x=mean_baseline2, color="red", label = f'Baseline={round(mean_baseline2,3)}')
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()