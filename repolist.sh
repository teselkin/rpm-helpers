#!/bin/bash

repoid=${1}

if [ -z "$repoid" ]; then
    exit 1
fi

formatstring=' {\n  "name": "%{name}",\n  "version": "%{version}",\n  "release": "%{release}",\n  "arch": "%{arch}",\n  "repository": "%{repoid}",\n  "packager": "%{packager}"\n },'

echo '[' > ${repoid}.json
repoquery -a --repoid=${repoid} --qf "${formatstring}"  >> ${repoid}.json
echo '{}]' >> ${repoid}.json

