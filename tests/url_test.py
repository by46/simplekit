import unittest

import simplekit.url as url


class UrlTestCase(unittest.TestCase):
    def test_join_path_segments(self):
        tests = [(['a'], ['b'], ['a', 'b']),
                 (['a', ''], ['b'], ['a', 'b']),
                 (['a'], ['', 'b'], ['a', 'b']),
                 (['a', ''], ['', 'b'], ['a', '', 'b']),
                 (['a', 'b'], ['c', 'd'], ['a', 'b', 'c', 'd'])]
        for base, segments, expected in tests:
            actual = url.join_path_segments(base, segments)
            self.assertListEqual(expected, actual)

    def test_remove_path_segments(self):
        tests = [(['', 'a', 'b', 'c'], ['b', 'c'], ['', 'a', '']),
                 (['', 'a', 'b', 'c'], ['', 'b', 'c'], ['', 'a'])]
        for base, segments, expected in tests:
            actual = url.remove_path_segments(base, segments)
            self.assertListEqual(expected, actual)

    def test_url(self):
        raw = 'http://www.google.com.hk/search?title=benjamin&age=27#/target'
        u = url.URL(raw)
        self.assertEqual(raw, u.url)
        u.netloc = 'www.google.com'
        self.assertEqual(raw.replace('.hk', ''), u.url)
        u.query.add(dict(name='wendy', high=175))

        raw = 'http://www.google.com/search?title=benjamin&age=27&high=175&name=wendy#/target'
        self.assertEqual(raw, u.url)
