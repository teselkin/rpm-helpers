#!/usr/bin/python

import json
from sh import repoquery

INTERNAL_REPO = ['mos61']
EXTERNAL_REPO = ['base', 'epel']


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
        if a['epoch'] != b['epoch']:
            return 'NO_MATCH'

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

print 'Items in packages.json - %s' % len(packages.keys())
print 'Items in backrefs.json - %s' % len(backrefs.keys())

fmt_string = '%s; %s; %s:%s-%s; %s; %s; %s; %s; %s\n'
with open('summary.csv', 'w') as f:
    for name in packages.keys():
        found_externally = False
        for repoid in INTERNAL_REPO:
            pkg_int = packages[name][repoid]
            for repoid_ext in EXTERNAL_REPO:
                if repoid_ext not in packages[name]:
                    continue
                found_externally = True
                pkg_ext = packages[name][repoid_ext]
                match = compare_versions(pkg_int, pkg_ext)
                pkg_string = '%s-%s:%s-%s' % (pkg_ext['name'],
                                              pkg_ext['epoch'],
                                              pkg_ext['version'],
                                              pkg_ext['release'])
                f.write(fmt_string % (name,
                                      backrefs[name]['count'],
                                      pkg_int['epoch'],
                                      pkg_int['version'],
                                      pkg_int['release'],
                                      pkg_int['vendor'],
                                      match,
                                      pkg_ext['repoid'],
                                      pkg_string,
                                      pkg_ext['vendor']))
            if not found_externally:
                f.write(fmt_string % (name,
                                      backrefs[name]['count'],
                                      pkg_int['epoch'],
                                      pkg_int['version'],
                                      pkg_int['release'],
                                      pkg_int['vendor'],
                                      'NO_MATCH', '', '', ''))

