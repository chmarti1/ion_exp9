#!/usr/bin/python3
#
#   Preliminary post-processing on experiment 9 data.
#   The experiment 9 data are collected on wires fed at a constant rate
# into the flame with the cutting oxygen activated.  Post1 applies the
# relevant calibrations and calculates meta data like total flow rate
# and f/o ratio.  Most importantly, it produces plots of the current
# signal throughout the test and accumulates statistics on the current
# signal throughout.  The statistics are written to result.json in
# the post1 directory.
#
# ** Raw Data Files **
# flow.dat is a window of voltages measured from oxygen and fuel gas 
# flow meters immediately prior to the test.
#
# burn.dat is the raw voltage and current measurement during the burn
# with meta data embedded.
# 


import os,sys,shutil
import numpy as np
import lconfig as lc
import json

# Where are the data files?
data_dir = os.path.abspath('../data')
# Should previous post-processing be overwritten?
overwrite = True
# Which post-processing step is this?
post_name = 'post1'
# How many samples should be included in a window
window_samples = 1000
# Current threshold for start- and stop-of-test
threshold_ua = 20.
# What should we identify ourselves in error messages?
POST_NAME = post_name.upper()

# Define a function that can be called repeatedly in a loop
# that is responsible for operating on the raw data sets
def post(target_dir, overwrite, startstop = None):
    # We now have a target data directory path stored in target_dir.
    # Next, build the paths to the required source files and the output 
    # directory/files
    burn_dat = os.path.join(target_dir, 'burn.dat')
    flow_dat = os.path.join(target_dir, 'flow.dat')
    post_dir = os.path.join(target_dir, post_name)
    results_json = os.path.join(post_dir, 'results.json')
    windows_dir = os.path.join(post_dir, 'windows')


    if not os.path.isfile(burn_dat):
        print(POST_NAME + ': Required file not found: ' + burn_dat)
        return
    if not os.path.isfile(flow_dat):
        print(POST_NAME + ': Required file not found: ' + flow_dat)
        return
    if os.path.isdir(post_dir):
        if overwrite:
            print(POST_NAME + ' [REPROCESSING] ' + target_dir)
            shutil.rmtree(post_dir)
            os.mkdir(post_dir)
        else:
            print(POST_NAME + ' [  IGNORING  ] ' + target_dir)
            return
    else:
        print(    POST_NAME + ' [ PROCESSING ] ' + target_dir)
        os.mkdir(post_dir)

    os.mkdir(windows_dir)

    # Load the raw data
    burn = lc.LConf(burn_dat, data=True, cal=True)
    flow = lc.LConf(flow_dat, data=True, cal=True)

    # Initialize a result dictionary
    results = {}

    # Start with some flow calculations
    o2_scfh = np.mean(flow.get_channel('Oxygen'))
    fg_scfh = np.mean(flow.get_channel('Fuel Gas'))

    results['window_samples'] = window_samples
    results['threshold_ua'] = threshold_ua

    results['o2_scfh'] = o2_scfh
    results['fg_scfh'] = fg_scfh
    results['fto_ratio'] = fg_scfh / o2_scfh
    results['preheat_scfh'] = o2_scfh + fg_scfh

    # Move on to embedded meta-data
    results['wire_d_in'] = burn.get_meta(0, 'wire_d_in')
    results['standoff_in'] = burn.get_meta(0, 'standoff_in')
    results['cut_o2_psig'] = burn.get_meta(0, 'cut_o2_psig')
    results['wire_material'] = burn.get_meta(0, 'wire')
    results['feed_ips'] = burn.get_meta(0, 'feed_ips')
    
    # Initialize sliding statistics
    # Sample period
    t_s = 1. / burn.get(0,'samplehz')
    # Start and stop indices
    start_index = 0
    stop_index = burn.data.shape[0]-1
    # Total number of data points
    N = burn.data.shape[0]
    time_s = []
    max_ua = []
    min_ua = []
    mean_ua = []
    median_ua = []
    rms_ua = []
    std_ua = []
   
    i_ua = burn.get_channel('Current')

    if startstop is None:
        temp = np.nonzero(i_ua > threshold_ua)[0]
        if len(temp) == 0:
            print('    !!!EMPTY!!!      Aborting.')
            return
        start_index = int(temp[0])
        stop_index = int(temp[-1])
    else:
        start_index = int(startstop[0] / t_s)
        stop_index = int(startstop[1] / t_s)
        
    results['start_index'] = start_index
    results['stop_index'] = stop_index
    results['window_n'] = (stop_index - start_index) // window_samples
    
    fig = lc.plt.figure(1)
    fig.set_size_inches(8,6)
    
    # Loop over the windows
    for count,index in enumerate(range(start_index, stop_index, window_samples)):
        temp = i_ua[index:(index+window_samples)]
        time_s.append(index * t_s)
        max_ua.append(np.max(temp))
        min_ua.append(np.min(temp))
        mean_ua.append(np.mean(temp))
        median_ua.append(np.median(temp))
        std_ua.append(np.std(temp))
        rms_ua.append(np.sqrt(std_ua[-1]**2 + mean_ua[-1]**2))
        
        # Generate the window plot
        fig.clf()
        ax = fig.subplots(1,1)
        t0 = index * t_s
        t1 = (index + window_samples) * t_s
        burn.show_channel('Current', ax=ax, start=t0, stop=t1)
        ax.axhline(max_ua[-1], color='k',ls='--')
        ax.axhline(min_ua[-1], color='k',ls='--')
        ax.axhline(mean_ua[-1], color='g',ls='-', label='Mean')
        ax.axhline(median_ua[-1], color='r',ls='-', label='Median')
        ax.axhline(rms_ua[-1], color='c',ls='-', label='RMS')
        ax.legend(loc=0)
        
        fig.savefig(os.path.join(windows_dir, f'{count}.png'))
    
    results['mean_ua'] = np.mean(i_ua[start_index:stop_index])
    results['median_ua'] = np.median(i_ua[start_index:stop_index])
    results['std_ua'] = np.std(i_ua[start_index:stop_index])
    results['rms_ua'] = np.sqrt(results['mean_ua']**2 + results['std_ua']**2)
    
    
    # Write results
    with open(results_json, 'w') as ff:
        json.dump(results, ff, indent=2)
    
    # Generate plots
    fig.clf()
    ax = fig.subplots(1,1)
    burn.show_channel('Current', ax=ax)
    ax.step(time_s, mean_ua, 'k--', where='post')
    ax.axhline(results['mean_ua'], color='k')
    ax.set_xlim(start_index*t_s, stop_index*t_s)
    fig.savefig(os.path.join(post_dir,'current.png'))

# In the special case with no arguments, iterate over ALL data
if len(sys.argv) == 1:
    for this in os.listdir(data_dir):
        test = os.path.join(data_dir, this)
        post(test, overwrite, None)
    exit(0)
elif len(sys.argv) == 2:
    target_dir = sys.argv[1]
    startstop = None
elif len(sys.argv) == 4:
    target_dir = sys.argv[1]
    startstop = (float(sys.argv[2]), float(sys.argv[3]))
else:
    raise Exception('post1.py data_dir [start stop]')    
        

# Search for the data set based on the trailing numbers
fail = True
for this in os.listdir(data_dir):
    test = os.path.join(data_dir, this)
    if os.path.isdir(test) and this.endswith(target_dir):
        if fail:
            target_dir = test
            fail = False
        else:
            raise Exception(POST_NAME + ': Found multiple data directories ending with: "' + target_dir + '"')

if fail:
    raise Exception(POST_NAME + ': Failed to find a data directory ending with: "' + target_dir + '"')
post(target_dir, True, startstop)
