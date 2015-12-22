

import os
import json
import re

from base import RepodataBase
from urllib import urlretrieve

from sh import rm
from sh import wget
from sh import repoquery
from sh import mkdir

from uuid import uuid4

from tempfile import mkdtemp

from lxml import etree


class Repodata(RepodataBase):
    def __init__(self, **kwargs):
        kwargs.setdefault('dist_type', 'centos')
        RepodataBase.__init__(self, **kwargs)
        self.index_file = 'repodata/repomd.xml'

    def grep_package(self, name, pattern=None):
        self.get_packages(name)

    """
    def get_packages(self, name='-a', repofrompath=[]):
        queryfmt = '{"name":"%{name}","version":"%{version}",' \
                   '"release":"%{release}","vendor":"%{vendor}",' \
                   '"repoid":"%{repoid}","packager":"%{packager}",' \
                   '"epoch":"%{epoch}"'
        queryargs = ['--repofrompath={},{}'.format(self.repo_id, self.cache_dir)]
        for item in repofrompath:
            queryargs.append('--repofrompath=%s' % item)
        queryargs.extend(['--qf', queryfmt, name])

        return [json.loads(line.strip()) for line in repoquery(*queryargs)]
    """

    def get_packages(self, name='-a', repofrompath=[]):
        queryfmt = 'name : %{name}\n' \
                   'epoch : %{epoch}\n' \
                   'version : %{version}\n' \
                   'release : %{release}\n' \
                   'vendor : %{vendor}\n' \
                   'packager : %{packager}\n' \
                   'repoid : %{repoid}\n' \
                   'packager : %{packager}\n' \
                   'summary : %{summary}\n' \
                   'source : %{sourcerpm}\n' \
                   'END_OF_RECORD'
        queryargs = []
        item = '{},{}'.format(self.repo_id, self.cache_dir)
        if item not in repofrompath:
            queryargs.append('--repofrompath=%s' % item)
        for item in repofrompath:
            queryargs.append('--repofrompath=%s' % item)
        queryargs.extend(['--qf', queryfmt, name])

        pkg_info = {}
        for line in repoquery(*queryargs):
            line = line.strip()
            if line == 'END_OF_RECORD':
                yield pkg_info
                pkg_info = {}
            kv = line.split(' : ', 1)
            if len(kv) == 2:
                pkg_info[kv[0]] = kv[1]

    def get_dependencies(self, name, repofrompath=[]):
        queryargs = ['--repofrompath={},{}'.format(self.repo_id, self.cache_dir)]
        for item in repofrompath:
            queryargs.append('--repofrompath=%s' % item)
        queryargs.extend(['--qf', '%{name}', '--resolve', '--requires', name])

        reqs = set()
        for item in repoquery(*queryargs):
            item = item.strip()
            if item != name:
                reqs.add(item)

        return list(reqs)

    def list_group(self, name='', repofrompath=[]):
        queryargs = ['--repofrompath={},{}'.format(self.repo_id, self.cache_dir)]
        for item in repofrompath:
            queryargs.append('--repofrompath=%s' % item)
        queryargs.extend(['--group', '--list', name])

        return [line.strip() for line in repoquery(*queryargs)]

    def update_cache(self):
        if self.repo_url == '':
            print("repo_url is not set, cannot update")
            return

        if not self.test_cache():
            self.purge_cache()
            mkdir(os.path.join(self.cache_dir, 'repodata'))

            index_file_url = '/'.join([self.repo_url, self.index_file])
            index_file_path = os.path.join(self.cache_dir, self.index_file)

            try:
                print("Downloading index file '{0}' --> '{1}' ...".format(
                    index_file_url, index_file_path
                ))
                urlretrieve(index_file_url, index_file_path)
            except:
                self.broken = True
                return

            try:
                xmlroot = etree.parse(index_file_path).getroot()
                xmlns = xmlroot.nsmap[None]
                for item in xmlroot.findall("{{{0}}}data".format(xmlns)):
                    for subitem in item.findall("{{{0}}}location".format(xmlns)):
                        location = subitem.get('href')
                        url = '/'.join([self.repo_url, location])
                        path = '/'.join([self.cache_dir, location])
                        print("Downloading file '{0}' --> '{1}' ...".format(
                            url, path
                        ))
                        urlretrieve(url, path)
            except:
                self.broken = True

