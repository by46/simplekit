import unittest

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
