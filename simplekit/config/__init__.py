import errno
import functools
import json
import logging
import os.path
import sqlite3
import sys
import types

import six

__author__ = 'benjamin.c.yan'


def import_string(import_name, silent=False):
    """Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).

    If `silent` is True the return value will be `None` if the import fails.

    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
                   `None` is returned instead.
    :return: imported object
    """
    # force the import name to automatically convert to strings
    # __import__ is not able to handle unicode strings in the fromlist
    # if the module is a package
    import_name = str(import_name).replace(':', '.')
    try:
        try:
            __import__(import_name)
        except ImportError:
            if '.' not in import_name:
                raise
        else:
            return sys.modules[import_name]

        module_name, obj_name = import_name.rsplit('.', 1)
        try:
            module = __import__(module_name, None, None, [obj_name])
        except ImportError:
            # support importing modules not yet set up by the parent module
            # (or package for that matter)
            module = import_string(module_name)

        try:
            return getattr(module, obj_name)
        except AttributeError as e:
            raise ImportError(e)

    except ImportError as e:
        if not silent:
            raise e


class Config(dict):
    def __init__(self, root_path, default=None):
        dict.__init__(self, default or {})
        self.root_path = root_path

    def from_pyfile(self, filename, silent=False):
        """Updates the values in the config from a Python file.  This function
        behaves as if the file was imported as module with the
        `from_object` function.

        :param filename: the filename of the config.  This can either be an
                         absolute filename or a filename relative to the
                         root path.
        :param silent: set to ``True`` if you want silent failure for missing
                       files.
        """
        filename = os.path.join(self.root_path, filename)
        d = types.ModuleType("config")
        d.__file__ = filename
        try:
            with open(filename, 'r') as config_file:
                exec (compile(config_file.read(), filename, 'exec'), d.__dict__)
        except IOError as e:
            if silent and e.errno in (errno.EISDIR, errno.ENOENT):
                return False
            e.strerror = "Unable to load configuration file (%s)" % e.strerror
            raise
        self.from_object(d)
        return True

    def from_object(self, obj):
        """Updates the values from the given object.  An object can be of one
        of the following one types:

        -   an actual object reference: that object is used directly

        Objects are usually either modules or classes.

        Just the uppercase variables in that object are stored in the config.
        Example usage::

            from yourapplication import default_config
            app.config.from_object(default_config)

        You should not use this function to load the actual configuration but
        rather configuration defaults.  The actual config should be loaded
        with :meth:`from_pyfile` and ideally from a location not within the
        package because the package might be installed system wide.

        :param obj: an import name or object
        """
        if isinstance(obj, six.string_types):
            obj = import_string(obj)

        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def from_json(self, filename, silent=False):
        """Updates the values in the config from a JSON file. This function
        behaves as if the JSON object was a dictionary and passed to the
        :meth:`from_mapping` function.

        :param filename: the filename of the JSON file.  This can either be an
                         absolute filename or a filename relative to the
                         root path.
        :param silent: set to ``True`` if you want silent failure for missing
                       files.

        """
        filename = os.path.join(self.root_path, filename)
        try:
            with open(filename) as json_file:
                obj = json.load(json_file)
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise

        return self.from_mapping(obj)

    def from_mapping(self, *mapping, **kwargs):
        """Updates the config like :meth:`update` ignoring items with non-upper
        keys.
        """
        mappings = []
        if len(mapping) == 1:
            if hasattr(mapping[0], 'items'):
                mappings.append(mapping[0].items())
            else:
                mappings.append(mapping[0])
        elif len(mapping) > 1:
            raise TypeError('expected at most 1 positional argument, got %d' % len(mapping))

        mappings.append(kwargs.items())
        for mapping in mappings:
            for key, value in mapping:
                if key.isupper():
                    self[key] = value
        return True

    def get_namespace(self, namespace, lowercase=True, trim_namespace=True):
        """Returns a dictionary containing a subset of configuration options
        that match the specified namespace/prefix. Example usage:
            app.config['IMAGE_STORE_TYPE']='fs'
            app.config['IMAGE_STORE_PATH']='/var/app/images'
            app.config['IMAGE_STORE_BASE_URL']='http://img.website.com'

        The result dictionary `image_store` would look like:
            {
            'type': 'fs',
            'path': '/var/app/images',
            'base_url':'http://image.website.com'
            }
        This is often useful when configuration options map directly to keyword arguments in functions or class constructors.

        :param namespace: a configuration namespace
        :param lowercase: a flag indicating if the keys of the resulting
            dictionary should be lowercase
        :param trim_namespace: a flag indicating if the keys of the resulting
            dictionary should not include the namespace
        :return: a dict instance
        """
        rv = {}
        for key, value in six.iteritems(self):
            if not key.startswith(namespace):
                continue
            if trim_namespace:
                key = key[len(namespace):]
            else:
                key = key
            if lowercase:
                key = key.lower()
            rv[key] = value
        return rv

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict.__repr__(self))


def auto_commit(fn):
    @functools.wraps(fn)
    def tmp(self, *args, **kwargs):
        connection = sqlite3.connect(self.db_full_path)
        cursor = connection.cursor()
        try:
            kwargs['cursor'] = cursor
            fn(self, *args, **kwargs)
        finally:
            cursor.close()
            connection.commit()
            connection.close()

    return tmp


class SQLiteConfig(dict):
    """Configuration with SQLite file

    Provide retrieve, update, and delete ``(key, value)`` pair style configuration.
    Any changed will save to SQLite file.

    Basic Usage::
        >>> import simplekit.config
        >>> config = simplekit.config.SQLiteConfig('configuration.db', default=dict(name='benjamin'))
        >>> assert config.name == 'benjamin'
        >>> config.age = 21
        >>> config['high'] = 175
        >>> config.close()
        >>> config = simplekit.config.SQLiteConfig('configuration.db')
        >>> assert config.name == 'benjamin'
        >>> assert config.age == 21
        >>> assert config['age'] == 21
        >>> assert config.high == 175
        >>> assert config['high'] == 175
        >>> del config.age
        >>> del config['high']
        >>> assert config.age is None
        >>> assert config.high is None
        >>> config.generic_name = 'benjamin'
        >>> config.generic_age = 27
        >>> config.generic_high = 175
        >>> groups = config.get_namespace('generic_')
        >>> assert groups == dict(name='benjamin', age=27, high=175)
    """

    def __init__(self, db_full_path, default=None, logger=None):
        """initialize a configuration instance.

        :param db_full_path: SQLite file's full path which save the configuration
        :param default: :class:`dict`, default configuration for new configuration base.
        """
        if not logger:
            logger = logging.getLogger('app')

        self.__logger = logger

        self.__db_full_path = db_full_path

        if not os.path.exists(db_full_path):
            self.__create_db(db_full_path, default)
        else:
            self.__load()

    @property
    def logger(self):
        return self.__logger

    @property
    def db_full_path(self):
        return self.__db_full_path

    def get_namespace(self, namespace, lowercase=True, trim_namespace=True):
        """Returns a dictionary containing a subset of configuration options

        that match the specified namespace/prefix. Example usage::
            app.config['IMAGE_STORE_TYPE']='fs'
            app.config['IMAGE_STORE_PATH']='/var/app/images'
            app.config['IMAGE_STORE_BASE_URL']='http://img.website.com'

        The result dictionary `image_store` would look like::
            {
            'type': 'fs',
            'path': '/var/app/images',
            'base_url':'http://image.website.com'
            }

        This is often useful when configuration options map directly to keyword arguments in functions
        or class constructors.

        :param namespace: a configuration namespace
        :param lowercase: a flag indicating if the keys of the resulting
            dictionary should be lowercase
        :param trim_namespace: a flag indicating if the keys of the resulting
            dictionary should not include the namespace
        :return: a dict instance

        """
        rv = {}
        for key, value in six.iteritems(self):
            if not key.startswith(namespace):
                continue
            if trim_namespace:
                key = key[len(namespace):]
            else:
                key = key
            if lowercase:
                key = key.lower()
            rv[key] = value
        return rv

    def close(self):
        pass

    def update(self, *args, **kwargs):
        raise NotImplementedError()

    def __setitem__(self, key, value):
        self.__update_key(key, value)
        super(SQLiteConfig, self).__setitem__(key, value)

    def __delitem__(self, key):
        self.__delete_key(key)
        super(SQLiteConfig, self).__delitem__(key)

    def __getattr__(self, key):
        return self.get(key)

    def __setattr__(self, key, value):
        if not key.startswith('_'):
            self[key] = value
        else:
            self.__dict__[key] = value

    def __delattr__(self, key):
        if not key.startswith('_'):
            if key in self:
                del self[key]
        else:
            del self.__dict__[key]

    @auto_commit
    def __load(self, cursor=None):
        cursor.execute('SELECT key, value, type FROM profile')
        for key, value, type_string in cursor:
            try:
                # TODO(benjamin): optimize code, especially security checking
                value = eval('%s("%s")' % (type_string, value))
            except ValueError:
                pass

            super(SQLiteConfig, self).__setitem__(str(key), value)

    @auto_commit
    def __create_db(self, db_full_path, default=None, cursor=None):
        try:
            create_sql = """
            CREATE TABLE IF NOT EXISTS profile
                (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                key TEXT, value TEXT, type TEXT);
            """
            cursor.execute(create_sql)
        except sqlite3.DatabaseError, e:
            # TODO(benjamin): log error
            self.logger.error("create db %s error: %s" % (db_full_path, e))
            raise e

        # TODO(benjamin): valid checking
        if default:
            text = "INSERT INTO profile(key, value, type) VALUES(?, ?, ?)"
            params = [(key, value, type(value).__name__) for key, value in default.items()]
            cursor.executemany(text, params)
            super(SQLiteConfig, self).update(default)

    @auto_commit
    def __update_key(self, key, value, cursor=None):
        cursor.execute('SELECT 1 FROM profile WHERE key=?', (key,))
        if cursor.rowcount == 1:
            text = 'UPDATE profile SET value=?, type=? WHERE key=?'
            data = (value, type(value).__name__, key)
        else:
            text = 'INSERT INTO profile(key,value,type) VALUES(?, ?, ?)'
            data = (key, value, type(value).__name__)
        cursor.execute(text, data)

    @auto_commit
    def __delete_key(self, key, cursor=None):
        cursor.execute('DELETE FROM profile WHERE key=?', (key,))
