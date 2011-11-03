.. _download-install:

Download and install instructions
=================================

Python Package Index (PyPI)
---------------------------

You can download the package from the
`Python Package Index <http://pypi.python.org/pypi/OERPLib/>`_ or install the
latest release this way::

You can install OERPLib with the `easy_install` tool::

    $ easy_install oerplib

Or with `pip`::

    $ pip install oerplib

An alternative way is to download the tarball from
`Python Package Index <http://pypi.python.org/pypi/OERPLib/>`_ page,
and install manually (replace `X.Y.Z` accordingly)::

    $ wget https://bitbucket.org/SebAlix/python-oerplib/downloads/OERPLib-X.Y.Z.tar.gz
    $ tar xzvf OERPLib-X.Y.Z.tar.gz
    $ cd OERPLib-X.Y.Z
    $ python setup.py install

No dependency is required.

Source code from the Mercurial repository
-----------------------------------------

The project is hosted in a BitBucket repository. To get the code, just type::

    $ hg clone https://bitbucket.org/SebAlix/python-oerplib

..
    
    On Debian-based systems
    -----------------------
    
    On Debian, just type in a root shell::
    
        # apt-get install python-oerplib
    
    On Ubuntu::
    
        $ sudo apt-get install python-oerplib

