# flake8: noqa
from __future__ import absolute_import, division, print_function, with_statement
from weixin.test.util import unittest


class ImportTest(unittest.TestCase):
    def test_import_everything(self):
        # Some of our modules are not otherwise tested.  Import them
        # all (unless they have external dependencies) here to at
        # least ensure that there are no syntax errors.
        import weixin.auth
        import weixin.autoreload
        import weixin.concurrent
        # import tornado.curl_httpclient  # depends on pycurl
        import weixin.escape
        import weixin.gen
        import weixin.http1connection
        import weixin.httpclient
        import weixin.httpserver
        import weixin.httputil
        import weixin.ioloop
        import weixin.iostream
        import weixin.locale
        import weixin.log
        import weixin.netutil
        import weixin.options
        import weixin.process
        import weixin.simple_httpclient
        import weixin.stack_context
        import weixin.tcpserver
        import weixin.template
        import weixin.testing
        import weixin.util
        import weixin.web
        import weixin.websocket
        import weixin.wsgi

    # for modules with dependencies, if those dependencies can be loaded,
    # load them too.

    def test_import_pycurl(self):
        try:
            import pycurl
        except ImportError:
            pass
        else:
            import weixin.curl_httpclient
