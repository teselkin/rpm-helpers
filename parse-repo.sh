#!/bin/bash

repoid=${1}

if [ -z "$repoid" ]; then
    exit 1
fi

csvstring='%{name}; %{version}; %{repoid}'

repoquery -a --repoid=${repoid} --qf "${csvstring}" \
| while IFS=';' read -a rec; do
    reqs=''
    for req in $(repoquery --qf '%{name}' --resolve --requires ${rec[0]} | sort -u); do
        if [ "${req}" != "${rec[0]}" ]; then
            reqs="$reqs $req"
        fi
    done
    echo "${rec[0]}; ${rec[1]}; ${rec[2]}; ${reqs}"
done

