#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import call

for i in range(10):
    call(['python', '-m', 'referee', 'agent', 'agent'], shell=False)