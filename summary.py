#!/usr/bin/python

import json
import re

import sys
reload(sys)
sys.setdefaultencoding('utf8')

from lib.rpm_repodata import Repodata

INTERNAL_REPO = ['mos61']
EXTERNAL_REPO = ['base', 'extras', 'updates', 'epel']

re_nvr = r'([\w\-]+)-((\d+\:)??[\w\.]*(?=\d+)[\w\.]*)-([\w\.]*(?=\d+)[\w\.]*)'


def compare_versions(a, b):
    # version_GT == a > b
    # version_LT == a < b
    try:
        aa = a['version'].split('.')
        bb = b['version'].split('.')
        for x in range(0, min(len(aa), len(bb))):
            if aa[x] == bb[x]:
                continue
            if ('%s%s' % (aa[x], bb[x])).isdigit():
                if int(aa[x]) > int(bb[x]):
                    return 'VERSION_GT'
                else:
                    return 'VERSION_LT'
            else:
                if aa[x] > bb[x]:
                    return 'VERSION_GT'
                else:
                    return 'VERSION_LT'

        if len(aa) > len(bb):
            return 'VERSION_GT'

        if len(aa) < len(bb):
            return 'VERSION_LT'

        if a['release'] != b['release']:
            return 'VERSION_MATCH'
    except:
        return 'BAD_DATA'

    return 'FULL_MATCH'


repos = {}
#repos['base'] = Repodata(repoid='centos-7-base')
#repos['epel'] = Repodata(repoid='centos-7-epel')
repos['mos61'] = Repodata(repoid='centos-6.6-mos61')


with open('packages.json') as f:
    packages = json.load(f)

with open('packages-ext.json') as f:
    packages_ext = json.load(f)

with open('backrefs.json') as f:
    backrefs = json.load(f)

with open('ownership.json') as f:
    ownership = json.load(f)

with open('master-node-pkgs.json') as f:
    master_node_pkgs = json.load(f)

with open('master-node-packages.txt.json') as f:
    master_node_packages = json.load(f)

groups = {}
requirements_rpm = []
with open('requirements-rpm.txt') as f:
    for line in f.readlines():
        line = line.strip()
        if line.startswith('@'):
            name = line[1:]
            groups[line] = repos['mos61'].list_group(name)
            continue
        match = re.match(re_nvr, line)
        if match:
            requirements_rpm.append(match.group(1))
        else:
            requirements_rpm.append(line)

print 'Items in packages.json - %s' % len(packages.keys())
print 'Items in packages_ext.json - %s' % len(packages_ext.keys())
print 'Items in backrefs.json - %s' % len(backrefs.keys())
#print 'Groups %s' % groups

rec_template = {
    'name': '',
    'backrefs': '',
    'version_evr': '',
    'vendor': '',
    'match': '',
    'owner': '',
    'comment': '',
    'ext_repoid': '',
    'ext_pkg_name': '',
    'ext_vendor': '',
    'reason': '',
    'summary': '',
    'source': '',
}
summary = []
for name in packages.keys():
    for repoid in INTERNAL_REPO:
        pkg_int = packages[name][repoid]
        rec = {}
        for repoid_ext in EXTERNAL_REPO:
            if repoid_ext not in packages_ext.get(name, {}):
                continue

            pkg_ext = packages_ext[name][repoid_ext]

            rec = {}
            rec.update(rec_template)
            rec['name'] = name
            rec['backrefs'] = backrefs[name]['count']
            rec['version_evr'] = '{version}-{release}'.format(**pkg_int)
            rec['vendor'] = pkg_int['vendor']
            rec['source'] = pkg_int['source']
            rec['summary'] = pkg_int['summary']
            rec['match'] = compare_versions(pkg_int, pkg_ext)
            rec['ext_repoid'] = pkg_ext['repoid']
            rec['ext_pkg_name'] = '{name}-{version}-{release}'.format(**pkg_ext)
            rec['ext_vendor'] = pkg_ext['vendor']
            summary.append(rec)

        if rec.get('name', '') == '':
            rec.update(rec_template)
            rec['name'] = name
            rec['backrefs'] = backrefs[name]['count']
            rec['version_evr'] = '{version}-{release}'.format(**pkg_int)
            rec['match'] = 'NOT_FOUND'
            rec['vendor'] = pkg_int['vendor']
            rec['source'] = pkg_int['source']
            rec['summary'] = pkg_int['summary']
            summary.append(rec)

for rec in summary:
    for group in groups.keys():
        if rec['name'] in groups[group]:
            rec['reason'] = group
    if rec['name'] in requirements_rpm:
        rec['reason'] = 'FUEL_MAIN'
    for reason in master_node_pkgs.keys():
        if rec['name'] in master_node_pkgs[reason]:
            rec['reason'] = reason
    for reason in master_node_packages.keys():
        if rec['name'] in master_node_packages[reason]:
            rec['reason'] = reason

    for owner in ownership.keys():
        if rec['name'] in ownership[owner]:
            rec['owner'] = owner
            break

fmt_string = '{name};{summary};{owner};{comment};{backrefs};{reason};' \
             '{source};{version_evr};{vendor};{match};{ext_repoid};' \
             '{ext_pkg_name};{ext_vendor}\n'
header = {
    'name': 'Name',
    'owner': 'Owner',
    'comment': 'Comment',
    'backrefs': 'Backrefs',
    'source': 'Source',
    'summary': 'Summary',
    'reason': 'Reason',
    'version_evr': 'Version',
    'vendor': 'Vendor',
    'packager': 'Packager',
    'match': 'Match Ext',
    'ext_repoid': 'Ext Repo',
    'ext_pkg_name': 'Ext Package',
    'ext_vendor': 'Ext Vendor',
}
with open('summary.csv', 'w') as f:
    f.write(fmt_string.format(**header))
    for record in summary:
        f.write(fmt_string.format(**record))
