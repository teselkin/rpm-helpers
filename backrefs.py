#!/usr/bin/python

import json


with open('packages.json') as f:
    packages = json.load(f)


rdeps = {}
for name in packages:
    pkg = packages[name]
    if name not in rdeps:
        rdeps[name] = set()
    for dep in pkg['requires']:
        if dep in rdeps:
            rdeps[dep].add(name)
        else:
            rdeps[name] = set()


backrefs = {}
for name in rdeps:
    pkg = packages[name]
    rec = {
        'rdeps': list(rdeps[name]),
        'count': len(rdeps[name]),
        'vendor': pkg['vendor'],
        'packager': pkg['packager'],
    }
    backrefs[name] = rec


with open('backrefs.json', 'w') as f:
    f.write(json.dumps(backrefs, sort_keys=True, indent=2))

