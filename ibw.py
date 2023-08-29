import os.path
import math
import numpy as np
import click
import pandas as pd
from preprocessing import extract_data, convert_rows_to_columns, join_lists
from matplotlib import pyplot as plt
from scipy.signal import argrelextrema
from scipy import integrate

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
            last_was_min = True
        if not math.isnan(max_peaks[i]):
            if last_was_min == False:
                max_peaks[i] = math.nan
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
@click.option('--store', default=True, help='store data: stores complete data as txt and datapoints_per_stack as json.')
@click.option('--joined', help='join lists (stacked, in_a_row, first_last, average)')
@click.option('--start', help='start of interval peaks(ms)', default=0.2)
@click.option('--step', help='step size recognized values', default=0.1)
@click.option('--interval', help='jumps values defined by interval', default=0.02)
def run(path, plot, store, joined, start, step, interval):
    # Extract complete data and datapoints_per_stack 
    datapoints_per_stack = extract_data(path, store)

    # Get number of stacks, datapoints per stack and time
    num_stacks = len(datapoints_per_stack[0]) # Länge der 1. Liste (= Widerholung der Mssung)
    num_datapoints = len(datapoints_per_stack) # Anzahl Listen
    time = num_datapoints * DT
    print(f"Number of stacks: {num_stacks}")
    print(f"Datapoints per stack: {num_datapoints}") 
    print(f"Recording time: {time}")

    # Convert rows to columns 
    flat_lists = convert_rows_to_columns(datapoints_per_stack, num_stacks)

    # Plot data: 
    if plot and joined=="stacked":    
        plot_data(datapoints_per_stack, time, path)
        print("Integral:", (-1)*np.trapez(datapoints_per_stack))
    # Print all stacks in a row (stack-1, stack-2, ..., stack-n)
    elif plot and joined=="in_a_row":   
        # Create joined lists (all stacks in a row: stack-1..n), and average stack
        joined_lists = join_lists(flat_lists)
        plot_data(joined_lists, time, path)
    # Plot first and last stack
    elif plot and joined=="first_last":
        plot_data(flat_lists[0], time, path, list2=flat_lists[-1])
        for i in [0, -1]:
            min_val = min(flat_lists[i])
            print("INTAGRAL: ", integrate.simps([x-min_val for x in flat_lists[i]]))
    # Plot average, also mark and print peaks
    elif plot and joined=="average":
        avrg = [sum([x[i] for x in flat_lists])/len([x[i] for x in flat_lists]) for i in range(len(flat_lists[0]))]
        # Get MONOSYNAPTIC INPUT from 200ms, every 100ms, 20ms interval (first 10 peaks)
        max_peaks = get_peaks(avrg, start, step, interval, num_intervals=10, comp=np.greater_equal)
        min_peaks = get_peaks(avrg, start, step, interval, num_intervals=10, comp=np.less_equal)
        min_peaks, max_peaks = alternate_min_max(min_peaks, max_peaks)
        plt.ylim(-85, -55)
        # Alternative method to get DYSYNAPTIC INPUT (using all data-points):
        df = peaks_to_dataframe(get_only_peaks(max_peaks), get_only_peaks(min_peaks))
        print(df)
        # Finally: plot data
        plot_data(avrg, time, path, min_peaks=min_peaks, max_peaks=max_peaks, df=df)
        # Substract min value from each value, to get integral from baseline only (not down to zero).
        min_val = min(avrg)
        print("INTAGRAL: ", integrate.simps([x-min_val for x in avrg]))

if __name__ == '__main__': 
    run()
