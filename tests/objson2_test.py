import unittest

import simplekit.objson


class Dolphin2TestCase(unittest.TestCase):
    def test_multi_object(self):
        text = r'[{"name":"benjamin"}, {"name": "wendy"}]'
        persons = simplekit.objson.loads(text)
        persons = sorted(persons, lambda x, y: x.name < y.name)
        self.assertEqual(u"benjamin", persons[0].name)
        self.assertEqual(u"wendy", persons[1].name)


