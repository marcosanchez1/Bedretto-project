import numba
import pandas as pd
import re
import numpy as np
import uproot
from scipy.optimize import least_squares
from numba import njit
from joblib import Parallel, delayed

dt = 0.3125
max_number_samples = 1024

def parse_wavecatcher_dat_file(path):
    events = []
    current_event = None
    current_channel = None

    # Regex patterns
    event_header_re = re.compile(r"=== EVENT (\d+) ===")
    ch_re = re.compile(r"CH:\s*(\d+)\s*EVENTID:\s*(\d+)")
    unix_re = re.compile(r"UnixTime = ([0-9.]+)")

    with open(path, "r") as f:
        for line in f:
            line = line.strip()

            # Detect new event
            m_event = event_header_re.match(line)
            if m_event:
                if current_event is not None:
                    events.append(current_event)

                # Only keep channels → samples
                current_event = {"channels": {}, 'unix_time': None}
                current_channel = None
                continue
            
            # Extract Unix time
            m_unix = unix_re.search(line)
            if m_unix and current_event is not None:
                current_event["unix_time"] = float(m_unix.group(1))
                continue

            # Detect new channel
            m_ch = ch_re.search(line)
            if m_ch and current_event is not None:
                ch_id = int(m_ch.group(1))
                current_event["channels"][ch_id] = []
                current_channel = ch_id
                continue

            # Read waveform samples
            if current_event is not None and current_channel is not None:
                try:
                    nums = [float(x) for x in line.split()]
                    if nums:
                        current_event["channels"][current_channel].extend(nums)
                except ValueError:
                    pass

    # Append last event
    if current_event is not None:
        events.append(current_event)

    # Convert to DataFrame
    df = pd.DataFrame(events)
    return df

def parse_wavecatcher_root_file(path):
    file = uproot.open(path)
    tree = file["wc_events"]

    event_ids = tree["wc_event_id"].array()
    timestamps = tree["midas_timestamp"].array()
    channels = tree["wf_channel"].array()      # vector<int>
    offsets = tree["wf_offset"].array()        # vector<int>
    nsamples = tree["wf_n_samples"].array()    # vector<int>
    samples = tree["wf_samples"].array()       # vector<float> (flat)

    events = []

    for eid, ts, ch_list, off_list, n_list, samp_flat in zip(
        event_ids, timestamps, channels, offsets, nsamples, samples
    ):

        event = {
            "unix_time": float(ts),
            "channels": {}
        }

        # Reconstruct each channel waveform
        for ch, off, n in zip(ch_list, off_list, n_list):
            start = int(off)
            end = start + int(n)
            waveform = samp_flat[start:end]
            event["channels"][int(ch)] = list(map(float, waveform))

        events.append(event)

    return pd.DataFrame(events)

# This functions just receives the input path of the raw data(.dat files) and will return it in the form
# of a df which will have the structure as:
#   channels
#   {0:[samples of channel 0],1:[samples of channel 1]}
# this function's purpose is just to be able to read the original raw data and if needed compare it with
# the fit.
def get_raw_datFile(input_path):
    return (parse_wavecatcher_dat_file(input_path))

# this functions receives the input path of the raw data(.root files) and will return it in the form
# of a df.
def get_raw_rootFile(input_path):
    return (parse_wavecatcher_root_file(input_path))

# This function is just to get the sample number at which we have
# the fraction of the amplitude
def get_t_with_samples(samples, fraction):

    baseline = np.mean(samples[:50])
    peak = np.max(samples)
    peak_position = np.argmax(samples)
    target = (peak - baseline) * fraction + baseline
    
    interval = 50
    idx = np.where(samples[peak_position - interval:peak_position] >= target)[0]#we'll take advantage of the very steep rise of the signal.
    
    if len(idx) == 0:
        return len(samples) # no crossing found return full length
    
    return (idx[0] + (peak_position - interval))*dt

def get_t_with_fit(A, fraction):
    A0, A1, A2, A3, A4, A5, A6 = A
    tp = A1 - (A3*np.sqrt(-np.log(fraction)))/(1 + A2*np.sqrt(-np.log(fraction)))
    return tp

# the fit function that we use for waveforms
@njit
def f(t, A):
    A0, A1, A2, A3, A4, A5, A6 = A
    n = t.size
    F = np.zeros(n)
    eps = 1e-12

    for i in range(n):
        ti = t[i]
        if ti <= A1:
            tl = ti - A1
            denom = 2 * (abs(A2) * tl + A3)**2 + eps
            F[i] = A0 * np.exp(-(tl*tl) / denom) + A6
        else:
            tr = ti - A1
            denom = 2 * (abs(A4) * tr + A5)**2 + eps
            F[i] = A0 * np.exp(-(tr*tr) / denom) + A6
    return F

# This function will perform a fit on the samples of the signal and return the optimized parameters.
def perform_fit_on_samples(t, samples, baseline):

    # amplitude guess works for positive or negative pulses
    A0 = np.max(np.abs(samples - baseline))

    # time of maximum absolute deviation
    A1 = np.argmax(np.abs(samples - baseline)) * dt

    # shape parameters initial guesses
    A2 = 0.01
    A3 = np.abs(A2) * A1
    A4 = 0.01
    A5 = np.abs(A4) * A1
    A6 = baseline

    p0 = np.array([A0, A1, A2, A3, A4, A5, A6], dtype=float)

    # bounds allow negative pulses
    lower = np.array([-2*A0, A1-5, -1, 0, -2, 0, baseline - 2], dtype=float)
    upper = np.array([ 2*A0, A1+5,  1, 10,  2, 10, baseline + 2], dtype=float)

    def residuals(params):
        return f(t, params) - samples

    res = least_squares(
        residuals,
        p0,
        bounds=(lower, upper),
        max_nfev=500,
        method="dogbox"
    )
    return res.x


# This will receive the raw df that we extract from either .dat or .root
# files and perform a fit on each of the events and return a new df with just the
# fit parameters, computations of charge and other things change a lot on each case
# so there's no point on calculating them here.
def perform_fit_on_dataframe(df, n_jobs=-1):
    """
    Parallel version of your dataframe fitting function.
    n_jobs=-1 uses all available CPU cores.
    """

    # Precompute t array once if all waveforms have same length
    # Otherwise compute inside the worker
    sample_length = len(next(iter(df['channels'][0].values())))
    t_global = np.arange(sample_length) * dt

    def fit_single_event(samples):
        """
        Fit all channels for a single event.
        Returns a dict {ch_id: optimized_params}
        """
        row = {}
        for ch_id, ch_samples in samples.items():
            baseline = np.mean(ch_samples[:50])
            optimized_params = perform_fit_on_samples(t_global, ch_samples, baseline)
            row[ch_id] = optimized_params
        return row

    # Parallel execution over events
    results = Parallel(n_jobs=n_jobs, backend="loky")(
        delayed(fit_single_event)(samples)
        for samples in df["channels"]
    )

    # Build final dataframe
    new_df = {
        "channels": results,
        "unix_time": df["unix_time"].tolist()
    }

    return pd.DataFrame(new_df)

def cfd_method(CF, a):

    #tp = a[1] + (a[3] * np.sqrt(-np.log(CF**2)))/(1 - a[2] * np.sqrt(-np.log(CF**2)))
    tm = a[1] - (a[3] * np.sqrt(-np.log(CF**2)))/(1 + a[2] * np.sqrt(-np.log(CF**2)))

    #return tp, tm
    return tm # Accordig to what I saw this is the correct solution.
