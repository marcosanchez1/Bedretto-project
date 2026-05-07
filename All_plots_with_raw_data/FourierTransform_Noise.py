'''
In this script I'll just perform the fourier transform on the noise of the signal, to see if we can distinguish the frequencies of the two noise sources that
we're suspecting we have.

The data structure of the data frames should be something like this:

'channels','unix_time'
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_0
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_1
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_2
...

'''
import numpy as np
import matplotlib.pyplot as plt
from Functions import rid_of_muon_signal, get_raw_data

def main(df, rate, route_figure):

    # --- Extract noise waveforms ---
    ch0_list = []
    ch1_list = []

    for row in df['channels']:
        ch0 = np.array(row[0])
        ch1 = np.array(row[1])

        # baseline correction
        ch0 = ch0 - np.mean(ch0)
        ch1 = ch1 - np.mean(ch1)

        ch0_list.append(ch0)
        ch1_list.append(ch1)

    ch0_arr = np.array(ch0_list)
    ch1_arr = np.array(ch1_list)

    # --- Sampling information ---
    # sampling interval of your oscilloscope
    dt = 312.5e-12   # 312 ps = 0.312 ns = 0.312e-9 s

    N = ch0_arr.shape[1]  # number of samples per waveform it should be like 641 or a bit less but not more.
    freqs = np.fft.rfftfreq(N, dt) # frequencies corresponding to the FFT bins
    freqs = freqs/1e6 # convert to MHz for better readability

    # --- Compute FFT magnitude ---
    fft0 = np.fft.rfft(ch0_arr, axis=1)
    fft1 = np.fft.rfft(ch1_arr, axis=1)

    # Power spectral density (averaged)
    psd0 = np.mean(np.abs(fft0)**2, axis=0)
    psd1 = np.mean(np.abs(fft1)**2, axis=0)

    # --- Plot ---
    plt.figure(figsize=(10,6))
    plt.loglog(freqs, psd0, label="CH0 PSD")
    plt.loglog(freqs, psd1, label="CH1 PSD")

    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Power Spectral Density(ADC^2/Hz)")
    plt.title("Average Noise FFT (after muon removal)")
    plt.grid(True, which="both", ls="--")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{route_figure}\\FFT_Noise.png")
    plt.show()
    plt.close()


if __name__ == "__main__":

    voltage = '0.005'
    run = '7'
    day = '5'
    month = '5'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_raw_data\Plots\1Bar_2Chs\57Vcoincidence\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = fr".\Data\Raw_data\1Bar_2Chs\57Vcoincidence\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
    df = get_raw_data(route_data)

    # compute rate
    RATE = len(df['unix_time'])/(df['unix_time'].iloc[-1] - df['unix_time'].iloc[0])
    RATE = int(round(RATE, 0))

    # With this function we get rid of muon peaks in both channels and we're left with only the "static" part
    # of the signal, it's working well just take into account that on the last few samples I'm taking about 10%
    # of the muon peak, so we should see a bit of bias here.
    df = rid_of_muon_signal(df)

    main(df, RATE, route_figure)
    
    print("\nEnd of execution.\n")