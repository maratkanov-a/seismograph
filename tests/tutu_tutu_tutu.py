import unittest

import re

from mock import Mock

from seismograph.ext.selenium import drivers

from seismograph.ext.selenium import add_route
from seismograph.ext.selenium.browser import BrowserConfig
from seismograph.ext.selenium.exceptions import RouteNotFound, RouterError
from seismograph.ext.selenium.proxy import WebDriverProxy
from tests.lib.case import BaseTestCase, ConfigTestCaseMixin
from selenium.webdriver.remote.webdriver import WebDriver



#
# class PollingTests(unittest.TestCase):
#     # class PollingTests(BaseTestCase):
#     def test_la(self):
#         # def runTest(self):
#         from seismograph.ext.selenium.polling import HTTPException as H
#         H = None
#         self.assertRaises(ImportError, H)
#         # def test_wrapper(self):
#

class RouterTests(BaseTestCase):
# class RouterTests(unittest.TestCase):
    @classmethod
    def a_func(cls, a):
        return a
#     def test_proxy(self):
#         from seismograph.ext.selenium.router import Router
#         router = Router(123)
#         router.__proxy = 123
#         self.assertEqual(router.__proxy, 123)
#
#     def test_rule(self):
#         from seismograph.ext.selenium.router import Router
#         self.assertDictEqual(Router.__rules__, {})
#         Router.add_rule(123, '')
#         rule = re.compile(r'^{}$'.format(123))
#         self.assertEqual(Router.__rules__[rule], '')
#         Router.__rules__ = {}

    # Not working
    def test_add_route(self):
        from seismograph.ext.selenium.router import Router
        self.assertDictEqual(Router.__rules__, {})
        add_route(123, '')
        rule = re.compile(r'^{}$'.format(123))
        self.assertEqual(add_route(123, ''), None)
        self.assertEqual(Router.__rules__[rule], '')
        Router.__rules__ = {}

    def test_get(self):
        from seismograph.ext.selenium.router import Router
        mock_file = Mock()
        mock_file.config.PROJECT_URL = "http://FAKE.COM/FAKE/"
        mock_file.browser = {"FAKE": "FAKE"}

        add_route(1, self.a_func)
        add_route(2, self.a_func)

        res = Router(mock_file).get('1')

        self.assertEqual(res, mock_file)
        Router.__rules__ = {}

    def test_get_2(self):
        from seismograph.ext.selenium.router import Router
        mock_file = Mock()
        mock_file.config.PROJECT_URL = None
        mock_file.browser = {"FAKE": "FAKE"}
        try:
            Router(mock_file).get('1')
        except RouteNotFound as route_error:
            self.assertEqual(route_error.message, '1')
        Router.__rules__ = {}

    def test_get_3(self):
        from seismograph.ext.selenium.router import Router
        mock_file = Mock()
        mock_file.config.PROJECT_URL = None
        mock_file.browser = {"FAKE": "FAKE"}

        add_route(1, self.a_func)
        add_route(2, self.a_func)

        try:
            router = Router(mock_file)
            router.go_to('1')
        except RouterError as route_error:
            self.assertEqual(route_error.message, 'Can not go to the URL. Project URL is not set to config.')
        Router.__rules__ = {}

    def test_get_page(self):
        from seismograph.ext.selenium.router import Router
        mock_file = Mock()
        mock_file.config.PROJECT_URL = None
        mock_file.browser = {"FAKE": "FAKE"}

        add_route(1, self.a_func)
        add_route(2, self.a_func)

        router = Router(mock_file)
        res = router.get_page('1')
        self.assertEqual(res, mock_file)
        Router.__rules__ = {}



# if __name__ == '__main__':
#     unittest.main()
