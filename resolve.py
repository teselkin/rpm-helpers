#!/usr/bin/python

import json
from sh import repoquery
from sh import ls

def list_packages(repoid):
    queryfmt = '{"name":"%{name}","version":"%{version}",' \
               '"release":"%{release}","arch":"%{arch}",' \
               '"repository":"%{repoid}","packager":"%{packager}"}'
    for line in repoquery('-a', '--repoid=%s' % repoid, '--qf', queryfmt):
        yield json.loads(line)

def list_dependencies(name, repoid):
    reqs = set()
    for item in repoquery('--repoid=%s' % repoid, '--qf', '%{name}', '--resolve', '--requires', name):
        item = item.strip()
        if item != name:
            reqs.add(item)
    return list(reqs)

rpms = {}
rdeps = {}
for item in list_packages('mos61'):
    name = item['name']
    rpms[name] = item
    if name not in rdeps:
        rdeps[name] = set()
    for ref in list_dependencies(name, 'mos61'):
        if ref in rdeps:
            rdeps[ref].add(name)
        else:
            rdeps[ref] = set()

with open('backrefs.txt', 'w') as f:
    for key in rdeps.keys():
        deps = list(rdeps[key])
        deps.sort()
        f.write('%s; %s; %s; %s; %s\n' % (len(deps), key, rpms[key]['version'], rpms[key]['packager'], ' '.join(deps)))

