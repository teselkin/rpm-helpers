#!/usr/bin/python

import json

packages = {}
with open('packages-mos-master.json') as f:
	packages = json.load(f)

requirements = []
with open('rhel-rpm.txt') as f:
	for line in f.readlines():
		requirements.append(line.strip())

for req in requirements:
	if req in packages:
		print('FOUND {} in {}'.format(req, packages[req].keys()))
	else:
		print('NOT_FOUND {}'.format(req))
