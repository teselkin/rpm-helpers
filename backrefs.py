#!/usr/bin/python

import json

REPOID = 'mos61'


with open('packages.json') as f:
    packages = json.load(f)


rdeps = {}
for name in packages:
    pkg = packages[name][REPOID]
    rdeps.setdefault(name, set())
    for dep in pkg['requires']:
        rdeps.setdefault(dep, set()).add(name)


backrefs = {}
for name in rdeps:
    pkg = packages[name][REPOID]
    rec = {
        'rdeps': list(rdeps[name]),
        'count': len(rdeps[name]),
        'vendor': pkg['vendor'],
        'packager': pkg['packager'],
    }
    backrefs[name] = rec


with open('backrefs.json', 'w') as f:
    f.write(json.dumps(backrefs, sort_keys=True, indent=2))

