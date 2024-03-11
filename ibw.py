from typing import Dict, List, Tuple
import numpy as np
import click
from matplotlib import pyplot as plt
from extractor.preprocessing import extract_data, convert_rows_to_columns
from extractor.functions import (
    Peaks,
    Selection,
    avrg,
    calc_time_from_sweeps,
    get_peaks,
    peaks_as_table, 
    DT,
)

VERSION = "0-0-2"

def get_range(
    sweeps: List[List[float]], selection: Selection
) -> Tuple[List[List[float]], float]:
    """
    Gets dataset matching the user defined selection and the appropriate time
    for the selection. 
    Function will always return a list of 1-22 sweeps. If average was selected,
    it will always be a list with one sweep representing the avaerage of the
    selection.
    The time is always the default time multiplied by the number of sweeps.
    """
    # Calculate time based on full data-set
    # Reduce dataset to range requested by user
    ranged_sweeps = [sweeps[i] for i in range(selection.start, selection.end)]
    print("all: ", len(sweeps), f"{selection.start}-{selection.end}", len(ranged_sweeps))
    # If avrg selected by user calculate the averange from the selected range
    ranged_sweeps = [ avrg(ranged_sweeps) ] if selection.calc_avrg else ranged_sweeps
    # calculate time from the number of sweeps obtained.
    return ranged_sweeps, calc_time_from_sweeps(sweeps)
def peaks(
    sweeps: List[List[float]], peaks_info: Peaks
) -> Tuple[Dict[int, Dict], float]:
    print("sweeps: ", type(sweeps), len(sweeps))
    peaks = {} 
    for index, sweep in enumerate(sweeps):
        min_peaks = get_peaks(sweep, peaks_info, comp=np.greater_equal)
        max_peaks = get_peaks(sweep, peaks_info, comp=np.less_equal)
        table = peaks_as_table(max_peaks, min_peaks)
        peaks[str(index)] = {"max": min_peaks, "min": max_peaks, "df": table}
    return peaks, calc_time_from_sweeps(sweeps)

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
