#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from distutils.core import setup

name = 'OERPLib'
version = '0.3'
release = '0.3.0'
description = 'OpenERP client library which allows to easily interact with an OpenERP server.'
author = u"ABF Osiell - Sébastien Alix"
author_email = 'sebastien.alix@osiell.com'
url = 'http://www.osiell.com/'
download_url = 'http://pypi.python.org/packages/source/O/OERPLib/OERPLib-%s.tar.gz' % release,
#download_url = 'https://bitbucket.org/SebAlix/python-oerplib/downloads'
license = 'LGPL v3'

cmdclass = {}
command_options = {}
# 'build_sphinx' option
try:
    from sphinx.setup_command import BuildDoc
    cmdclass = {'build_sphinx': BuildDoc}
    command_options={
        'build_sphinx': {
            #'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', release),
            'source_dir': ('setup.py', 'doc/source'),
            'build_dir': ('setup.py', 'doc/'),
         }}
except Exception:
    print("No Sphinx module found. You have to install Sphinx to be able to generate the documentation.")

setup(name=name,
      version=release,
      description=description,
      long_description=open('README.txt').read(),
      author=author,
      author_email=author_email,
      url=url,
      download_url=download_url,
      packages=['oerplib', 'oerplib.test'],
      license=license,
      cmdclass=cmdclass,
      command_options=command_options,
      )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
