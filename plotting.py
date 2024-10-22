from typing import List, Tuple
import numpy as np
import matplotlib
from matplotlib import colors as mcolors
from matplotlib import pyplot as plt

from extractor.functions import Scalebar
matplotlib.use("svg")

def plot_data(
    path, 
    values, 
    total_time, 
    ylim=None, 
    min_peaks=None, 
    max_peaks=None,
    df=None,
    scalebar: Scalebar=None
):  
    num_values = len(values) if isinstance(values[0], float) else len(values[0])
    print("Plotting now: ", num_values, total_time)
    listxachs=np.linspace(0, total_time, num_values)
    # Plot peaks, if set
    if min_peaks is not None:
        plt.scatter(listxachs, min_peaks, c='b')
    if max_peaks is not None:
        plt.scatter(listxachs, max_peaks, c='b')
    print("building plot")
    if isinstance(values[0], float):
        plt.plot(listxachs, values, linewidth=0.3, color="red")
    else: 
        color_names = _color_names(len(values))
        for i, xs in enumerate(values): 
            plt.plot(listxachs, xs, linewidth=0.3, color=color_names[i], label = 'id %s'%i)
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
    if ylim:
        plt.ylim(ylim)
    if scalebar is None or scalebar.show:
        apply_scalebar(scalebar.hide_ticks, scalebar.xsize, scalebar.ysize)
    # Store figure
    plt.savefig(f"{path}.png", format='png', dpi=90)  # Adjust dpi for lower resolution
    plt.savefig(f"{path}.svg", format='svg')    # only if you want to safe it
    # Store df (peaks)
    if df is not None:
        df.to_csv(f"{path}.csv")
    # plt.show()
    plt.cla()
    plt.clf()

def _color_names(num_plots: int) -> List[str]: 
    def sorted_colors() -> List[str]: 
        return sorted(
            mcolors.CSS4_COLORS, 
            key=lambda c: tuple(mcolors.rgb_to_hsv(mcolors.to_rgb(c)))
        )
    if num_plots <= 6:
        return list(mcolors.BASE_COLORS)
    elif num_plots <= 10: 
        return list(mcolors.TABLEAU_COLORS)
    elif num_plots <= 25: 
        return sorted_colors()[4::5] 
    else:
        return sorted_colors()[2::3] 
   
def apply_scalebar(
    hideTicks: bool, 
    scaleXsize: int|None,
    scaleYsize: int|None, 
    scaleXunits="ms", 
    scaleYunits="mV", 
    lineWidth=2,
    hideFrame=True, 
    fontSize=8, 
): 
    """ 
    Add an L-shaped scalebar to the current figure. 
    This removes current axis labels, ticks, and the figure frame. 
    """ 
    # calculate the current data area 
    x1, x2, y1, y2 = plt.axis()  # bounds 
    xc, yc = (x1+x2)/2, (y1+y2)/2  # center point 
    xs, ys = abs(x2-x1), abs(y2-y1)  # span 
  
    # determine how big we want the scalebar to be 
    if scaleXsize is None:
        scaleXsize = abs(plt.xticks()[0][1]-plt.xticks()[0][0])/2 
    if scaleYsize is None:
        scaleYsize = abs(plt.yticks()[0][1]-plt.yticks()[0][0])/2 
  
    # create the scale bar labels 
    lblX = str(scaleXsize) 
    lblY = str(scaleYsize) 
  
    # prevent units unecessarially ending in ".0" 
    if lblX.endswith(".0"): 
        lblX = lblX[:-2] 
    if lblY.endswith(".0"): 
        lblY = lblY[:-2] 
  
    if scaleXunits == "sec" and "." in lblX: 
        lblX = str(int(float(lblX)*1000)) 
        scaleXunits = "ms" 
  
    # add units to the labels 
    lblX = lblX+" "+scaleXunits 
    lblY = lblY+" "+scaleYunits 
    lblX = lblX.strip() 
    lblY = lblY.strip() 
  
    # determine the dimensions of the scalebar 
    scaleBarPadX = 0.10 
    scaleBarPadY = 0.05 
    scaleBarX = x2-scaleBarPadX*xs 
    scaleBarX2 = scaleBarX-scaleXsize 
    scaleBarY = y1+scaleBarPadY*ys 
    scaleBarY2 = scaleBarY+scaleYsize 
  
    # determine the center of the scalebar (where text will go) 
    scaleBarXc = (scaleBarX+scaleBarX2)/2 
    scaleBarYc = (scaleBarY+scaleBarY2)/2 
  
    # create a scalebar point array suitable for plotting as a line 
    scaleBarXs = [scaleBarX2, scaleBarX, scaleBarX] 
    scaleBarYs = [scaleBarY, scaleBarY, scaleBarY2] 
  
    # the text shouldn't touch the scalebar, so calculate how much to pad it 
    lblPadMult = .005 
    lblPadMult += .002*lineWidth 
    lblPadX = xs*lblPadMult 
    lblPadY = ys*lblPadMult 
  
    # hide the old tick marks 
    if hideTicks: 
       plt.gca().get_yaxis().set_visible(False) 
       plt.gca().get_xaxis().set_visible(False) 
  
    # hide the square around the image 
    if hideFrame: 
        plt.gca().spines['top'].set_visible(False) 
        plt.gca().spines['right'].set_visible(False) 
        plt.gca().spines['bottom'].set_visible(False) 
        plt.gca().spines['left'].set_visible(False) 
  
    # now do the plotting 
    plt.plot(scaleBarXs, scaleBarYs, 'k-', lw=lineWidth) 
    plt.text(scaleBarXc, scaleBarY-lblPadY, lblX, 
             ha='center', va='top', fontsize=fontSize) 
    plt.text(scaleBarX+lblPadX, scaleBarYc, lblY, 
             ha='left', va='center', fontsize=fontSize) 
