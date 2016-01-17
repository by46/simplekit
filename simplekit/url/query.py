import re
import warnings

import six
from six.moves import urllib
from six.moves.urllib.parse import unquote_plus, quote_plus

from .omdict1D import omdict1D
from .util import utf8, callable_attr

__author__ = 'benjamin.c.yan'

VALID_ENCODED_QUERY_KEY_REGEX = re.compile(
    r'^([\w\-\.\~\:\@\!\$\&\'\(\)\*\+\,\;\/\?]|(\%[\da-fA-F][\da-fA-F]))*$')


def is_valid_encoded_query_key(key):
    return bool(VALID_ENCODED_QUERY_KEY_REGEX.match(key))


VALID_ENCODED_QUERY_VALUE_REGEX = re.compile(
    r'^([\w\-\.\~\:\@\!\$\&\'\(\)\*\+\,\;\/\?\=]|(\%[\da-fA-F][\da-fA-F]))*$')


def is_valid_encoded_query_value(value):
    return bool(VALID_ENCODED_QUERY_VALUE_REGEX.match(value))


class Query(object):
    SAFE_KEY_CHARS = "/?:@-._~!$'()*,"
    SAFE_VALUE_CHARS = "/?:@-._~!$'()*,="

    def __init__(self, query='', strict=False):
        self.strict = strict
        self._params = omdict1D()
        self.load(query)

    def load(self, query):
        self.params.load(self.__item(query))
        return self

    def add(self, args):
        for key, value in self.__item(args):
            self.params.add(key, value)

        return self

    def set(self, mapping):
        """
        Adopt all mappings in <mapping>, replacing any existing mappings
        with the same key. If a key has multiple values in <mapping>,
        they are all adopted.

        Examples
        >>> assert Query({1:1}).set([(1,None),(2,2)]).params.allitems() == [(1,None),(2,2)]
        >>> assert Query({1:None,2:None}).set([(1,1),(2,2),(1,11)]).params.allitems() == [(1,1),(2,2),(1,11)]
        >>> assert Query({1:None}).set([(1,[1,11,111])]).params.allitems() == [(1,1),(1,11),(1,111)]

        :param mapping: :class:`dict`
        :return: <self>
        """
        self.params.updateall(mapping)
        return self

    @property
    def params(self):
        return self._params

    def __item(self, items):
        if not items:
            items = []
        elif callable_attr(items, 'allitems'):
            items = list(items.allitems())
        elif callable_attr(items, 'iterallitems'):
            items = list(items.iterallitems())
        elif callable_attr(items, 'items'):
            items = list(six.iteritems(items))
        elif isinstance(items, six.string_types):
            items = self.__extract_items_from_string(items)
        else:
            items = list(items)
        return items

    def __extract_items_from_string(self, query):
        pairs_string = [s2 for s1 in query.split('&') for s2 in s1.split(';')]

        if self.strict:
            pairs = [s1.split('=', 1) for s1 in pairs_string]
            pairs = [(p[0], '' if len(p) == 1 else p[1]) for p in pairs]
            for key, value in pairs:
                valid_key = is_valid_encoded_query_key(key)
                valid_value = is_valid_encoded_query_value(value)
                if not valid_key or not valid_value:
                    s = ("Improperly encoded query string received: '%s'. "
                         "Proceeding, but did you mean '%s'?" %
                         (query, urllib.parse.urlencode(pairs)))
                    warnings.warn(s, UserWarning)

        items = []
        parsed_items = urllib.parse.parse_qsl(query, keep_blank_values=True)
        for (key, value), pair in six.moves.zip(parsed_items, pairs_string):
            if key == unquote_plus(pair):
                value = None
            items.append((key, value))

        return items

    def encode(self):
        delimiter = '&'
        pairs = []
        for key, value in self.params.iterallitems():
            utf8key = utf8(key, utf8(str(key)))
            utf8value = utf8(value, utf8(str(value)))
            quoted_key = quote_plus(utf8key, self.SAFE_KEY_CHARS)
            quoted_value = quote_plus(utf8value, self.SAFE_VALUE_CHARS)
            pair = '='.join([quoted_key, quoted_value])
            if value is None:  # Example: http://sprop.su/?param
                pair = quoted_key
            pairs.append(pair)
        return delimiter.join(pairs)
