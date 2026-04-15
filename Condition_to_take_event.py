# This script will just contain the conditions for selecting or discriminating events, I did just one script for this 
# because I have several scripts basically running with the same data just doing different plots and I guess it's
# easier to just do a separate script that contains the conditions and all of them use it.

import pandas as pd


def discriminated_df(df, trigger)->pd.DataFrame:
    # Here we can add some conditions to select or discriminate events, it can be based, on raise time or charge or whatever.
    # For example, we can select only events with a charge above a certain threshold in channel 0 and a charge below a certain threshold in channel 1.
    # This is just an example, you can modify the conditions as you see fit.
    
    # Example condition: select events with charge above 0.5 V*ns in channel 0 and below 0.5 V*ns in channel 1.
    threshold_ch0 = trigger 
    threshold_ch1 = trigger*(6/5)
    
    # We'll use as reference the amplitude of the signal aka A0. For example this condition takes events were A0
    # of channel 0 is above the trigger and A0 of channel 1 is above a certain value that we'll modify.
    new_df = df[(df['channels'].apply(lambda row: row[0]['fit_parameters'][0] >= threshold_ch0)) & 
                         (df['channels'].apply(lambda row: row[1]['fit_parameters'][0] >= threshold_ch1))]
    
    return new_df