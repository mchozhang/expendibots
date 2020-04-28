#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import call

for i in range(100):
    call(['python', '-m', 'referee', 'midnight', 'midnight'], shell=False)