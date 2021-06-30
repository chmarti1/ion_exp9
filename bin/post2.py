#!/usr/bin/python3
#
#   Accumulated result post-processing on experiment 9
#
# The user is expected to curate the results of post1 to select which
# experiments should be plotted on a single plot.  To mark an experiment
# for plotting, the user should manually add
#   "post2":1,
# as an entry to the result.json file.  Post 2 will automatically detect
# it and use it for plotting.
#
# The user should also review the automatic threshold detection employed
# by post1; it is not entirely successful.  The "start_index" and 
# "stop_index" indicate the window of the raw data that should be 
# included for calculating the wire current statistics.  The values 
# should be manually adjusted as needed since the automatic detection in
# post1 is not entirely successful.  Post2 will reanalyze the data based
# on the window identified in the results file.
# 

import os,sys,shutil
import numpy as np
import matplotlib.pyplot as plt
import json
import lconfig as lc

data_dir = os.path.abspath('../data')

materials = {
    'steel':{'index':1, 'c_min_pct':0.06, 'c_max_pct':0.08, 'c_pct':0.07},
    'hcsteel': {'index':2, 'c_min_pct':0.8, 'c_max_pct':0.95, 'c_pct':0.85},
    'iron':{'index':0, 'c_min_pct':0.0, 'c_max_pct':.005, 'c_pct':0.0},
    'stainless':{'index':3, 'c_min_pct':0.0, 'c_max_pct':.008, 'c_pct':0.0}
    }

material = []
c_min_pct = []
c_max_pct = []
c_pct = []
current_ua = []
current_max_ua = []
current_min_ua = []
current_std_ua = []

for this in os.listdir(data_dir):
    include = True
    source_dir = os.path.join(data_dir, this)
    post1_dir = os.path.join(source_dir, 'post1')
    # If post1 has been run
    if os.path.isdir(post1_dir):
        with open(os.path.join(post1_dir, 'results.json'), 'r') as ff:
            results = json.load(ff)
        print(this)
        # If these data are marked for inclusion
        if 'post2' in results and results['post2']:
            print(results['wire_material'])
            
            # Grab the material properties
            this_mat = materials[results['wire_material']]
            c_min_pct.append(this_mat['c_min_pct'])
            c_max_pct.append(this_mat['c_min_pct'])
            c_pct.append(this_mat['c_pct'])
            material.append(this_mat['index'])
            
            # Re-load the raw data
            dat = lc.LConf(os.path.join(source_dir, 'burn.dat'), data=True, cal=True)
            index0 = results['start_index']
            index1 = results['stop_index']
            # Get statistics
            I_uA = dat.get_channel(0)
            current_ua.append(np.mean(I_uA[index0:index1]))
            current_max_ua.append(np.max(I_uA[index0:index1]))
            current_min_ua.append(np.min(I_uA[index0:index1]))
            current_std_ua.append(np.std(I_uA[index0:index1]))
            
            

material = np.array(material)
current_ua = np.array(current_ua)
current_max_ua = np.array(current_max_ua) - current_ua
current_min_ua = current_ua - np.array(current_min_ua)
current_std_ua = np.array(current_std_ua)
c_min_pct = np.array(c_min_pct)
c_max_pct = np.array(c_max_pct)
c_pct = np.array(c_pct)

c_min_pct -= c_pct
c_max_pct -= c_pct

fig,ax = plt.subplots(1,1)
ax.errorbar(c_pct, current_ua, xerr=(c_min_pct, c_max_pct), yerr=current_std_ua, fmt='ko', capsize=2)
#ax.set_xscale('log')
#ax.set_yscale('log')
ax.grid(True)
ax.set_xlabel('Carbon Content (%)')
ax.set_ylabel('Current (uA)')
fig.savefig('../post2.png')
