# -*- coding: UTF-8 -*-


class Common(object):
    """RPC Service 'common'"""
    def __init__(self, connector):
        self.connector = connector


class Object(object):
    """RPC Service 'object'"""
    def __init__(self, connector):
        self.connector = connector


class Wizard(object):
    """RPC Service 'wizard'"""
    def __init__(self, connector):
        self.connector = connector


class Report(object):
    """RPC Service 'report'"""
    def __init__(self, connector):
        self.connector = connector


class DB(object):
    """RPC Service 'db'"""
    def __init__(self, connector):
        self.connector = connector

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
