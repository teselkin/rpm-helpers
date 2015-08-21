#!/usr/bin/python

import json
from sh import repoquery

srcfile='mos61.json'

with open(srcfile) as f:
    data = json.load(f)

for rec in data:
    if 'name' not in rec:
        continue
    print rec['name']


