import numpy as np
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use("svg")

def plot_data(
    path, values, total_time, min_peaks=None, max_peaks=None, df=None
):  
    print("Plotting now: ", len(values), total_time)
    listxachs=np.linspace(0, total_time, len(values)) 
    # Plot peaks, if set
    if min_peaks is not None:
        plt.scatter(listxachs, min_peaks, c='b')
    if max_peaks is not None:
        plt.scatter(listxachs, max_peaks, c='b')
    print("building plot")
    plt.plot(listxachs, values, linewidth=0.3, color="red")
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
    print("storing file")
    path = path.replace('input','output')  # input, ouput = foldernames
    path = path.replace('ibw','png')
    plt.savefig(path, format='png', dpi=90)  # Adjust dpi for lower resolution
    path = path.replace('png','svg')
    plt.savefig(path, format='svg')    # only if you want to safe it
    # Store df (peaks)
    if df is not None:
        path = path.replace('svg','csv')
        df.to_csv(path)
    print("clearing up")
    plt.cla()
    plt.clf()
    print("done")
    # plt.show()
    
def scalebar(abf=None, hideTicks=True, hideFrame=True, fontSize=8, scaleXsize=None, scaleYsize=None, scaleXunits=2, scaleYunits=5, lineWidth=2): 
     """ 
     Add an L-shaped scalebar to the current figure. 
     This removes current axis labels, ticks, and the figure frame. 
     """ 
  
     # if an ABF objet is given, use its sweep units 
     if abf: 
         scaleXunits = abf.sweepUnitsX 
         scaleYunits = abf.sweepUnitsY 
  
     # calculate the current data area 
     x1, x2, y1, y2 = plt.axis()  # bounds 
     xc, yc = (x1+x2)/2, (y1+y2)/2  # center point 
     xs, ys = abs(x2-x1), abs(y2-y1)  # span 
  
     # determine how big we want the scalebar to be 
     if not scaleXsize: 
         scaleXsize = abs(plt.xticks()[0][1]-plt.xticks()[0][0])/2 
     if not scaleYsize: 
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
