#!/usr/bin/python

import json
from sh import repoquery

INTERNAL_REPO = ['mos61']
EXTERNAL_REPO = ['base', 'epel']


def get_packages(repoid, name='-a'):
    queryfmt = '{"name":"%{name}","version":"%{version}",' \
               '"release":"%{release}","vendor":"%{vendor}",' \
               '"repoid":"%{repoid}","packager":"%{packager}",' \
               '"epoch":"%{epoch}"}'
    queryargs = ['--repoid=%s' % repoid, '--qf', queryfmt, name]
    for line in repoquery(*queryargs):
        yield json.loads(line.strip())


def get_dependencies(repoid, name):
    reqs = set()
    queryargs = ['--repoid=%s' % repoid, '--qf', '%{name}',
                 '--resolve', '--requires', name]
    for item in repoquery(*queryargs):
        item = item.strip()
        if item != name:
            reqs.add(item)
    return list(reqs)


packages = {}
for repoid in INTERNAL_REPO:
    for pkg in get_packages(repoid=repoid):
        name = pkg['name']
        pkg['requires'] = get_dependencies(repoid, name)
        packages.setdefault(name, {})[repoid] = pkg
        for repoid_ext in EXTERNAL_REPO:
            for pkg_ext in get_packages(repoid=repoid_ext, name=name):
                pkg_ext['requires'] = get_dependencies(repoid_ext, name)
                packages.setdefault(name, {})[repoid_ext] = pkg_ext

with open('packages.json', 'w') as f:
    f.write(json.dumps(packages, indent=2, sort_keys=True))

