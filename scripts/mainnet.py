#!/bin/python

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import re
import sys
from dateutil import parser

if len(sys.argv) < 2:
    print('usage: mainnet.py [file1] [file2] ...')
    sys.exit(1)

genesis = 1606824023

fig, ax = plt.subplots()  # Create a figure containing a single axes.
ax.set_title(f'Propagation times in mainnet observed in different locations')
ax.set_xlabel('time in second')
ax.set_ylabel('probability density function (pdf)')
ax.set_xticks(np.arange(0, 10, 1.0));
ax.set_xticks(np.arange(0, 10, 0.5), minor=True);
all_delays = []
for fname in sys.argv[1:]:
    f = open(fname)
    delays = []
    for line in f.readlines():
        match = re.search(r'^(.*) INFO.*New block received.*slot: (\d+),', line)
        if match == None:
            continue
        time = parser.parse(match.group(1) + " UTC")
        slot = int(match.group(2))
        slot_time = slot * 12 + genesis;
        delays.append(time.timestamp() - slot_time)
        print(slot)
    ax.hist(delays, np.arange(0, 10, 0.05), density=True, histtype='step', label=fname)
    all_delays += delays

ax.axvline(np.median(all_delays), color='k', label="median", linestyle='dashed', linewidth=1)
ax.legend()
fig.savefig(f'histogram.png')
