import json
import os
import os.path
import math
import numpy as np
from pprint import pformat
import statistics
import click
import pandas as pd
from matplotlib import pyplot as plt
from igor.binarywave import load as loadibw
from scipy.signal import argrelextrema

DT = 5*10 ** -5

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
                print ("removed min peak")
            last_was_min = True
        if not math.isnan(max_peaks[i]):
            if last_was_min == False:
                max_peaks[i] = math.nan
                print ("removed max peak")
            last_was_min = False
    return min_peaks, max_peaks



def peaks_to_dataframe(max_peaks, min_peaks):
    rows = []
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
    df = pd.DataFrame(np.array(rows), columns=["index", "time", "min", "index", "time", "max", "amp"])
    return df

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

def get_peaks(xs, start, step, interval, num_intervals, comp):
    # convert seconds to index
    start = int(start*len(xs)/2)
    step = int(step*len(xs)/2)
    interval = int(interval*len(xs)/2)
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
        if counter == num_intervals:
            break
    peaks = peaks + [math.nan for _ in range(len(peaks), len(xs))]
    print(f"get_peaks with: {start}, {step},{interval},found {len(get_only_peaks(peaks))} peaks.")
    return peaks

def extract_data(path):
    data = loadibw(path)
    wave = data['wave']
    values = np.nan_to_num(wave['wData']).tolist()
    del data['wave']['wData']
    return (data, values)

def store_data(path, data, values): 
    path = path.replace('ibw', '')
    path = path.replace('input', 'output')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = pformat(data).splitlines()            
    with open(f'{path}.txt', 'w') as writer: 
        writer.writelines([line + "\n" for line in lines])
        # json.dump(data, writer, indent=4)
    with open(f'{path}.json', 'w') as writer:
        json.dump(values, writer, indent=4)

def plot_data(values, total_time, path, min_peaks=None, max_peaks=None, df=None, list2=None):  
    listxachs=np.linspace(0, total_time, len(values)) 
    # Plot peaks, if set
    if min_peaks is not None:
        plt.scatter(listxachs, min_peaks, c='b')
    if max_peaks is not None:
        plt.scatter(listxachs, max_peaks, c='b')
    plt.plot(listxachs, values, linewidth=0.3, color="red")
    # Plot second list if set
    if list2 is not None:
        plt.plot(listxachs, list2, linewidth=0.3, color="red", label="last")
    plt.xlabel("Time [minutes]",
            family = 'serif',
            color='black',
            weight = 'normal',
            size = 10,
            labelpad = 5)
    plt.ylabel("Voltage [mV]",
            family = 'serif',
            color='black',
            weight = 'normal',
            size = 10,
            labelpad = 5)

      
    # Store figure
    path = path.replace('input','output')  # input, ouput = foldernames
    path = path.replace('ibw','svg')
    plt.savefig(f'{path}',format='svg')    # only if you want to safe it
    # Store df (peaks)
    if df is not None:
        path = path.replace('svg','csv')
        df.to_csv(path)
    # Show plot
    plt.show()


@click.command()
@click.option('--path', help='specify the path and filename: "Data/<date>/<filename>"')
@click.option('--plot', default=True, help='show plot')
@click.option('--store', default=True, help='store data: stores complete data as txt and values as json.')
@click.option('--joined', help='join lists')
@click.option('--start', help='join lists', default=0.2)
@click.option('--step', help='join lists', default=0.1)
@click.option('--interval', help='join lists', default=0.02)
def run(path, plot, store, joined, start, step, interval):
    # Extract complete data and values 
    data, values = extract_data(path)

    # Print type of data to plot (stacked, in_a_row, first_last, average)
    print("joined: ", joined)
    
    # Get number of stacks, datapoints per stack and time
    stacks = len(values[0])
    datapoints = len(values)
    time = datapoints * DT
    print(f"Number of stacks: {stacks} \nDatapoints per stack: {datapoints}")

    # Convert rows to columns 
    flat_lists = [ list() for x in range(stacks)]
    for l in values:
        for i in range(stacks):
            flat_lists[i].append(l[i])
    # Create joined lists (all stacks in a row: stack-1..n), and average stack
    joined_lists = [] 
    listsofaverage = []
    for i in range(len(flat_lists)):
        joined_lists += flat_lists[i]
        listsofaverage.append(sum(flat_lists[i])/len(flat_lists[i]))

    print ("Recording time :", time)
    np_flat_lists = np.array(flat_lists)
    for i in range(len(np_flat_lists)):
         np_flat_lists[i] = np.array(np_flat_lists[i])
    averages = np.mean(np_flat_lists, axis=0)

    # Store data:
    if store:
        store_data(path, data, values)
    # Plot data: 
    # TODO: what is plotted here?
    if plot and joined=="stacked":    
        plot_data(values, time, path)
    # Print all stacks in a row (stack-1, stack-2, ..., stack-n)
    elif plot and joined=="in_a_row":
        plot_data(joined_lists, time, path)
    # Plot first and last stack
    elif plot and joined=="first_last":
        plot_data(flat_lists[0], time, path, list2=flat_lists[-1])
    # Plot average, also mark and print peaks
    elif plot and joined=="average":
        mid = int( 0.5 * len(flat_lists))
        # Get monosynaptic input from 200ms, every 100ms, 20ms interval (first 10 peaks)
        max_peaks = get_peaks(flat_lists[mid], start, step, interval, num_intervals=10, comp=np.greater_equal)
        min_peaks = get_peaks(flat_lists[mid], start, step, interval, num_intervals=10, comp=np.less_equal)
        min_peaks, max_peaks = alternate_min_max(min_peaks, max_peaks)
        # Alternative method to get dysynaptic input (using all data-points):
        #maxpeaks = get_peaks_in_range(flat_lists[mid], comp=np.greater_equal)
        df = peaks_to_dataframe(get_only_peaks(max_peaks), get_only_peaks(min_peaks))
        print(df)
        # Finally: plot data
        plot_data(flat_lists[mid], time, path, min_peaks=min_peaks, max_peaks=max_peaks, df=df)
        
if __name__ == '__main__': 
    run()
