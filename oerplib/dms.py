# -*- coding: UTF-8 -*-
from ftplib import FTP
import os
import tempfile

from oerplib.oerp import error

class DMS(FTP, object):
    """ EXPERIMENTAL, NOT TESTED OR DOCUMENTED!
    Represents the Document Management System of an OpenERP server.
    Inherits from FTP class.
    """
    def __init__(self, server, port):
        super(DMS, self).__init__()
        self.server = server
        self.port = port

    def login(self, user="anonymous", pwd="", acct=""):
        try:
            super(DMS, self).connect(self.server, self.port)
        except Exception as exc:
            raise error.DMSConnectionError(u"FTP connection failed. " + \
                                u"Check the DMS service of OpenERP server " + \
                                u"or connection settings")
        try:
            super(DMS, self).login(user, pwd, acct)
        except Exception as exc:
            raise error.DMSConnectionError(u"Wrong login ID or password")

    def get(self, file_name):
        """ Download a file from the OpenERP DMS Service (FTP Server)
            and return its temporary client-side path.

        """
        try:
            (ft_no, ft_name) = tempfile.mkstemp(prefix='oerplib_')
            ft_obj = file(ft_name, 'wb+')
            super(DMS, self).retrbinary('RETR {0}'.format(file_name),
                                        ft_obj.write)
        except:
            raise error.DMSConnectionError(u"The download of the file" + \
                                u"'{0}' has failed.".format(file_name))
        else:
            return ft_name
        finally:
            #outfile.close()
            ft_obj.close()
            os.close(ft_no)
        return None

#    def reset(self, path):
#        """ Reset FTP root directory """
#        #FIXME e.g. path = 'Documents/Production/
#        self.cwd('/{0}/{1}'.format(oerp.config.DATABASE, path))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
