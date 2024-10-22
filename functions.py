import math
from typing import List, Any
from dataclasses import dataclass
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

DT = 5*10 ** -5

@dataclass 
class Peaks: 
    start: float
    step: float
    interval: float
    num_intervals: int

@dataclass 
class Selection: 
    start: int 
    end: int 
    calc_avrg: bool 

@dataclass 
class Scalebar: 
    show: bool 
    hide_ticks: bool 
    ysize: int|None
    xsize: int|None

def avrg(flat_lists: List[List[float]]) -> List[float]:
    return [sum([x[i] for x in flat_lists])/len([x[i] for x in flat_lists]) for i in range(len(flat_lists[0]))]

def calc_time_from_sweeps(sweeps: List[List[float]]) -> float: 
    return len(sweeps[0]) * DT

def get_only_peaks(peaks):
    """ 
    Removes all NaN values from peaks and peaks which are too close.
    """
    reduced_peaks = []
    for i, peak in enumerate(peaks):
        # Add to reduced peaks, if not nan or index of last value is <100 smaller than current.
        if not math.isnan(peak) and (len(reduced_peaks) == 0 or i-reduced_peaks[-1][0] > 100):
            reduced_peaks.append([i, i*DT, peak])
    return reduced_peaks

def alternate_min_max(min_peaks, max_peaks):
    last_was_min = False
    for i in range(len(min_peaks)):
        if not math.isnan(min_peaks[i]):
            if last_was_min == True:
                min_peaks[i] = math.nan
            last_was_min = True
        if not math.isnan(max_peaks[i]):
            if last_was_min == False:
                max_peaks[i] = math.nan
            last_was_min = False
    return min_peaks, max_peaks

def peaks_as_table(max_peaks, min_peaks) -> List[List[Any]]:
    max_peaks = get_only_peaks(max_peaks)
    min_peaks = get_only_peaks(min_peaks)
    rows = [["index", "time", "min", "index", "time", "max", "amp"]]
    # Create rows
    for i in range(len(max_peaks)):
        row = []
        row += min_peaks[i] if i < len(min_peaks) else [math.nan, math.nan, math.nan]
        row += max_peaks[i] if i < len(max_peaks) else [math.nan, math.nan, math.nan]
        if i < len(min_peaks) and i < len(max_peaks): 
            row.append(max_peaks[i][2]-min_peaks[i][2])
        else: 
            row.append(math.nan)
        rows.append(row)
    return rows

# change epsilon to determmin number of peaks (for large data use ~25, for small use 1)
def get_peaks_in_range(xs, comp, epsilon=25):
    # Create data-frame with given values
    df = pd.DataFrame(xs, columns=['data'])
    # calculate number of data-points to evaluate
    n = int(len(xs) / epsilon)
    # get peaks
    df['peaks'] = df.iloc[argrelextrema(df.data.values, comp,
                        order=n)[0]]['data']
    # Convert to list of peaks and ignore values below average
    peaks = []
    average = sum(xs)/len(xs)
    for i in range(len(df['peaks'])):
        if comp(df['peaks'][i], average):
           peaks.append(df['peaks'][i]) 
        else:
           peaks.append(math.nan)
    return peaks

def get_peaks(xs, peaks_info: Peaks, comp):
    # convert seconds to index
    start = int(peaks_info.start*len(xs)/2)
    step = int(peaks_info.step*len(xs)/2)
    interval = int(peaks_info.interval*len(xs)/2)
    # fill values up to first data-point with nans
    peaks = [math.nan for _ in range(start-(step-interval))]
    counter = 0
    for i in range(start, len(xs), step):
        # fill with nans
        peaks = peaks + [math.nan for _ in range(len(peaks), i)]
        # make sure bounds are not exceeded, then get peeks
        if len(xs) > i+interval:
            peaks = peaks + get_peaks_in_range(xs[i:(i+interval)], comp, 1)
        # stop after first 'num_intervals' datapoints
        counter += 1
        if counter == peaks_info.num_intervals:
            break
    peaks = peaks + [math.nan for _ in range(len(peaks), len(xs))]
    print(f"get_peaks with: {start}, {step},{interval},found {len(get_only_peaks(peaks))} peaks.")
    return peaks


