import matplotlib.pyplot as plt 
from scipy.integrate import simps
from typing import List, Tuple

def get_integral(ys: List[float], start=0.2, show_plot: bool = True) -> int: 
    """
    Calculates the integral (area underneath the curve) in the first amplitude. 
    The first amplitude is assumed to be at `start` (milliseconds).
    If `show_plot` is True, also plots data.
    """
    xs = [i for i in range(len(ys))] # Create x-values
    base_line = ys[0] # Use fx(0) as baseline

    # Find start and end of first amplitude and create reduced dataset: 
    start, end = __cal_start_end(ys, start=0.2, base_line=base_line)
    xs_integral = [xs[i] for i in range(start, end)]
    ys_integral = [ys[i] for i in range(start, end)]
    
    # Calculate integral
    integral = __cal_area(xs_integral, ys_integral, base_line) 
    print(f'Area underneath the curve (TOTAL): {integral}')

    # Show plot
    if show_plot:
        plot_integral(ys, xs, base_line, ys_integral, xs_integral)
    return integral

def plot_integral(
    ys: List[float], xs: List[int], base_line: float, ys_int: List[float], xs_int: List[int]
) -> None:
    """
    Code plots data in `ys` and additionally shades the aread underneath the
    curve in the shortend data set ys_int (integral)
    """
    plt.plot(xs, ys, label="Curve")
    plt.fill_between(xs_int, ys_int, base_line, alpha=0.2)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    # plt.ylim(-65,-50) TODO (fux): removed since view was better without
    plt.legend()
    # plt.show()

def __cal_area(xs: List[int], ys: List[float], base_line: float):
    return simps(ys, xs, int(base_line))

def __cal_start_end(ys: List[float], start: float, base_line: float) -> Tuple[int, int]:
    start = int(start*len(ys)/2)
    # Use 5 as magic number to skip first minimal differences
    for index, val in enumerate(ys): 
        if index > start+200 and val < base_line: 
            return start, index
    return start, start
