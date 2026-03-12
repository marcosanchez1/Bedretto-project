'''
On the paper I got it says that if the event is between a 40ns window it'
can be considered a coincidence, so basically if the peak1 and peak2 are
between the same 40ns window it can be considered that they're the same.

The speed of a muon is very close to the light, so it traverses both detectors
basically in an instant, so the signal should be triggered on both channels 
at the same time.

And I think now I'll just plot or base everything on the filtered data.
'''

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import numpy as np
from scipy.stats import landau

import pandas as pd
import ast

# In this function we're not considering error which is wrong
# but for now I'll just get the landau fit and the momenta 
# of the distribution.
def get_max_peak_and_error(df, channel):
    peaks = []
    for row in df["channels"]:
        #print(row[0]['baseline'])
        peaks.append(max(row[channel]['samples']))
    peaks = np.array(peaks)

    #Plot histogram
    fig, ax = plt.subplots(figsize=(10, 6))
    counts, bins, _ = ax.hist(peaks, bins='auto', alpha=0.5, label='Data', density=False)

    # 3. Fit Landau distribution
    # landau.fit returns (loc, scale)
    loc, scale = landau.fit(peaks)

    # 4. Evaluate fitted PDF
    x = np.linspace(min(peaks), max(peaks), 500)
    pdf = landau.pdf(x, loc=loc, scale=scale)

    # Scale PDF to histogram height
    pdf_scaled = pdf * len(peaks) * (bins[1] - bins[0])

    ax.plot(x, pdf_scaled, 'r-', lw=2, label='Landau fit')

    plt.xlabel("Peak value")
    plt.ylabel("Frequency")
    plt.title(f"Peak distribution — Channel {channel}")
    plt.legend()
    plt.show()

    # 5. Extract MPV (most probable value)
    # For Landau, MPV = loc
    mpv = loc

    # 6. Estimate error on MPV
    # A simple and common choice: sigma / sqrt(N)
    error = scale / np.sqrt(len(peaks))

    return mpv, error

def main():
    Voltage = 56.7
    #window = 40e-9 # in seconds
    window = 40e3 #This would be in ps, no?
    #dt = 312e-12
    dt = 1 # Set this to 1

    df = pd.read_csv(r".\Data\2Bars_2Chs_filtered_data\Run_{}V_Run1_Data_3_3_2026_Ascii.csv".format(Voltage))
    df["channels"] = df["channels"].apply(ast.literal_eval) # Convert string to dict, because our info is stored as string.

    # first I think it would be nice to do a statistical distribution of the peaks.
    # Basically for now I'll just get the mean max peak of each channel, the error of this measurement
    max1,error1 = get_max_peak_and_error(df, 0)
    max2,error2 = get_max_peak_and_error(df, 1)
    print("Channel 1: max peak = {}, Error = {}".format(max1, error1))
    print("Channel 2: max peak = {}, Error = {}".format(max2, error2))


    # Now we'll go through each event and if the max peak of the event
    # is within the window of the mean max peak of the channel, then we
    # can consider it a coincidence AND if the max peak of the two channels
    # are within the same window, then we can consider it a coincidence.
    
    df_coincidences = [] # We'll store the coincidences in this dataframe, so we can plot them later.
    # but we want it to have the same structure as the original df to recycle the code we already built.

    for index, row in df.iterrows():
        # Get the max peak of each channel for the current event
        max_peak_ch1 = np.sum(row["channels"][0]['samples']) if 0 in row["channels"].keys() else 0
        max_peak_ch2 = np.sum(row["channels"][1]['samples']) if 1 in row["channels"].keys() else 0

        # Check if the max peaks are within error
        if (abs(max_peak_ch1 - max1) <= error1) and (abs(max_peak_ch2 - max2) <= error2):
            #Now check x axis or indices to see if they're withing the same window
            #Remember each index is 312ps
            print(abs(np.argmax(row["channels"][0]) - np.argmax(row["channels"][1])))
            if abs(np.argmax(row["channels"][0]) - np.argmax(row["channels"][1])) * dt <= window:
                df_coincidences = df_coincidences.append(row['channels']) # If both conditions are met, we consider it a coincidence and we add it to our new dataframe.

    df = pd.DataFrame(df_coincidences,columns=['channels']) # Now we only have the coincidences in our dataframe, so we can plot them.
    
    if len(df["channels"])==0:
        print('ERROR: NO COINCIDENCES')
        return

    # Sampling period (seconds)
    #dt = 312.5e-12
    dt = 1

    # Prepare figure
    fig, (ax1,ax2) = plt.subplots(2, 1, figsize=(10, 8))

    line1, = ax1.plot([], [], lw=2)
    ax1.set_xlabel("Time (ps)")
    ax1.set_ylabel("Voltage (V)")

    line2, = ax2.plot([], [], lw=2)
    ax2.set_xlabel("Time (ps)")
    ax2.set_ylabel("Voltage (V)")

    # Precompute time axis we're basically gonna look for the list os samples that has the most data
    t = []
    for row in df["channels"]:
        for ch in row.keys():
            if len(row[ch]) > len(t):
                t = np.arange(len(row[ch])) * dt
    # Set axis limits once
    ax1.set_xlim(t[0], t[-1])
    ax2.set_xlim(t[0], t[-1])

    #Now to set the limits of y I'll look for the max value of voltage in all the samples of all the channels and all the events,
    # and the same for the min value, so I can set the limits of y to be the same for all the events and all the channels,
    # so we can compare them better.
    low_limit = 0
    high_limit = 0
    for row in df["channels"]:
        for ch in row.keys():
            low_limit = min(low_limit, min(row[ch]))
            high_limit = max(high_limit, max(row[ch]))

    ax1.set_ylim(low_limit, high_limit)
    ax2.set_ylim(low_limit, high_limit)

    ax1.grid(True)
    ax2.grid(True)

    # Animation update function
    def update(i):

        #Get data for the current event
        samples1 = df["channels"].iloc[i][0]
        t1 = np.arange(len(samples1)) * dt

        samples2 = df["channels"].iloc[i][1]
        t2 = np.arange(len(samples2)) * dt
        
        # Update line data
        line1.set_data(t1, samples1)
        line1.set_label("Filtered signal Ch1")

        line2.set_data(t2, samples2)
        line2.set_label("Filtered signal Ch2")

        ax1.set_title("Waveform Animation - Channel 1 - Event {}".format(i))
        ax2.set_title("Waveform Animation - Channel 2 - Event {}".format(i))

        ax1.legend(loc="upper right")
        ax2.legend(loc="upper right")

        return line1, line2

    # Create animation
    ani = animation.FuncAnimation(fig, update, frames=len(df), interval=50, blit=False)
    plt.show()


if __name__ == "__main__":
    main()