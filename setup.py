#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
from distutils.core import setup

name = 'OERPLib'
version = '0.5.1'
description = 'OpenERP client library which allows to easily interact with an OpenERP server.'
keywords = "openerp client xml-rpc xml_rpc xmlrpc net-rpc net_rpc netrpc oerplib communication lib library python service web webservice"
author = u"ABF Osiell - Sebastien Alix"
author_email = 'sebastien.alix@osiell.com'
url = 'http://packages.python.org/OERPLib/'
download_url = 'http://pypi.python.org/packages/source/O/OERPLib/OERPLib-%s.tar.gz' % version
license = 'LGPL v3'
doc_build_dir = 'doc/build'
doc_source_dir = 'doc/source'

cmdclass = {}
command_options = {}
# 'build_doc' option
try:
    from sphinx.setup_command import BuildDoc
    if not os.path.exists(doc_build_dir):
        os.mkdir(doc_build_dir)
    cmdclass = {'build_doc': BuildDoc}
    command_options = {
        'build_doc': {
            #'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', version),
            'source_dir': ('setup.py', doc_source_dir),
            'build_dir': ('setup.py', doc_build_dir),
            'builder': ('setup.py', 'html'),
         }}
except Exception:
    print("No Sphinx module found. You have to install Sphinx "
          "to be able to generate the documentation.")

setup(name=name,
      version=version,
      description=description,
      long_description=open('README.txt').read(),
      keywords=keywords,
      author=author,
      author_email=author_email,
      url=url,
      download_url=download_url,
      packages=['oerplib',
                'oerplib.rpc',
                'oerplib.service',
                'oerplib.service.osv'],
      license=license,
      cmdclass=cmdclass,
      command_options=command_options,
      classifiers=[
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
