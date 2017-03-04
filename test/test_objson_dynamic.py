"""
Objson.dynamic class
"""

import unittest

from simplekit.objson.dynamic_class import make_dynamic_class


class ObjsonDynamicClassTestCase(unittest.TestCase):
    def test_make_dynamic_class(self):
        Entity = make_dynamic_class('Entity', 'name, sex, age')
        entity = Entity()
        self.assertTrue(hasattr(entity, 'name'))
        self.assertTrue(hasattr(entity, 'sex'))
        self.assertTrue(hasattr(entity, 'age'))

        entity = Entity()
        entity.name, entity.sex, entity.age = 'benjamin', 'male', 21

        self.assertEqual(entity.name, 'benjamin')
        self.assertEqual(entity.sex, 'male')
        self.assertEqual(entity.age, 21)
