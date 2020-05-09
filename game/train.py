#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import call

for i in range(1500):
    call(['python', '-m', 'referee', 'midnight', 'midnight'], shell=False)
    # call(['python', '-m', 'referee', 'test', 'midnight'], shell=False)
