#!/usr/bin/python

import ConfigParser
import dataset
from lib.rpm_repodata import Repodata
from uuid import uuid4

config = ConfigParser.ConfigParser()
config.read('config.ini')

int_repos = ['centos7-mos']
ext_repos = ['centos7-base']

db = dataset.connect('sqlite:///packages.db')
packages = db['packages']
requires = db['requires']


def init_database(int_repos=[], ext_repos=[]):
    global packages
    global requires

    packages.drop()
    packages = db['packages']
    requires.drop()
    requires = db['requires']

    repos = {}
    repofrompath = []
    for repoid in int_repos + ext_repos:
        if config.has_section('repo:{}'.format(repoid)):
            repo = {}
            for key in config.options('repo:{}'.format(repoid)):
                repo[key] = config.get('repo:{}'.format(repoid), key).strip("'")
            print(repo)
            repos[repoid] = Repodata(name=repo['name'],
                                     dist_type=repo['dist_type'],
                                     dist_release=repo['dist_release'],
                                     baseurl=repo['baseurl'])
            repofrompath.append('{},{}'.format(repoid, repos[repoid].cache_dir))

    for repo in repos.values():
        repo.update_cache()

    for repoid in int_repos:
        for pkg in repos[repoid].get_packages():
            pkg['uuid'] = str(uuid4())
            pkg['backref'] = 0
            for dep_name in repos[repoid].get_dependencies(pkg['name'], repofrompath=repofrompath):
                requires.insert(dict(req_id=pkg['uuid'], req_name=dep_name))
            packages.insert(pkg)
            print pkg['name']


#init_database(int_repos, ext_repos)


for item in packages.all():
    backrefs = requires.count(req_name=item['name'])
    print '{} -> {}'.format(item['name'], backrefs)

results = db.query('SELECT name FROM packages as p join requires as r on p.uuid = r.req_id where r.req_name="wxGTK";')
for item in results:
    print item['name']


results = db.query('select count(*) from packages;')
for item in results:
    print item
