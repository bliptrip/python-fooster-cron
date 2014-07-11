#!/usr/bin/env python3
from distutils.core import setup

from cron import name, version

setup(
	name=name,
	version=version,
	description='A small cron-like scheduler in Python',
	license='MIT',
	author='Foster McLane',
	author_email='fkmclane@gmail.com',
	packages=['cron'],
)
