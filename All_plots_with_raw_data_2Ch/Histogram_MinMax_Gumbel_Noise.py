'''
In this script I'll just perform two histograms of the max values of both channels noise parts aka the static line before
the actual muon peaks.

The data structure of the data frames should be something like this:
channels,unix_time
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_0
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_1
{0:[samples_CH0],1:[samples_CH1]},unix_time_event_2
...

'''
import numpy as np
import matplotlib.pyplot as plt
from Functions import rid_of_muon_signal, get_raw_data

from scipy.stats import norm
from scipy.optimize import curve_fit
from scipy.stats import gumbel_r

def max_gaussian_pdf(x, N, mu, sigma, A):
    # Gaussian CDF and PDF
    z = (x - mu) / sigma
    cdf = norm.cdf(z, loc=0, scale=1)
    pdf = norm.pdf(z, loc=0, scale=1)

    # Theoretical PDF of the maximum
    return A * N * (cdf**(N - 1)) * pdf / sigma

def plot_extrema(ax, data, title, N_samples):
    bins = int(round(2 * np.sqrt(len(data)), 0))

    # Histogram (density=True for PDF)
    hist_vals, bin_edges, _ = ax.hist(
        data, bins=bins, density=True, histtype='step', label='Data'
    )

    # Bin centers
    x = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    # Initial guesses
    N0 = N_samples
    sigma0 = np.std(data)
    mu0 = np.mean(data)
    A0 = 1.0

    try:
        popt, pcov = curve_fit(max_gaussian_pdf,
                               x, hist_vals,
                               p0=[N0, mu0, sigma0, A0],
                               maxfev=20000
                               )
        N_fit, mu_fit, sigma_fit, A_fit = popt

        # Fitted curve
        pdf_fit = max_gaussian_pdf(x, N_fit, mu_fit, sigma_fit, A_fit)

        ax.plot(
            x, pdf_fit,
            label=f"Fit: N={N_fit:.1f};mu={mu_fit:.2g};std={sigma_fit:.4g};A={A_fit:.1g}",
            color='red'
        )

    except RuntimeError:
        ax.text(0.5, 0.5, "Fit failed", transform=ax.transAxes,
                ha='center', va='center')

    ax.set_title(title)
    ax.set_xlabel("Value (ADC)")
    ax.set_ylabel("Density")
    ax.grid(True)
    ax.legend()

def main(df, rate, route_figure):
    
    min0, max0, min1, max1 = [], [], [], []
    for row in df['channels']:
        ch0 = np.array(row[0])
        baseline = np.mean(ch0)   # or median
        ch0_corr = ch0 - baseline

        min0.append(-np.min(ch0_corr))
        max0.append(np.max(ch0_corr))

        ch1 = np.array(row[1])
        baseline = np.mean(ch1)   # or median
        ch1_corr = ch1 - baseline

        min1.append(-np.min(ch1_corr))
        max1.append(np.max(ch1_corr))
    # Convert to arrays
    min0 = np.array(min0)
    max0 = np.array(max0)
    min1 = np.array(min1)
    max1 = np.array(max1)

    fig, ax = plt.subplots(2, 2, figsize=(10, 6))
    ax0, ax1, ax2, ax3 = ax.flatten()

    # Number of samples per waveform
    N_samples = len(df['channels'].iloc[0][0])

    # Apply to both channels
    plot_extrema(ax0, min0, f"CH0 Min (rate={rate} Hz)", N_samples)
    plot_extrema(ax1, max0, f"CH0 Max (rate={rate} Hz)", N_samples)
    plot_extrema(ax2, min1, f"CH1 Min (rate={rate} Hz)", N_samples)
    plot_extrema(ax3, max1, f"CH1 Max (rate={rate} Hz)", N_samples)

    plt.tight_layout()
    plt.savefig(f"{route_figure}\\GumbelFit_MinMax_Noise.png")
    plt.show()
    plt.close()

if __name__ == "__main__":

    voltage = '57'
    run = '5'
    day = '15'
    month = '4'

    #route of folder where to save the figures
    route_figure = fr".\All_plots_with_raw_data\Plots\1Bar_2Chs\Tests"

    # route of original data, will only use it to compare with the fit and discriminate events
    route_data = f".\\Data\\Raw_data\\1Bar_2Chs\\Run_{voltage}V_Run{run}_Data_{month}_{day}_2026_Ascii.dat"
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