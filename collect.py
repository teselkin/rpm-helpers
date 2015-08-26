#!/usr/bin/python

import json
#from sh import repoquery

from lib.rpm_repodata import Repodata

INTERNAL_REPO = ['mos61']
EXTERNAL_REPO = ['base', 'epel']

"""
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
"""

repos = {}
#repos['base'] = Repodata(name='base', dist_type='centos', dist_release='6.6',
#                         baseurl='http://vault.centos.org/6.6/os/x86_64/')
#repos['epel'] = Repodata(name='epel', dist_type='centos', dist_release='6.6',
#                         baseurl='http://mirror.yandex.ru/epel/6/x86_64/')
repos['base'] = Repodata(name='base', dist_type='centos', dist_release='7',
                         baseurl='http://mirror.yandex.ru/centos/7/os/x86_64/')
repos['epel'] = Repodata(name='epel', dist_type='centos', dist_release='7',
                         baseurl='http://mirror.yandex.ru/epel/7/x86_64/')
repos['mos61'] = Repodata(name='mos61', dist_type='centos', dist_release='6.6',
                          baseurl='http://mirror.fuel-infra.org/fwm/6.1/centos/os/x86_64/')

for repo in repos.values():
    repo.update_cache()

repofrompath = []
for repo in repos.values():
    repofrompath.append(repo.format("{repo_id},{cache_dir}"))


print "Getting list of packages from internal repo:"
packages = {}
for repoid in INTERNAL_REPO:
    for pkg in repos[repoid].get_packages():
        name = pkg['name']
        print "* %s" % name
        pkg['requires'] = repos[repoid].get_dependencies(name)
        packages.setdefault(name, {})[repoid] = pkg


print "Checking external repos:"
packages_ext = {}
for name in packages.keys():
    print "* %s" % name
    for repoid in EXTERNAL_REPO:
        for pkg in repos[repoid].get_packages(name=name):
#            pkg['requires'] = repos[repoid].get_dependencies(name=name)
            packages_ext.setdefault(name, {})[repoid] = pkg


with open('packages.json', 'w') as f:
    f.write(json.dumps(packages, indent=2, sort_keys=True))

with open('packages-ext.json', 'w') as f:
    f.write(json.dumps(packages_ext, indent=2, sort_keys=True))
