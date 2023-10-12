from typing import List
import numpy as np
import click
from preprocessing import extract_data, convert_rows_to_columns, join_lists
from functions import get_only_peaks, alternate_min_max, get_peaks, peaks_to_dataframe, DT
from plotting import plot_data
from matplotlib import pyplot as plt
from scipy import integrate
from integral import get_integral 
      
def stacked(path: str, datapoints_per_stack: List[List[int]], time: float) -> None:
    # plt.ylim(-70, -35)
    plot_data(path, datapoints_per_stack, time)
    # print("Integral:", (-1)*np.trapez(datapoints_per_stack))

def in_a_row(path: str, flat_lists: List[List[int]], time: float):
    # Create joined lists (all stacks in a row: stack-1..n), and average stacks
    joined_lists = join_lists(flat_lists)
    return plot_data(path, joined_lists, time)

def first_last(path: str, flat_lists, time):
    plot_data(path, flat_lists[0], time, list2=flat_lists[-1])
    min_val = time[0]
    for i in [0, -1]:
        min_val = min(flat_lists[i])
        print("INTAGRAL: ", integrate.simps([x-min_val for x in flat_lists[i]]))
   # Plot average, also mark and print peaks

# elif plot and joined=="average":
def average(
    path: str, flat_lists: List[List[int]], time: float, start: float, step: float, interval: float
):   
    # Calculate average
    avrg = [sum([x[i] for x in flat_lists])/len([x[i] for x in flat_lists]) for i in range(len(flat_lists[0]))]
    # Calculate and plot integral
    get_integral(avrg, start=start, show_plot=True)
    # Get MONOSYNAPTIC INPUT from 200ms, every 100ms, 20ms interval (first 10 peaks)
    max_peaks = get_peaks(avrg, start, step, interval, num_intervals=10, comp=np.greater_equal)
    min_peaks = get_peaks(avrg, start, step, interval, num_intervals=10, comp=np.less_equal)
    min_peaks, max_peaks = alternate_min_max(min_peaks, max_peaks)
    # plt.ylim(-200, -45) TODO (fux): removed since view was better without
    # Alternative method to get DYSYNAPTIC INPUT (using all data-points):
    df = peaks_to_dataframe(get_only_peaks(max_peaks), get_only_peaks(min_peaks))
    print(df)
    # Finally: plot data
    plot_data(path, avrg, time, min_peaks=min_peaks, max_peaks=max_peaks, df=df)

def average_new(
    flat_lists: List[List[int]], time: float, start: float, step: float, interval: float
):
    # Calculate average
    avrg = [sum([x[i] for x in flat_lists])/len([x[i] for x in flat_lists]) for i in range(len(flat_lists[0]))]
    # Get MONOSYNAPTIC INPUT from 200ms, every 100ms, 20ms interval (first 10 peaks)
    max_peaks = get_peaks(avrg, start, step, interval, num_intervals=10, comp=np.greater_equal)
    min_peaks = get_peaks(avrg, start, step, interval, num_intervals=10, comp=np.less_equal)
    min_peaks, max_peaks = alternate_min_max(min_peaks, max_peaks)
    plt.ylim(-200, -20)
    # Alternative method to get DYSYNAPTIC INPUT (using all data-points):
    df = peaks_to_dataframe(get_only_peaks(max_peaks), get_only_peaks(min_peaks))
    print(df)
        
    #Calculate min_val before using it in integral calculation
    min_val = min(avrg)        
    #Calculate the integral value of the entire avrg data after the avrg is complete
    integral_value = integrate.simps([x - min_val for x in avrg], dx=step)
    #Create a time array for the integral data
    integral_time = np.linspace(0, time, len(avrg))
    #Perform element-wise addition to the avrg list
    avrg_with_min_val = [x + min_val for x in avrg]
    #Show the integral value as text on the plot
    plt.text(
        0.7, 
        0.9, 
        f'Integral Value: {integral_value:.2f}', 
        transform=plt.gca().transAxes, 
        fontsize=12, 
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )

    #Finally: plot data
    plt.plot(integral_time, avrg, label='Average Data')
    plt.fill_between(integral_time, min_val, avrg_with_min_val, alpha=0.3, label='Integral Area')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.title('Average Data with Integral Area')
    plt.legend()
    plt.grid(True)
    #scalebar(X,Y)
    plt.show()
##here old code
    print("INTEGRAL: ", integral_value)  # Integral value at the end of the data


# def calculate_area_under_curve(flat_lists: List[List[int]], time: float, end_time=1.25):
#     """ 
#     Beispielaufruf:
#         `area_under_curve = calculate_area_under_curve(flat_lists, time)`
#         `print("Fläche unter der Kurve bis zur Zeitachse 1.25:", area_under_curve)`
#     """
#     # Extrahiere den ersten Wert von flat_lists
#     first_list = flat_lists[0]
# 
#     # Finde den Index des Zeitpunkts, an dem die Zeitachse 1.25 erreicht
#     index_end_time = int(end_time / time[1])  # Annahme: Zeitintervalle sind gleichmäßig
# 
#     # Erzeuge einen Ausschnitt der Daten bis zur Zeitachse 1.25
#     subset_first_list = first_list[:index_end_time + 1]
# 
#     # Berechne die Fläche unter der Kurve mithilfe der Trapezregel
#     area = integrate.trapz(subset_first_list, dx=time[1])
# 
#     return area

@click.command()
@click.option('--path', help='specify the path and filename: "Data/<date>/<filename>"')
@click.option('--plot', default=True, help='show plot')
@click.option('--store', default=True, help='store data: stores complete data as txt and datapoints_per_stack as json.')
@click.option('--joined', help='join lists (stacked, in_a_row, first_last, average)')
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
    elif plot and joined=="in_a_row":   
        in_a_row(path, flat_lists, time)
    # Plot first and last stack
    elif plot and joined=="first_last":
        first_last(path, flat_lists, time)
        ##new code start
    elif plot and joined=="average":
        average(path, flat_lists, time, start, step, interval)
        # average_new(flat_lists, time, start, step, interval)
    elif plot and joined=="average_new":
        average_new(flat_lists, time, start, step, interval)

if __name__ == '__main__':
    run()
