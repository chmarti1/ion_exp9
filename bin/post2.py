#!/usr/bin/python3

import os,sys,shutil
import numpy as np
import matplotlib.pyplot as plt
import json

data_dir = os.path.abspath('../data')

materials = {
    'steel':{'index':1, 'c_min_pct':0.06, 'c_max_pct':0.08, 'c_pct':0.07},
    'iron':{'index':0, 'c_min_pct':0.0, 'c_max_pct':.005, 'c_pct':0.0},
    'stainless':{'index':2, 'c_min_pct':0.0, 'c_max_pct':.008, 'c_pct':0.0}
    }

material = []
c_min_pct = []
c_max_pct = []
c_pct = []
current_ua = []

for this in os.listdir(data_dir):
    include = True
    post1_dir = os.path.join(data_dir, 'post1')
    # If post1 has been run
    if os.path.isdir(post1_dir):
        with open(os.path.join(post1_dir, 'results.json'), 'r') as ff:
            results = json.load(ff)
        print(this)
        # If these data are marked for inclusion
        if 'post2' in results and results['post2']:
            print('..')
            this_mat = materials[results['wire_material']]
            c_min_pct.append(mat['c_min_pct'])
            c_max_pct.append(mat['c_min_pct'])
            c_pct.append(mat['c_pct'])
            material.append(mat['index'])
            current_ua.append(results['mean_ua'])

material = np.array(material)
current_ua = np.array(current_ua)
c_min_pct = np.array(c_min_pct)
c_max_pct = np.array(c_max_pct)
c_pct = np.array(c_pct)

c_min_pct -= c_pct
c_max_pct -= c_pct

fig,ax = plt.subplots(1,1)
ax.errorbar(material, current_ua, xerr=(c_min_pct, c_max_pct))
fig.savefig('../post2.png')
