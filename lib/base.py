#!/usr/bin/env python

from sh import mkdir
from sh import rm

from uuid import uuid4
from urlparse import urlparse

import os
import time


class RepodataBase(object):
    def __init__(self, repoid='', name='', dist_type='', dist_release='', baseurl='', base_path='/tmp'):
        if repoid == '' and (name == '' or dist_type == '' or dist_release == ''):
            raise Exception('repo_id or (name + dist_type + dist_release) must not be empty strings!')

        if repoid:
            (dist_type, dist_release, name) = repoid.split('-')

        self.name = name
        self.dist_type = dist_type
        self.dist_release = dist_release
        # Base path where files related to the repository are located
        self.base_path = base_path
        self.path = ''
        # Main index file of the repository
        self.index_file = ''

        self.cache_uuid = uuid4()
        self.cache_threshold_sec = 60 * 60

        self.broken = False
        self.repo_id = '%s-%s-%s' % (dist_type, dist_release, name)
        self.repo_url = baseurl

        self.cache_dir = os.path.join(self.base_path, self.repo_id)

    def grep_package(self, name, pattern=None):
        pass

    def test_cache(self):
        index_file_path = os.path.join(self.cache_dir, self.index_file)
        print("Testing index file '{0}'".format(index_file_path))
        if os.path.exists(index_file_path):
            file_age = time.time() - os.path.getctime(index_file_path)
            if file_age > self.cache_threshold_sec:
                print("File '{0}' too old.".format(index_file_path))
                return False
        else:
            print("No such file '{0}'".format(index_file_path))
            return False

        print("Cache is up-to-date (index file updated {0} sec ago).".format(file_age))
        return True

    def update_cache(self):
        pass

    def purge_cache(self):
        if os.path.exists(self.cache_dir):
            rm('-r', '-f', self.cache_dir)
        mkdir('-p', self.cache_dir)

    def __str__(self):
        return self.format("Remote URL: {index_file_url}, "
                           "Cached file: {index_file_path}")

    def format(self, format_string):
        args = {
            'base_path': self.base_path,
            'broken': self.broken,
            'cache_dir': self.cache_dir,
            'cache_threshold_sec': self.cache_threshold_sec,
            'cache_uuid': self.cache_uuid,
            'dist_release': self.dist_release,
            'dist_type': self.dist_type,
            'index_file': self.index_file,
            'index_file_path': os.path.join(self.cache_dir, self.index_file),
            'index_file_url': '/'.join([self.repo_url, self.index_file]),
            'name': self.name,
            'repo_id': self.repo_id,
            'repo_url': self.repo_url,
        }
        return format_string.format(**args)

class RepodataUrl():
    def __init__(self, product_name, product_version='', product_release='',
                dist='', codename='', component='', arch=''):
        if product_name == 'fuel':
            product_release = product_release or 'master'
            product_version = product_version or '6.0'
            dist = dist or 'ubuntu'
        elif product_name == 'ubuntu':
            dist = 'ubuntu'
            product_release = ''
        elif product_name == 'centos':
            dist = 'centos'
            product_release = ''

        if dist == 'ubuntu':
            codename = codename or 'precise'
            component = component or 'main'
            arch = arch or 'amd64'
        elif dist == 'centos':
            arch = arch or 'x86_64'

        self.kwargs = {
            'product_name': product_name,
            'product_version': product_version,
            'product_release': product_release,
            'dist': dist,
            'codename': codename,
            'component': component,
            'arch': arch
        }

        url_prefix = {
            'fuel': 'http://fuel-repository.mirantis.com',
            'osci': '',
            'ubuntu': 'http://archive.ubuntu.com/ubuntu',
            'centos': ''
        }.get(product_name, '')

        url_product_suffix = {
            'fuel-release': 'fwm/{product_version}/{dist}',
            'fuel-stable': 'osci/{dist}-fuel-{product_version}-stable/{dist}',
            'fuel-testing': 'osci/{dist}-fuel-{product_version}-testing/{dist}',
            'fuel-master': 'osci/{dist}-fuel-master/{dist}',
        }.get('{product_name}-{product_release}'.format(**self.kwargs), '')

        url_dist_suffix = {
            'fuel-release-ubuntu': 'dists/{codename}/{component}/binary-{arch}',
            'ubuntu--ubuntu': 'dists/{codename}/{component}/binary-{arch}',
            'fuel-release-centos': 'os/{arch}',
            'centos--centos': 'os/{arch}',
        }.get('{product_name}-{product_release}-{dist}'.format(**self.kwargs), '')

        self.url_prefix = url_prefix
        self.url_suffix = '/'.join([url_product_suffix, url_dist_suffix]).format(**self.kwargs)

        self.url = urlparse(url='/'.join([self.url_prefix, self.url_suffix]))
