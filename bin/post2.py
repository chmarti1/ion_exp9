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
import lplot as lp

data_dir = os.path.abspath('../data')

materials = {
    'steel':{'index':1, 'c_min_pct':0.06, 'c_max_pct':0.1, 'c_pct':0.1},
    'hcsteel': {'index':2, 'c_min_pct':0.80, 'c_max_pct':0.95, 'c_pct':0.85},
    'iron':{'index':0, 'c_min_pct':0.0, 'c_max_pct':.005, 'c_pct':0.0},
    'stainless':{'index':3, 'c_min_pct':0.0, 'c_max_pct':.008, 'c_pct':0.0}
    }

material = []
c_min_pct = []
c_max_pct = []
c_pct = []
current_ua = []
max_ua = []
min_ua = []
std_ua = []

for this in os.listdir(data_dir):
    include = True
    source_dir = os.path.join(data_dir, this)
    post1_dir = os.path.join(source_dir, 'post1')
    # If post1 has been run
    if os.path.isdir(post1_dir):
        try:
            with open(os.path.join(post1_dir, 'results.json'), 'r') as ff:
                results = json.load(ff)
            print(this)
            # If these data are marked for inclusion
            if 'post2' in results and results['post2']:
                print('adding dataset:', results['wire_material'])
                
                # Grab the material properties
                this_mat = materials[results['wire_material']]
                c_min_pct.append(this_mat['c_min_pct'])
                c_max_pct.append(this_mat['c_max_pct'])
                c_pct.append(this_mat['c_pct'])
                material.append(this_mat['index'])
                
                max_ua.append(results['mean_max_ua'])
                min_ua.append(results['mean_min_ua'])
                std_ua.append(results['mean_std_ua'])
                current_ua.append(results['mean_ua'])
        except:
            pass
            

material = np.array(material)
current_ua = np.array(current_ua)
max_ua = np.array(max_ua) - current_ua
min_ua = current_ua - np.array(min_ua)
c_min_pct = np.array(c_min_pct)
c_max_pct = np.array(c_max_pct)
c_pct = np.array(c_pct)

# Save the conditions to a table
X = np.array([c_pct, c_min_pct, c_max_pct, current_ua, std_ua]).transpose()
np.savetxt('../post2.dat', X,
    header='C(%) C_min(%) C_max(%) I(uA) I_std(uA)',
    delimiter='\t')

c_min_pct = c_pct - c_min_pct
c_max_pct = c_max_pct - c_pct

# Exclude iron from the linear fit
I = material != 0
C = np.polyfit(c_pct[I], current_ua[I], 1)

x = np.linspace(0,1.0,21)
y = np.polyval(C, x)

ax = lp.init_fig('Carbon Content (%)', 'Current ($\mu$A)', label_size=14)
ax.errorbar(c_pct, current_ua, xerr=(c_min_pct, c_max_pct), yerr=std_ua, fmt='ko', capsize=6, )
ax.plot(x,y,'k--')
ax.text(0.05,125,f'y = {C[0]:0.3f} x + {C[1]:0.3f}', backgroundcolor = 'w', fontsize=14)

#ax.set_xscale('log')
#ax.set_yscale('log')
ax.grid(True)
ax.get_figure().savefig('../post2.png')

