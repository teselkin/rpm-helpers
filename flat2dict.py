#!/usr/bin/python

import argparse
import re
import json

parser = argparse.ArgumentParser()
parser.add_argument('--ifile')
parser.add_argument('--ofile')
parser.add_argument('--key', type=int, default=2)
parser.add_argument('--value', type=int, default=1)
args = parser.parse_args()

ifile = args.ifile
if args.ofile:
    ofile = args.ofile
else:
    ofile = args.ifile + '.json'

key_id = args.key - 1
value_id = args.value - 1
ownership = {}
with open(ifile) as f:
    for line in f.readlines():
        rec = re.compile('\t+').split(line.strip())
        if len(rec) == 0:
            continue
        try:
            key = rec[key_id]
        except IndexError:
            key = ''
        try:
            value = rec[value_id]
        except IndexError:
            value = ''
        ownership.setdefault(key, []).append(value)

with open(ofile, 'w') as f:
    f.write(json.dumps(ownership, indent=2, sort_keys=True))
