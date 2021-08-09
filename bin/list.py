#!/usr/bin/python3

import os,sys,shutil
import numpy as np
import matplotlib.pyplot as plt
import json
import lconfig as lc

data_dir = os.path.abspath('../data')
contents = os.listdir(data_dir)
contents.sort()

for this in contents:
    line = f'{this:<14s} '
    source_dir = os.path.join(data_dir, this)
    post1_dir = os.path.join(source_dir, 'post1')
    
    post1 = ' '
    post2 = ' '
    
    material = 'NONE'
    
    
    # If post1 has been run
    if os.path.isdir(post1_dir):
        post1 = '1'
        with open(os.path.join(post1_dir, 'results.json'), 'r') as ff:
            results = json.load(ff)
        # If these data are marked for inclusion
        if 'post2' in results and results['post2']:
            post2 = '2'
            
        material = results['wire_material']
    
    else:
        try:
            burst_file = os.path.join(data_dir, 'burst.dat')
            burst = lc.LConf(burst_file, data=False)
            material = burst.get_meta(0, 'wire')
        except:
            pass
    print(f'{this:<14s} {post1}{post2} {material}')
    
