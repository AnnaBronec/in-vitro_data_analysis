import json
import numpy as np
import os
from igor2.binarywave import load as loadibw
from typing import List

def extract_data(path: str, store: bool) -> List[List[int]]:
    data = loadibw(path)
    wave = data['wave']
    datapoints_per_stack = np.nan_to_num(wave['wData']).tolist()
    del data['wave']['wData']
    # Store data:
    if store:
        __store_data(path, data, datapoints_per_stack)
    return datapoints_per_stack

def convert_rows_to_columns(
    datapoints_per_stack: List[List[float]], num_stacks: int
) -> List[List[int]]:
    flat_lists = [ list() for x in range(num_stacks)] #flat_lists = leere Liste für jeden stack
    for nth_datapoints in datapoints_per_stack:
        for stack in range(num_stacks):
            flat_lists[stack].append(nth_datapoints[stack])
    return flat_lists

def join_lists(flat_lists: List[List[float]]) -> List[List[float]]:
    joined_lists = [] 
    for i in range(len(flat_lists)):
        joined_lists += flat_lists[i]
    return joined_lists

def __store_data(path, data, values): 
    path = path.replace('ibw', '')
    path = path.replace('input', 'output')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = format(data).splitlines()            
    with open(f'{path}.txt', 'w') as writer: 
        writer.writelines([line + "\n" for line in lines])
        # json.dump(data, writer, indent=4)
    with open(f'{path}.json', 'w') as writer:
        json.dump(values, writer, indent=4)





