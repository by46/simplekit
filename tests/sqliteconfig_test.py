import os
import os.path
import tempfile
import unittest

from simplekit.config import SQLiteConfig, Config

__author__ = 'benjamin.c.yan'

BASIC_LOG_HOME = "."
BASIC_FILE_SIZE = 21


class ConfigTestCase(unittest.TestCase):
    def test_config(self):
        config = Config(os.path.dirname(__file__))
        config.from_object(__name__)

        self.assertEqual(".", config["BASIC_LOG_HOME"])
        self.assertEqual(21, config["BASIC_FILE_SIZE"])

        self.assertDictEqual({'log_home': '.', 'file_size': 21}, config.get_namespace('BASIC_'))
        self.assertDictEqual({'BASIC_LOG_HOME': '.', 'BASIC_FILE_SIZE': 21},
                             config.get_namespace('BASIC_', lowercase=False, trim_namespace=False))
        self.assertDictEqual({'basic_log_home': '.', 'basic_file_size': 21},
                             config.get_namespace('BASIC_', trim_namespace=False))

        config = Config(os.path.dirname(__file__))
        config.from_pyfile("saber.cfg")
        self.assertEqual(".", config["BASIC_LOG_HOME"])
        self.assertEqual(21, config["BASIC_FILE_SIZE"])

        config = Config(os.path.dirname(__file__))
        config.from_json("saber.json")
        self.assertEqual(".", config["BASIC_LOG_HOME"])
        self.assertEqual(21, config["BASIC_FILE_SIZE"])


class SQLiteConfigTestCase(unittest.TestCase):
    filename = 'config.db'

    def test_config_normal(self):
        tmp = tempfile.mktemp(prefix='cabinet', suffix='testing')
        os.makedirs(tmp)

        full_path = os.path.join(tmp, self.filename)
        config = SQLiteConfig(full_path, default=dict(name='benjamin', sex='male', age=28))
        config.close()

        self.assertEqual('benjamin', config.name)
        self.assertEqual('male', config.sex)
        self.assertEqual(28, config.age)

        config = SQLiteConfig(full_path)

        self.assertEqual('benjamin', config.name)
        self.assertEqual('male', config.sex)
        self.assertEqual(28, config.age)
        config.close()
        os.remove(full_path)
        os.removedirs(tmp)

    def test_config_save(self):
        tmp = tempfile.mktemp(prefix='cabinet', suffix='testing')
        os.makedirs(tmp)

        full_path = os.path.join(tmp, self.filename)
        config = SQLiteConfig(full_path)
        config.name = 'benjamin'
        config.age = 28
        config['sex'] = 'male'
        config.close()

        config = SQLiteConfig(full_path)

        self.assertEqual('benjamin', config.name)
        self.assertEqual('male', config.sex)
        self.assertEqual(28, config.age)

        del config.age
        del config['sex']
        config.close()

        config = SQLiteConfig(full_path)

        self.assertEqual('benjamin', config.name)
        self.assertEqual(None, config.sex)
        self.assertEqual(None, config.age)

        config.close()

        os.remove(full_path)
        os.removedirs(tmp)

    def test_get_namespace(self):
        tmp = tempfile.mktemp(prefix='cabinet', suffix='testing')
        os.makedirs(tmp)

        full_path = os.path.join(tmp, self.filename)
        config = SQLiteConfig(full_path, default=dict(generic_name='benjamin', generic_sex='male', generic_age=28))

        namespace = config.get_namespace('generic_')
        self.assertDictEqual(dict(name='benjamin', sex='male', age=28), namespace)

        config.close()

        os.remove(full_path)
        os.removedirs(tmp)
