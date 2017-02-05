import unittest

from simplekit.common import percent
from simplekit.common import sizeof_fmt


class FsTestCase(unittest.TestCase):
    def test_sizeof_fmt(self):
        size = 10
        expect = '10'
        actual = sizeof_fmt(size)
        self.assertEqual(actual, expect)

        size = 1024
        expect = '1.0 K'
        actual = sizeof_fmt(size)
        self.assertEqual(actual, expect)

        size = 1024 * 1024 + 1
        expect = '1.0 M'
        self.assertEqual(sizeof_fmt(size), expect)

    def test_percent(self):
        total = 1024
        value = 512
        expect = 50.0
        actual = percent(value, total)
        self.assertEqual(actual, expect)

        expect = 50.0
        actual = percent(value, total, precision=3)
        self.assertEqual(actual, expect)

        total = 3
        value = 1
        expect = 33.33
        actual = percent(value, total)
        self.assertEqual(actual, expect)

        expect = 33.333
        actual = percent(value, total, precision=3)
        self.assertEqual(actual, expect)

        expect = 33.33
        actual = percent(value, total, precision=-1)
        self.assertEqual(actual, expect)

        expect = 33.33
        actual = percent(value, total, precision=None)
        self.assertEqual(actual, expect)
