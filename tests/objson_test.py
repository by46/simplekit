__author__ = 'Administrator'

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import json
import unittest

from simplekit import objson


class DolphinTestCase(unittest.TestCase):
    def test_loads_basic(self):
        tests = [(r'"ben"', "ben"),
                 ('1', 1),
                 ('3.1415', 3.1415),
                 ('true', True),
                 ('false', False),
                 ('[]', [])]
        for text, expected in tests:
            actual = objson.loads(text)
            self.assertEqual(expected, actual)

    def test_loads_normal(self):
        text = r'{"sort":true, "name":{"first":"benjamin", "last": "yan"}}'
        obj = objson.loads(text)
        self.assertIsNotNone(obj)
        self.assertTrue(obj.sort)
        self.assertEqual("benjamin", obj.name.first)
        self.assertEqual("yan", obj.name.last)

    def test_loads_exceptions(self):
        tests = ["{"]
        for text in tests:
            self.assertIsNone(objson.loads(text))

    def test_loads_exceptions2(self):
        text = r'{"class":true, "def":true, "case":true}'
        obj = objson.loads(text)
        self.assertTrue(obj.mclass)
        self.assertTrue(obj.mdef)
        self.assertTrue(obj.case)

        self.assertTrue(obj['class'])
        self.assertTrue(obj['def'])

        text = r'{"class":true, "mclass":false, "from-cookie": true, "0file":true}'
        obj = objson.loads(text)
        self.assertFalse(obj.mclass)
        self.assertTrue(obj['class'])
        self.assertTrue(obj.from_cookie)
        self.assertTrue(obj['from-cookie'])
        self.assertTrue(obj.m0file)
        self.assertTrue(obj['0file'])

    def test_dumps(self):
        text = r'{"sort":true, "name":{"first":"benjamin", "last": "yan"}}'
        obj = objson.loads(text)
        actual = objson.dumps(obj)
        self.assertDictEqual(json.loads(text), json.loads(actual))

    def test_loads_knapsack(self):
        text = r'{"name":"benjamin", "age":21}'
        obj = objson.loads(text)
        obj2 = objson.loads(text)
        self.assertEqual(type(obj), type(obj2))

        text = r'{"age":21,"name":"benjamin"}'
        obj3 = objson.loads(text)
        self.assertEqual(type(obj), type(obj3))

        text = r'{"age":21,"name":"benjamin1"}'
        obj4 = objson.loads(text)
        self.assertEqual(type(obj), type(obj4))

        text = r'{"name":"benjamin", "age":"21"}'
        obj5 = objson.loads(text)
        self.assertNotEqual(type(obj), type(obj5))

    def test_load_normal(self):
        fp = StringIO(r'{"name":"benjamin", "age":21}')
        obj = objson.load(fp)
        self.assertIsNotNone(obj)
        self.assertEqual("benjamin", obj.name)
        self.assertEqual(21, obj.age)

    def test_dump_normal(self):
        text = r'{"name":"benjamin", "age":21}'
        obj = objson.loads(text)
        fp = StringIO()
        objson.dump(obj, fp)
        self.assertEqual(json.loads(text), json.loads(fp.getvalue()))

    def test_dump_change_value(self):
        text = r'{"name":"benjamin", "age":21}'
        obj = objson.loads(text)
        obj.age = 30
        fp = StringIO()
        objson.dump(obj, fp)
        expected = json.loads(text)
        expected['age'] = 30
        self.assertEqual(expected, json.loads(fp.getvalue()))

    def test_dynamic_class(self):
        team = objson.make_dynamic_class("Team", "name,age,members")
        t = team({'name': 'neweggtech', 'age': 5, 'members': []})
        self.assertEqual('neweggtech', t.name)
        self.assertEqual(5, t.age)

        team = objson.make_dynamic_class("Team", "name,age,age, members")
        t = team({'name': 'neweggtech', 'age': 5, 'members': []})
        self.assertEqual('neweggtech', t.name)
        self.assertEqual(5, t.age)
