#!/usr/bin/python

import re
import json

filename = 'master-node-packages.txt'
re_nvr = r'([\w\-]+)-((\d+\:)??[\w\.]*(?=\d+)[\w\.]*)-([\w\.]*(?=\d+)[\w\.]*)'

packages = {}
reason = 'fuel-master'
with open(filename) as f:
    for line in f.readlines():
        name = line.strip()
        #name, reason = line.strip().split(' ', 1)
        match = re.match(re_nvr, name)
        if match:
            name = match.group(1)
        packages.setdefault(reason, []).append(name)

with open(filename + '.json', 'w') as f:
    f.write(json.dumps(packages, sort_keys=True, indent=2))

