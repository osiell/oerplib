#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from sphinx.setup_command import BuildDoc
from distutils.core import setup

name = 'OERPLib'
version = '0.1'
release = '0.1.1'
description = 'Python library which allows to easily interact with an OpenERP server.'
author = u"ABF Osiell - Sébastien Alix"
author_email = 'sebastien.alix@osiell.com'
url = 'http://www.osiell.com/'
#download_url = 'http://pypi.python.org/packages/source/o/oerplib/oerplib-%s.tar.gz' % version,
license = 'LGPL v3'

setup(name=name,
      version=release,
      description=description,
      long_description=open('README.txt').read(),
      author=author,
      author_email=author_email,
      url=url,
      #download_url=download_url,
      packages=['oerplib', 'oerplib.test'],
      license=license,
      # 'build_sphinx' option
      cmdclass={'build_sphinx': BuildDoc},
      command_options={
            'build_sphinx': {
                #'project': ('setup.py', name),
                'version': ('setup.py', version),
                'release': ('setup.py', release),
                'source_dir': ('setup.py', 'doc/source'),
                'build_dir': ('setup.py', 'doc/'),
            }},
      )

