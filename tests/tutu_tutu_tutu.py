import socket
import unittest

import re

import requests
from mock import Mock
from seismograph.ext.selenium.polling import do, wrap
from selenium.webdriver.remote.webelement import WebElement

from seismograph.ext.selenium.proxy.proxy import WebElementProxy

from seismograph.ext.selenium.utils import change_name_from_python_to_html

from seismograph.ext.selenium.router import Router

from seismograph.ext.selenium import add_route
from seismograph.ext.selenium.exceptions import RouteNotFound, RouterError
from tests.lib.case import BaseTestCase
from seismograph.ext.selenium.query import QueryObject, ValueFormat, ATTRIBUTE_ALIASES, attribute_by_alias, Expression, \
    ContainsText, TAG_ALIASES, tag_by_alias, QueryResult


class PollingTests(unittest.TestCase):
    def test_import(self):
        from seismograph.ext.selenium.polling import HTTPException as H
        H = None
        self.assertRaises(ImportError, H)

    def a(self):
        return self

    def test_do(self):
        self.assertNotEqual(wrap()(self.a), self.a)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 8000))

        do(requests.get)()()


class RouterTests(unittest.TestCase):
    def setUp(self):
        def a_func(a):
            return a

        def prepare_config_with_project_url():
            mock_file = Mock()
            mock_file.config.PROJECT_URL = "http://FAKE.COM/FAKE/"
            mock_file.browser = {"FAKE": "FAKE"}
            return mock_file

        def prepare_config_without_project_url():
            mock_file = Mock()
            mock_file.config.PROJECT_URL = None
            mock_file.browser = {"FAKE": "FAKE"}
            return mock_file

        self.mock_with = prepare_config_with_project_url
        self.mock_without = prepare_config_without_project_url
        self.func_for_test = a_func

    def tearDown(self):
        Router.__rules__ = {}

    def test_proxy(self):
        router = Router(123)
        router.__proxy = 123
        self.assertEqual(router.__proxy, 123)

    def test_rule(self):
        self.assertDictEqual(Router.__rules__, {})

        Router.add_rule(123, '')
        rule = re.compile(r'^{}$'.format(123))

        self.assertEqual(Router.__rules__[rule], '')

    # Not working
    def test_add_route(self):

        self.assertDictEqual(Router.__rules__, {})

        add_route(123, '')

        rule = re.compile(r'^{}$'.format(123))

        self.assertEqual(add_route(123, ''), None)
        self.assertEqual(Router.__rules__[rule], '')

    def test_get(self):

        mock_file = self.mock_with()

        add_route(1, self.func_for_test)
        add_route(2, self.func_for_test)

        res = Router(mock_file).get('1')

        self.assertEqual(res, mock_file)

    def test_get_except(self):
        mock_file = self.mock_without()

        try:
            Router(mock_file).get('1')
        except RouteNotFound as route_error:
            self.assertEqual(route_error.message, '1')

    def test_get_without_config(self):
        mock_file = Mock()
        mock_file.config.PROJECT_URL = None
        mock_file.browser = {"FAKE": "FAKE"}

        add_route(1, self.func_for_test)
        add_route(2, self.func_for_test)

        try:
            router = Router(mock_file)
            router.go_to('1')
        except RouterError as route_error:
            self.assertEqual(route_error.message, 'Can not go to the URL. Project URL is not set to config.')

    def test_get_page(self):
        mock_file = self.mock_without

        add_route(1, self.func_for_test)
        add_route(2, self.func_for_test)

        router = Router(mock_file)
        res = router.get_page('1')
        self.assertEqual(res, mock_file)


class QueryTests(unittest.TestCase):
    def test_QueryObject_init_method(self):
        query = QueryObject('la', el={"la": 123})
        self.assertEqual(query.tag, 'la')
        self.assertEqual(query.selector, {"el": {"la": 123}})

    def test_QueryObject_str_method(self):
        query = QueryObject('la', el={"la": 123})
        res = query.__str__()
        waited_answer = u'<{} {}>'.format(query.tag, u' '.join((u'{}="{}"'.format(k, v) for k, v in query.selector.items())),)
        self.assertEqual(res, waited_answer)

    def test_QueryObject_call_method(self):
        query = QueryObject('la', el={"la": 123})
        proxy = WebElementProxy(WebElement('1', 1))
        query.__call__(proxy)
        self.assertIsInstance(query, QueryObject)

    def test_tag_by_alias(self):
        awaited_res = TAG_ALIASES.get('kek', 'kek')
        res = tag_by_alias('kek')

        self.assertEqual(res, awaited_res)

        res = tag_by_alias('any')

        self.assertEqual(res, '*')

    def test_attribute_by_alias(self):
        res = change_name_from_python_to_html(
            ATTRIBUTE_ALIASES.get('id', 'id'),
        )
        self.assertEqual(res, attribute_by_alias('id'))

        res = change_name_from_python_to_html(
            ATTRIBUTE_ALIASES.get('one', 'one'),
        )
        self.assertEqual(res, attribute_by_alias('one'))

    def test_ValueFormat_methods(self):
        value = ValueFormat('id')

        try:
            value.__call__()
        except ValueError as value_error:
            self.assertEqual(value_error.message, 'Unknown format')

        value.__format__ = '{attr_value} {attr_name}'
        res = value.__call__('id')
        self.assertEqual(res, '{} {}'.format(value.value, attribute_by_alias('id')))

    def test_Expression_init_method(self):
        expression = Expression()
        self.assertListEqual(expression._expressions, [])

    def test_Expression_expression_method(self):
        expression = Expression(12)
        self.assertEqual(expression.expression(12), expression)

    def test_Expression_with_ValueFormat(self):
        value_format = ValueFormat('id')
        value_format.__format__ = '{attr_value} {attr_name}'

        expression = Expression(value_format)
        self.assertEqual(expression.expression(value_format), expression)

    def test_Expression_with_ContainsText_exept(self):
        try:
            expression = Expression(ContainsText(123))
        except ValueError as error:
            self.assertEqual(error.message, 'Restricted format "ContainsText"')

    def test_Expression_call_method(self):
        expression = Expression(12)
        res = expression.__call__('nice')
        self.assertEqual(res, '[nice="12"]')

    def test_QueryResult_methods(self):
        mock = Mock()
        mock.reason_storage = {'last css query': ''}
        mock.config.POLLING_DELAY = 1.0
        mock.config.POLLING_TIMEOUT = 10.0
        mock.disable_polling = WebElementProxy(WebElement('1', 1)).disable_polling

        query = QueryResult(mock, 'css')
        self.assertIsNotNone(query.__we)
        self.assertIsNotNone(query.__css)
        self.assertIsNotNone(query.__proxy)

        res = query.__repr__()
        self.assertIsNotNone(res)

        res = query.__css_string__()
        self.assertNotEqual(res, query.__css)

        res = query.wait()
        self.assertNotEqual(res, mock)

if __name__ == '__main__':
    unittest.main()
