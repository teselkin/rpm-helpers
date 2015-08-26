
import os

from base import RepodataBase

from sh import awk
from sh import grep_dctrl
from sh import gzip
from sh import rm
from sh import wget
from sh import mkdir

from tempfile import mkdtemp

from utils import pushd


class Repodata(RepodataBase):
    def __init__(self, repo_url, base_path=None):
        RepodataBase.__init__(self, url=repo_url, base_path=base_path)

        self.index_file = 'Packages'

        self.path = os.path.normpath(os.path.join(self.base_path,
                                                  self.repo_url.url.netloc,
                                                  self.repo_url.url_suffix))

    def grep_package(self, name, pattern=None):
        pattern = pattern if pattern else "{0}"
        try:
            return [
                line.rstrip().split(' ', 1)
                for line in awk(
                    grep_dctrl(
                        '--field', 'Package,Provides',
                        '--show-field', 'Package,Version',
                        '--eregex', '--ignore-case',
                        '--pattern', pattern.format(name),
                        os.path.join(self.path, self.index_file)
                    ),
                    '/Package/{p=$2;next} /Version/{print p " " $2}'
                )
            ]
        except Exception as err:
            #print(str(err))
            return []

    def update_cache(self):
        if not self.test_cache():
            rm(self.path, '-rf')
            mkdir('-p', self.path)

            index_file_url = '/'.join([self.repo_url.url.geturl(), 'Packages.gz'])
            index_file_path = os.path.join(self.path, self.index_file)

            print("Downloading index file '{0}' --> '{1}' ...".format(
                index_file_url, index_file_path
            ))
            try:
                with pushd(self.path):
                    wget(index_file_url, '-O', self.index_file + '.gz')
                    gzip('-d', self.index_file + '.gz')
            except Exception as err:
                print(str(err))
                self.broken = True
