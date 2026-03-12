'''
In this version I'll save several figures because I'll apply a second threshold
to try and fitler out the noise and get the fingerplot, but I'll try with 
several different values.
'''

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ast

def main():
    voltage = 60
    trigger_oscilloscope = -0.99
    #dt = 312e-12 #to get it in units of s
    dt = 1 #in units of ps
    
    df = pd.read_csv(r".\Data\1Bar_2Chs_filtered_data\Run_{}V_Run0_Data_3_10_2026_Ascii.csv".format(voltage))
    df["channels"] = df["channels"].apply(ast.literal_eval)

    #For this particualr case I observed that the maximum voltage is 0.4 so in the last
    # graph we should observe literally nothing.
    threshold = [trigger_oscilloscope*i for i in range(1,2)]

    for th in threshold:
        # Aggregate charge_pC from all processed CSV files
        charge_ch1 = []
        charge_ch2 = []

        max_v1 = []
        max_v2 = []

        mean_baseline1 = []
        mean_baseline2 = []

        # Integrate the signal to get charge
        for index, row in df.iterrows():
            # First get data for channel 1.
            samples_ch1 = row['channels'][0]['samples']
            baseline1 = row['channels'][0]['baseline']

            max1 = np.max(samples_ch1) #max voltage of present signal. It has to be before the next line because we want the
            # max value of the signal, not max difference between baseline and signal.
            samples_ch1 = [samples_ch1[i] - baseline1 for i in range(len(samples_ch1))] #We take into consideration the baseline.
            charge1 = np.sum(samples_ch1) * dt # This would the charge and should be proportional to number of photons

            # Now let's get the data for channel 2
            samples_ch2 = row['channels'][1]['samples']
            baseline2 = row['channels'][1]['baseline']
            
            max2 = np.max(samples_ch2)* dt
            samples_ch2 = [samples_ch2[i] - baseline2 for i in range(len(samples_ch2))]
            charge2 = np.sum(samples_ch2)* dt # This would be strictly the integral
            
            # Only if the signal/charge is above orequal to threshold, and both signals have to be above
            # this threshold in order to say "we have a coincidence"
            if max1 >= th and max2 >= th:
                charge_ch1.append(charge1)
                mean_baseline1.append(baseline1)
                max_v1.append(max1)

                charge_ch2.append(charge2)
                mean_baseline2.append(baseline2)
                max_v2.append(max2)

        mean_baseline1 = np.mean(mean_baseline1)
        mean_baseline2 = np.mean(mean_baseline2)

        # Now just plot the charge distribution
        fig, axs = plt.subplots(2, 2, figsize=(10, 8))
        ax1, ax2, ax3, ax4 = axs.flatten()

        n = 1

        n_bins = int( round( np.sqrt(len(charge_ch1)) ,0) )
        n_bins = n * n_bins
        ax1.hist(charge_ch1, bins=n*n_bins, alpha=0.7, label=f'bins={n_bins}')
        #ax1.hist(charge_ch1, bins=n_bins, alpha=0.7, label=f'Channel 1-bins={n_bins}', range=(min(charge_ch1),20))
        ax1.set_xlabel('Charge (pC)')
        ax1.set_ylabel('Frequency')
        ax1.set_title(f'Charge Distribution-Channel_1-Samples={len(charge_ch1)}')
        ax1.legend()
        ax1.grid(True)

        n_bins = int( round( np.sqrt(len(max_v1)) ,0) )
        n_bins = n * n_bins
        ax3.hist(max_v1, bins=n_bins, alpha=0.7, label=f'bins={n_bins}')
        ax3.set_xlabel('Voltage (V)')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Max.Voltage Distribution-Channel_1')
        ax3.axvline(x=trigger_oscilloscope, color="green", label = f'Threshold Oscilloscope={trigger_oscilloscope}')
        #ax3.axvline(x=mean_baseline1, color="red", label = f'Baseline={round(mean_baseline1,3)}')
        ax3.axvline(x=th, color="orange", label = f'2nd Threshold={round(th,4)}')
        ax3.legend()
        ax3.grid(True)
        
        n_bins = int( round( np.sqrt(len(charge_ch2)) ,0) )
        n_bins = n * n_bins
        ax2.hist(charge_ch2, bins=n_bins, alpha=0.7, label=f'bins={n_bins}')
        #ax2.hist(charge_ch2, bins=n_bins, alpha=0.7, label=f'Channel 2-bins={n_bins}', range=(min(charge_ch2), 25))
        ax2.set_xlabel('Charge (pC)')
        ax2.set_ylabel('Frequency')
        ax2.set_title(f'Charge Distribution-Channel_2-Samples={len(charge_ch2)}')
        ax2.grid(True)
        ax2.legend()

        n_bins = int( round( np.sqrt(len(max_v2)) ,0) )
        n_bins = n * n_bins
        ax4.hist(max_v2, bins=n_bins, alpha=0.7, label=f'bins={n_bins}')
        ax4.set_xlabel('Voltage (V)')
        ax4.set_ylabel('Frequency')
        ax4.set_title('Max.Voltage Distribution-Channel_2')
        ax4.axvline(x=trigger_oscilloscope, color="green", label = f'Threshold Oscilloscope={trigger_oscilloscope}')
        #ax4.axvline(x=mean_baseline2, color="red", label = f'Baseline={round(mean_baseline2,3)}')
        ax4.axvline(x=th, color="orange", label = f'2nd Threshold={round(th,4)}')
        ax4.legend()
        ax4.grid(True)

        plt.tight_layout()
        plt.savefig(f".\\Photos_of_charge_distributions_1Bar_2Ch_2ndThreshold\\{voltage}V_{int(th/trigger_oscilloscope)}_Threshold_{round(th,4)}.png")
        print(f'\n Finished with threshold: {round(th,4)}')
        plt.show()

    print('\n End of execution. \n')

if __name__ == "__main__":
    main()