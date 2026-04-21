# The aim of this script is to unify and re-organize everything I've done until this
# point(01/04/2026) on the project.

# So basically what I'm aiming to do in this script is:
# 1. Say we have some folder inside Data\Raw_data, that we already have it's direction,
#    that contains raw data in the form of .dat files which is what wavecatcher is
#    giving us
# 2. And say we have another file inside Data\Processed_data with the same name but empty
#    where we'll deposit the end result of this script
# 3. This script what will do is take all .dat files of the raw file we'll extract the
#    wave form perform the fitting that we already know, perform the integral and in the
#    processed data file we'll only take the A0,A1,A2,...,A6 parameters of each
#    channel, their respective integral/charge, the time at 10% of the signal and at 90%
#    and save them in the form of a csv file.
#    3.1. I'm thinking that that I'll keep the format I've been working on for the end result
#         of the csv, which is soemthing like
#     
#     channel,unix_time
#     {0:{fitting_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90},1:{0:{fitting_parameters:[A0,A1,...],charge:charge_0,t_10: t_10,t_90:t_90}},unix_time_0
#         
#         Notice that in the column channel we're saving dictionaries we're gonna have N
#         dictionaries for N events. Say we have event i, the dictionary has two keys(I'll make
#         it so it can have m keys for m channels) 0 and 1, and in each key we'll have their
#         respective fitting parameters and charge.
#         We keep unix_time because it helps us compute the rate, in theory we only need the
#         last and first value of unix_time column but I don't se how we can do this, so I'll
#         just keep it.

#  NOTES OF MK2 VERSION: The only difference is that I'll try to implement some parallel processing to try and make this
#  faster. The integral is of only the exponencial part of the function I substract A6 before integrating. And, I'll
#  perform the integration until 100% of the amplitude, maybe we should take even less.
#  Also, I noticed that for low signals we were having some issues: 1) t_90 was giving nan values but t_10 was always good
#  so I put a condition that if it's nan then just take t_90=A1 which is not correct but at least for now I think will do
#  2) when low signals happened, to be precise max < 0.02 before I was taking these signals as just zero, but it's not okay
#  there were some relevant events that I was taking incorrectly so now I'm always performing the fit no matter what.

import pandas as pd
import re
import os
import numpy as np
import time
from scipy.optimize import least_squares
from numba import njit
import scipy.integrate as integrate
from multiprocessing import Pool, cpu_count

# This dt is the time spacing between samples, we multiply the sample number by this
# to know the position in time of the sample.
dt = 0.312 # multiply by this to get it in ns, in the software it just says 312ps not 312.5ps.

# We will perform the fit until peak + 30 samples more,
WINDOW = 30 * dt

# At least for the first approximation of the baseline we say it's the average of the first
# 100 samples.
baseline_window = 20

# This are the folder routes that we want to process and then store the data.
# Notice that the route is practically the same except for the second direction
#raw_folder = r".\Data\Raw_data\1Bar_2Chs\57V_varying_gatelength_and_trigger_only"
#processed_folder = r".\Data\Processed_data\1Bar_2Chs\57V_varying_gatelength_and_trigger_only"
raw_folder = r".\Data\Raw_data\1Bar_2Chs"
processed_folder = r".\Data\Processed_data\1Bar_2Chs"




#________________________________________FUNCTIONS______________________________________________
def process_channel_waveform(args):
    """Standalone function for multiprocessing."""
    ev_index, ch_id, samples = args
    try:
        params = process_samples(samples)
        charge = integral(params)
        return ev_index, ch_id, params, charge
    except Exception:
        return ev_index, ch_id, None, None
    
def parse_wavecatcher_file(path):
    events = []
    current_event = None
    current_channel = None

    # Regex patterns
    event_header_re = re.compile(r"=== EVENT (\d+) ===")
    unix_re = re.compile(r"UnixTime = ([0-9.]+)")
    ch_re = re.compile(
        r"CH:\s*(\d+)\s*EVENTID:\s*(\d+).*?"
        r"Baseline:\s*([0-9.\-]+)\s*V\s*"
        r"Amplitude:\s*([0-9.\-]+)\s*V\s*"
        r"Charge:\s*([0-9.\-]+)"
    )

    with open(path, "r") as f:
        for line in f:
            line = line.strip()

            # Detect new event
            m_event = event_header_re.match(line)
            if m_event:
                # Save previous event
                if current_event is not None:
                    events.append(current_event)

                current_event = {
                    "unix_time": None,
                    "channels": {}
                }
                current_channel = None
                continue

            # Extract Unix time
            m_unix = unix_re.search(line)
            if m_unix and current_event is not None:
                current_event["unix_time"] = float(m_unix.group(1))
                continue

            # Detect new channel block
            m_ch = ch_re.search(line)
            if m_ch and current_event is not None:
                ch_id = int(m_ch.group(1))

                # Samples is the only one that we save temporarily, the rest of info we'll store in csv files
                # this info was requested to be saved by prof.
                current_event["channels"][ch_id] = {
                    "_samples": [],
                    "fit_parameters": None,
                    "charge": None,
                    "t_10": None, # Time when signal is at 10% of its amplitude
                    "t_90": None
                }

                current_channel = ch_id
                continue

            # Read waveform samples
            if current_event is not None and current_channel is not None:
                try:
                    nums = [float(x) for x in line.split()]
                    if nums:
                        current_event["channels"][current_channel]["_samples"].extend(nums)
                except ValueError:
                    pass

    # Append last event
    if current_event is not None:
        events.append(current_event)

    # === PARALLEL PROCESSING OF CHANNELS ===
    tasks = []
    for ev_index, ev in enumerate(events):
        for ch_id, ch_data in ev["channels"].items():
            samples = ch_data["_samples"]
            tasks.append((ev_index, ch_id, samples))

    # Run fits in parallel
    with Pool(cpu_count()) as pool:
        results = pool.map(process_channel_waveform, tasks)

    # Assign results back into events
    for ev_index, ch_id, params, charge in results:
        if params is not None:
            A = params.tolist()
            charge = float(charge)
            t_10 = get_t(params, 0.1)
            t_90 = get_t(params, 0.9)

            events[ev_index]["channels"][ch_id]["fit_parameters"] = A
            events[ev_index]["channels"][ch_id]["charge"] = charge
            events[ev_index]["channels"][ch_id]['t_10'] = t_10
            if t_90 is not None and not np.isnan(t_90):
                events[ev_index]["channels"][ch_id]['t_90'] = t_90
            else:
                # For what I saw with the files that I processed and correcting the get_t by writing the
                # 3000 values, it entered for just three event which is good.
                events[ev_index]["channels"][ch_id]['t_90'] = A[1]
                # I think this is a good solution because it will return nan in the cases where the signal,
                # is very weak or there's not even a signal, meaning it's like a straight line and how do you
                # define the 90% of a line? you can't, so the closest we can define the 90% of a line or
                # something barely a line is with the 100% there is virtually no difference in this cases.
        else:
            # it never went into this condition but just in case.
            events[ev_index]["channels"][ch_id]["fit_parameters"] = None
            events[ev_index]["channels"][ch_id]["charge"] = None
            events[ev_index]["channels"][ch_id]['t_10'] = None
            events[ev_index]["channels"][ch_id]['t_90'] = None

        del events[ev_index]["channels"][ch_id]["_samples"]

    # Convert to DataFrame
    df = pd.DataFrame(events)
    return df

def process_samples(samples):
    samples_np = np.asarray(samples, dtype=float)

    baseline = fast_baseline(samples_np)
    max_index = np.argmax(samples_np)
    
    #end = max_index + WINDOW
    end = min(len(samples_np), max_index + int(round(WINDOW/dt,0)))

    t = np.arange(end) * dt # This to convert it to time in ns

    # It would be a good idea to check if the fit was performed correctly.
    params = perform_fit(t, samples_np[:end], baseline)
    
    return params

@njit
def fast_baseline(samples_np):
    s = 0.0
    for i in range(baseline_window):
        s += samples_np[i]
    return s / baseline_window

def perform_fit(t, samples, baseline):
    # initial guess
    A0 = np.max(samples) - baseline # Adding this -baseline term, gets us the pure amplitude without offset.
    A1 = np.argmax(samples) * dt # to convert it into ns.
    A2 = 0.01
    A3 = np.abs(A2) * A1
    A4 = 0.01
    A5 = np.abs(A4) * A1
    A6 = baseline

    p0 = np.array([A0, A1, A2, A3, A4, A5, A6], dtype=float)

    # Let's try to fit for a WINDOW = 30
    lower = np.array([A0*0.1, A1-5, -0.5,  0, -0.5,  0, A6 - 0.7], dtype=float)
    upper = np.array([A0*2  , A1+5,  0.5, 20,  0.5, 20, A6 + 0.7], dtype=float)


    def residuals(params):
        return f(t, params) - samples

    #changed curve fit for least squares method., it's supposed to be faster, but didn't give good results
    res = least_squares(residuals,p0,bounds=(lower, upper),max_nfev=5000,method="trf")

    popt = res.x #This is the list of optimized parameters

    return popt  # [A0..A6] This is for the least_squares part

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

def integral(parameters):

    A1 = parameters[1]
    A6 = parameters[6]
    ti = 0
    tf = A1 # The fit is performed until A1 + WINDOW but here we'll integrate until A1.
    
    # Due to the fact that f takes a numpy list of t and returns a list of f, since
    # in this case we needed a 1:1 function. We just give a list with 1 value and will
    # return a list with one value and we just work with that.
    integral = integrate.quad(lambda t: f(np.array([t]), parameters)[0] - A6, ti, tf)
    # Notice that we substract A6 from the function and not after integration, should be
    # the same, but I'll do it this way.


    # Substracting this last term is equivalent to removing the baseline contribution to the integral.
    return (integral[0]) # integral = (value,error)

# We receive the parameters A[i] and fraction is the porcentage of amplitude we wish
# to find the time of, basically we wish to find t sucha that f(t_i) = Amplitude * fraction.
def get_t(A, fraction):
    A0, A1, A2, A3, A4, A5, A6 = A

    # Build a time axis from 0 to peak+WINDOW
    t = np.linspace(0, A1 + WINDOW, 3000)

    # Evaluate waveform
    y = f(t,A)

    # Target level
    target = A0*fraction + A6

    # Find first crossing
    idx = np.where(y >= target)[0]
    if len(idx) == 0:
        return np.nan  # No crossing found
    
     # this would be in ns
    return t[idx[0]] #returns nan if no crossing found.

#________________________________________MAIN______________________________________________
def main():

    # Loop through all .dat files in the raw folder
    for filename in os.listdir(raw_folder):

        # This makes sure that we only read the .dat files
        if filename.lower().endswith(".dat"):
            
            # We'll just declare this to measure how much it takes to process one file
            ti = time.time()

            # We just get the full route to the file we're currently processing.
            input_path = os.path.join(raw_folder, filename)

            # we pass the route to the function parse_wavecatcher_file and will
            # return the df.
            df = parse_wavecatcher_file(input_path)

            # Output filenames
            base = os.path.splitext(filename)[0]

            # rout + name of the output csv file we'll save
            out_csv = os.path.join(processed_folder, base + ".csv")

            # We save the df in the csv file route declared before.
            df.to_csv(out_csv, index=False)

            # File finished processing we save this time
            tf = time.time()


            print(f'File finished: {out_csv} in {tf - ti:.1f}s')

    print("\nAll files processed.")

    return None

#________________________________________EXECUTE ONLY IF MAIN______________________________________________
if __name__ == '__main__':
    main()