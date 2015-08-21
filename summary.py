#!/usr/bin/python

import json
from sh import repoquery


def check_other_repos(name, repolist=['base', 'epel']):
    queryfmt = '{"name":"%{name}","version":"%{version}",' \
               '"release":"%{release}","vendor":"%{vendor}",' \
               '"repoid":"%{repoid}","packager":"%{packager}",' \
               '"epoch":"%{epoch}"}'
    a = []
    for repoid in repolist:
        for line in repoquery('--qf', queryfmt, '--repoid=%s' % repoid, name):
            result = line.strip()
            if result:
                a.append(json.loads(result))
    return a


def compare_versions(a, b):
    try:
#        if a['epoch'] != b['epoch']:
#            return 'NO_MATCH'
#
        if a['version'] != b['version']:
            return 'NO_MATCH'

        if a['release'] != b['release']:
            return 'VERSION_MATCH'
    except:
        return 'BAD_DATA'

    return 'FULL_MATCH'


with open('packages.json') as f:
    packages = json.load(f)

with open('backrefs.json') as f:
    backrefs = json.load(f)

#print 'Items in packages.json - %s' % len(packages.keys())
#print 'Items in backrefs.json - %s' % len(backrefs.keys())

with open('summary.csv', 'w') as f:
    for name in packages.keys():
        other_packages = check_other_repos(name)
        if other_packages:
            for pkg in other_packages:
                match = compare_versions(pkg, packages[name])
                pkg_string = '%s %s-%s:%s-%s' % (pkg['repoid'], pkg['name'],
                                                 pkg['epoch'], pkg['version'],
                                                 pkg['release'])
                f.write('%s; %s; %s; %s; %s; %s\n' % (name,
                                                    packages[name]['version'],
                                                    packages[name]['release'],
                                                    backrefs[name]['count'],
                                                    match,
                                                    pkg_string))
        else:
            f.write('%s; %s; %s; %s; %s; %s\n' % (name,
                                                packages[name]['version'],
                                                packages[name]['release'],
                                                backrefs[name]['count'],
                                                'NO_MATCH',
                                                ''))

