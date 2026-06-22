import pandas as pd
import re
import numpy as np
import uproot

dt = 0.3125
def parse_wavecatcher_file(path):
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

def parse_wavecatcher_root(path):
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
    return (parse_wavecatcher_file(input_path))

def get_raw_rootFile(input_path):
    return (parse_wavecatcher_root(input_path))

# Function to get rid of the "real" signal or the muon signal on the raw_data and return
# just the noise.
# Basically the algorithm that I'll follow is, find the peak of the signal, before the peak
# find the time at 10% of the peak, then we'll return only from 0 to this value, maybe even take like 
# 30 samples less or something like that.
def rid_of_muon_signal(df)->pd.DataFrame:

    new_df = {'channels':[], 'unix_time':[]}
    for samples, unix_time in zip(df['channels'],df['unix_time']):
        row = {}

        cut0 = 640 #get_t(samples[0],0.1) # 640 corresponds to 200ns (200ns/0.3125ns = 640 samples)
        cut1 = 640 #get_t(samples[1],0.1) # I noticed that we just need to cut until this point to get rid of muon signal
        
        row[0] = samples[0][:cut0]
        row[1] = samples[1][:cut1]

        # Plotting the position in time of the max values I realized that I should cut from 200ns onward
        # so I'll add a condition here to cut these values.
        limit = int(round(200/dt,0))
        if len(row[0]) > limit:
            row[0] = row[0][:limit]
        if len(row[1]) > limit:
            row[1] = row[1][:limit]

        new_df["channels"].append(row)
        new_df["unix_time"].append(unix_time)

    return pd.DataFrame(new_df)

# This function is just to get the sample number at which we have
# the fraction of the amplitude
def get_t(samples, fraction):

    baseline = np.mean(samples[:50])
    peak = np.max(samples)
    peak_position = np.argmax(samples)
    target = (peak - baseline) * fraction + baseline
    
    interval = 200
    idx = np.where(samples[peak_position - interval:peak_position] >= target)[0]#we'll take advantage of the very steep rise of the signal.
    
    if len(idx) == 0:
        return len(samples) # no crossing found return full length
    
    return idx[0] + (peak_position - interval)