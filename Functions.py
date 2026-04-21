import pandas as pd
import re
import numpy as np

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

# This functions just receives the input path of the raw data(.dat files) and will return it in the form
# of a df which will have the structure as:
#   channels
#   {0:[samples of channel 0],1:[samples of channel 1]}
# this function's purpose is just to be able to read the original raw data and if needed compare it with
# the fit.
def get_raw_data(input_path):
    return (parse_wavecatcher_file(input_path))

# Function to discriminate events
def discriminated_df(df, trigger)->pd.DataFrame:
    # Here we can add some conditions to select or discriminate events, it can be based, on raise time or charge or whatever.
    # For example, we can select only events with a charge above a certain threshold in channel 0 and a charge below a certain threshold in channel 1.
    # This is just an example, you can modify the conditions as you see fit.
    
    # Example condition: select events with charge above 0.5 V*ns in channel 0 and below 0.5 V*ns in channel 1.
    threshold_ch0 = trigger * 1
    threshold_ch1 = trigger * 0
    
    # We'll use as reference the amplitude of the signal aka A0. For example this condition takes events were A0
    # of channel 0 is above the trigger and A0 of channel 1 is above a certain value that we'll modify.
    new_df = df[(df['channels'].apply(lambda row: row[0]['fit_parameters'][0] >= threshold_ch0)) & 
                         (df['channels'].apply(lambda row: row[1]['fit_parameters'][0] >= threshold_ch1))]
    
    # Basically this region of rise time where it's flat
    new_df = new_df[new_df['channels'].apply(lambda row: np.abs(row[0]['t_10']-row[1]['t_10']) <= 2.5)]

    return new_df
def status(A_CH0, A_CH1, samples_CH0, samples_CH1):
    dt = 0.3125
    max_number_samples = 1024

    if A_CH0[1] <= 0 or A_CH0[1] >= max_number_samples*dt: # It cannot be outside this interval not possible
        return False
    
    # The position of the peak is not possible for it to be
    if A_CH1[1] <= 0 or A_CH1[1] >= max_number_samples * dt: # It cannot be outside this interval not possible
        return False
    
    # the bar's length is 169.8cm and the speed of light inside the material is about 16cm/ns
    # meaning that if the signal is "good" it shouldn't be more than like 11ns
    if abs(A_CH0[1] - A_CH1[1]) > 11:
        return False

    return True

# The idea of this function is to compare some elements such as amplitude of the fit
# with the original data and in this way discriminate the events that may not have a
# good fit.
def compare_df(df_fit, df_raw):
    # We assume they're of the same size
    rows = []
    for i in range(len(df_fit['channels'])):
        A_CH0 = df_fit['channels'].iloc[i][0]['fit_parameters']
        samples_CH0 = df_raw['channels'].iloc[i][0]

        A_CH1 = df_fit['channels'].iloc[i][1]['fit_parameters']
        samples_CH1 = df_raw['channels'].iloc[i][1]

        status_fit = status(A_CH0, A_CH1, samples_CH0, samples_CH1)

        if status_fit:
            rows.append(df_fit.iloc[i])

    # Build new DataFrame from accepted rows
    new_df = pd.DataFrame(rows).reset_index(drop=True)
    return new_df

    
