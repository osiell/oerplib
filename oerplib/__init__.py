# -*- coding: UTF-8 -*-
"""This module defines the :class:`OERP` and :class:`DMS` classes.

The :class:`OERP` class manage the client-side operations which are related to an OpenERP
server. You can use this to write Python programs that performs a variety of
automated jobs that communicate with an OpenERP server.

"""
"""
The :class:`DMS` class manage the Document Management System of an OpenERP server. This one
inherits from `ftplib.FTP <http://docs.python.org/library/ftplib.html>`_ class and has few methods to facilitate some tasks.

"""
import os
import subprocess

from oerplib.oerp import OERP
from oerplib.dms import DMS
from oerplib import error
#
#MSG_ERROR = u"ERREUR"
#MSG_DONE = u"FAIT"
#
#def open_pdf(file_path, pdf_viewer):
#    """Open a PDF file with the PDF Viewer.
#        
#    Keyword arguments:
#    file_path  -- path to the PDF file
#    pdf_viewer -- path to the PDF Viewer executable
#
#    """
#    try:
#        if os.path.exists(file_path):
#            subprocess.Popen(args=[pdf_viewer, file_path])
#    except:
#        raise error.Error(u"Erreur d'ouverture du fichier PDF. \
#Veuillez vérifier si le chemin vers le lecteur PDF est correct.")

