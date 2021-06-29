#!/usr/bin/python3

import time
import os,sys

datadir = '../data'

target = os.path.join(datadir, time.strftime('%Y%m%d%H%M%S'))
flowfile = os.path.join(target, 'flow.dat')
burnfile = os.path.join(target, 'burn')

# Make the target directory
os.mkdir(target)

# Prompt the user for input
go_f = True
while go_f:
    wire = input('Wire type (string):')
    wire_d_in = float(input('Wire diameter (in):'))
    feed = input('Feedrate plan (string):')
    standoff_in = float(input('Standoff (in):'))
    cut_o2_psig = float(input('Cutting O2 pressure (psig):'))
    print('Is the above correct?')
    go_f = not (input('(Y/n):') == 'Y')

# Run the flow measurement
print('Flow measurement')
os.system('lcburst -c flow.conf -d ' + flowfile)

# Run the measurement
print('Measuring...')
os.system(f'lcrun -c burn.conf -d {burnfile} -s wire="{wire}" -f wire_d_in={wire_d_in} -s feed_ips="{feed}" -f standoff_in={standoff_in} -f cut_o2_psig={cut_o2_psig}')
