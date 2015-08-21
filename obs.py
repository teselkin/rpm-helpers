#!/usr/bin/python

import json


with open('backrefs.json') as f:
    backrefs = json.load(f)

with open('obs.csv', 'w') as f:
    for name in backrefs.keys():
        if backrefs[name]['count'] == 0 and \
                backrefs[name]['vendor'].startswith('obs://'):
            f.write('%s; %s; %s\n' %(backrefs[name]['count'], name, backrefs[name]['vendor']))

