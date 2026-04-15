import pandas as pd
import re

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

def discriminated_df(df, trigger)->pd.DataFrame:
    # Here we can add some conditions to select or discriminate events, it can be based, on raise time or charge or whatever.
    # For example, we can select only events with a charge above a certain threshold in channel 0 and a charge below a certain threshold in channel 1.
    # This is just an example, you can modify the conditions as you see fit.
    
    # Example condition: select events with charge above 0.5 V*ns in channel 0 and below 0.5 V*ns in channel 1.
    threshold_ch0 = trigger 
    threshold_ch1 = trigger*(0/2)
    
    # We'll use as reference the amplitude of the signal aka A0. For example this condition takes events were A0
    # of channel 0 is above the trigger and A0 of channel 1 is above a certain value that we'll modify.
    new_df = df[(df['channels'].apply(lambda row: row[0]['fit_parameters'][0] >= threshold_ch0)) & 
                         (df['channels'].apply(lambda row: row[1]['fit_parameters'][0] >= threshold_ch1))]
    
    return new_df