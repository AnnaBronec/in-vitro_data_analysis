from typing import Dict, List
import numpy as np
import click
from matplotlib import pyplot as plt
from scipy import integrate
from extractor.preprocessing import extract_data, convert_rows_to_columns, join_lists
from extractor.functions import (
    Peaks,
    Selection,
    avrg,
    get_only_peaks, 
    alternate_min_max, 
    get_peaks, 
    peaks_to_dataframe, 
    DT,
)
from extractor.plotting import plot_data
from extractor.integral import get_integral 

VERSION = "0-0-2"

def plot(
    path: str, flat_lists: List[List[float]], time: float, selection: Selection
) -> List[List[float]]:
    ranged_flat_lists = [flat_lists[i] for i in range(selection.start, selection.end)]
    rtn_data = ranged_flat_lists if not selection.calc_avrg else [ avrg(ranged_flat_lists) ]
    print("got ranged lists: ", type(ranged_flat_lists), len(ranged_flat_lists), avrg)
    print("got ranged lists: ", type(rtn_data), len(rtn_data))
    if avrg: 
        data, time = average(ranged_flat_lists, time)
    else: 
        data, time = in_a_row(ranged_flat_lists, time)
    plot_data(path, data, time)
    print("got ranged lists: ", type(rtn_data), len(rtn_data))
    return rtn_data

      
def in_a_row(flat_lists: List[List[float]], time: float):
    # Create joined lists (all stacks in a row: stack-1..n), and average stacks
    return join_lists(flat_lists), time*len(flat_lists)

# elif plot and joined=="average":
def average(flat_lists: List[List[float]], time: float):   
    return avrg(flat_lists), time

def peaks(flat_lists: List[List[int]], peaks_info: Peaks) -> Dict[int, Dict]:
    print("flat_lists: ", type(flat_lists), len(flat_lists))
    peaks = {} 
    for index, sweep in enumerate(flat_lists):
        peaks[index] = {
            "max": get_peaks(sweep, peaks_info, comp=np.greater_equal),
            "min": get_peaks(sweep, peaks_info, comp=np.less_equal)
        }
    return peaks


# Calculate and plot integral
# def average(
#     flat_lists: List[List[int]], time: float, start: float, step: float, interval: float
# )
# get_integral(avrg, start=start, show_plot=True)
# # Get MONOSYNAPTIC INPUT from 200ms, every 100ms, 20ms interval (first 10 peaks)
# max_peaks = get_peaks(avrg, start, step, interval, num_intervals=10, comp=np.greater_equal)
# min_peaks = get_peaks(avrg, start, step, interval, num_intervals=10, comp=np.less_equal)
# min_peaks, max_peaks = alternate_min_max(min_peaks, max_peaks)
# # plt.ylim(-200, -45) TODO (fux): removed since view was better without
# # Alternative method to get DYSYNAPTIC INPUT (using all data-points):
# df = peaks_to_dataframe(get_only_peaks(max_peaks), get_only_peaks(min_peaks))
# print(df)
# Finally: plot data
# plot_data(path, avrg, time, min_peaks=min_peaks, max_peaks=max_peaks, df=df)

@click.command()
@click.option('--path', help='specify the path and filename: "Data/<date>/<filename>"')
@click.option('--plot', default=True, help='show plot')
@click.option('--store', default=True, help='store data: stores complete data as txt and datapoints_per_stack as json.')
@click.option('--joined', help='join lists (stacked, in-a-row, first-last, average)')
@click.option('--start', help='start of interval peaks(ms)', default=0.2)
@click.option('--step', help='step size recognized values', default=0.1)
@click.option('--interval', help='jumps values defined by interval',
              default=0.002)
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
       stacked(path, datapoints_per_stack, time)
    # Print all stacks in a row (stack-1, stack-2, ..., stack-n)
    elif plot and joined=="in-a-row":   
        in_a_row(path, flat_lists, time)
    # Plot first and last stack
    elif plot and joined=="first-last":
        first_last(path, flat_lists, time)
        ##new code start
    elif plot and joined=="average":
        average(path, flat_lists, time, start, step, interval)
        # average_new(flat_lists, time, start, step, interval)
    elif plot and joined=="average_new":
        average_new(flat_lists, time, start, step, interval)

if __name__ == '__main__':
    run()
