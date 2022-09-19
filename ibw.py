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

def get_peaks(xs, total_time):
    df = pd.DataFrame(xs, columns=['data'])
    n = int(len(xs) / 25)
    df['max'] = df.iloc[argrelextrema(df.data.values, np.greater_equal,
                        order=n)[0]]['data']
    peaks = []
    average = sum(xs)/len(xs)
    for i in range(len(df['max'])):
        if not math.isnan(df['max'][i]) and df['max'][i] > average:
           peaks.append([i, i*DT, df['max'][i]]) 
        else:
           df['max'][i] = math.nan
    print(f"num peaks: {len(peaks)}")
    plt.scatter(df.index, df['max'], c='r')
    plt.plot(df.index, df['data'])
    plt.show()
    return peaks
    print(peaks)


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

def plot_data(values, total_time, path, list2=None):  
    listxachs=np.linspace(0, total_time, len(values))
    plt.plot(listxachs, values, linewidth=0.3, color="red")
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
    path = path.replace('ibw','svg')
    path = path.replace('input','output')  #input, ouput = foldernames
    plt.savefig(f'{path}',format='svg')                 #only if you want to safe it
  #  plt.savefig(f'{path}.eps', format='eps')
   # plt.savefig(f'{path}.svg', format='svg')
    plt.show()


@click.command()
@click.option('--path', help='specify the path and filename: "Data/<date>/<filename>"')
@click.option('--plot', default=True, help='show plot')
@click.option('--store', default=True, help='store data: stores complete data as txt and values as json.')
@click.option('--joined', help='join lists')
def run(path, plot, store, joined):
    # Extract complete data and values 
    data, values = extract_data(path)

    print("joined: ", joined)
    
    stacks = len(values[0])
    datapoints = len(values)

    time = datapoints * DT
    #time = seconds / 60  #convert to minutes
    #time = seconds/ 20

    print(f"Number of stacks: {stacks} \nDatapoints per stack: {datapoints}")

    flat_lists = [ list() for x in range(stacks)]
    for l in values:
        for i in range(stacks):
            flat_lists[i].append(l[i])
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
    if plot and joined=="stacked":    
        plot_data(values, time, path)
    elif plot and joined=="in_a_row":
        plot_data(joined_lists, time, path)
    elif plot and joined=="first_last":
        plot_data(flat_lists[0], time, path, flat_lists[-1])
    elif plot and joined=="average":
        mid= int( 0.5 * len(flat_lists))
        plot_data(flat_lists[mid], time ,path)
        maxpeak = get_peaks(flat_lists[mid], time)
        print(maxpeak)
       # plot_data(average, time ,path)
       # plot_data(maxpeak, time, c='r')
       # plt.plot(total_time, df['data'])
        plt.show()

       # plot_data(listsofaverage, time, path)
        
if __name__ == '__main__': 
    run()
