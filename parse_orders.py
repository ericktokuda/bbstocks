#!/usr/bin/env python3
"""Parse csv of orders
"""

import argparse
import time
import os
from os.path import join as pjoin
import inspect

import sys
import numpy as np
from itertools import product
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
from io import StringIO
from unicodedata import normalize
import shutil

#############################################################
def info(*args):
    pref = datetime.now().strftime('[%y%m%d %H:%M:%S]')
    print(pref, *args, file=sys.stdout)

##########################################################
def main():
    info(inspect.stack()[0][3] + '()')
    t0 = time.time()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', default='/tmp/out/', help='Output directory')
    args = parser.parse_args()

    if not os.path.isdir(args.outdir): os.mkdir(args.outdir)

    cols = 'stock,reqnum,negnum,cannum,price,operation,empty,status,negdate,regdate'.split(',')
    orderspath = './20200606-ordens.csv'
    linesall = open(orderspath, encoding='ISO-8859-1',).\
            read().strip().split('\n')
    rows = list(reversed(linesall[3:]))
    for i in range(len(rows)):
        fields = rows[i].split(';')
        
        for j in [1, 2, 3]:
            fields[j] = fields[j].replace('.', '')
        fields[4] = fields[4].replace(',', '.')
        for j in [8, 9]:
            dtfields = list(reversed(fields[j].split('.')))
            fields[j] = '-'.join(dtfields)
        rows[i] = ','.join(fields)
    rowsstr = '\n'.join(rows)
    
    
    fh = StringIO(rowsstr)
    df = pd.read_csv(fh, sep=',', names=cols)
    del df['empty']
    df = df[(df.status == 'Negociada')]
    df.index = np.arange(len(df))

    custody = { st: {'n':0, 'value':0.0} for st in np.unique(df.stock)}
    n = len(df)
    for i, row in df.iterrows():
        st = row.stock
        if row.operation == 'Compra':
            custody[st]['n'] += row.negnum
            custody[st]['value'] -= (row.price * row.negnum)
        elif row.operation == 'Venda':
            custody[st]['n'] -= row.negnum
            custody[st]['value'] += (row.price * row.negnum)
        else:
            info('Neihter buy nor sell operation')

    profit = 0.0
    for st, entry in custody.items():
        info('st:{}, n:{}, value:{}'.format(st, entry['n'], entry['value']))
        if entry['n'] == 0: profit += entry['value']

    info('profit:{}'.format(profit))
    breakpoint()
    df.to_csv('/tmp/formatted.csv', index=False)
    info('Elapsed time:{}'.format(time.time()-t0))

##########################################################
if __name__ == "__main__":
    main()

