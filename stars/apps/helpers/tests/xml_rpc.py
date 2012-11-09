"""Tests for stars.apps.helpers.xml_rpc.
"""
import xmlrpclib

from django.test import TestCase
import testfixtures

from stars.apps.helpers import xml_rpc


class XMLRPCTest(TestCase):

    def test_run_rpc_logging(self):
        """Does run_rpc log a warning if there's no resource found?
        """
        XMLRPC_FAULT_MSG = 'bo-o-o-o-o-gus xmlrpc fault'
        RUN_RPC_ARGS = 'bo-o-o-o-o-gus arg'
        def raiser(*args):
            raise xmlrpclib.Fault(1, XMLRPC_FAULT_MSG)
        def mock_get_server(*args):
            return MockServer()
        with testfixtures.LogCapture('stars') as log:
            with testfixtures.Replacer() as r:
                r.replace('stars.apps.helpers.xml_rpc.get_server',
                          mock_get_server)
                r.replace('stars.apps.helpers.xml_rpc.get_params', raiser)
                xml_rpc.run_rpc(service_name='bo-o-o-o-ogus name',
                                args=RUN_RPC_ARGS)

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'WARNING')
        self.assertEqual(log.records[0].msg, ' '.join((XMLRPC_FAULT_MSG,
                                                       RUN_RPC_ARGS)))


class MockServer(xmlrpclib.ServerProxy):

    def __init__(self):
        self.service_name = 'bo-o-o-o-gus service'
