import unittest

from model.function import Function
from model.substitution import Substitution


class SubstitutionTestCase(unittest.TestCase):
    """Test cases for class `Substitution`."""

    def setUp(self):
        self.__f_add = Function('a', ['b', 'c'], "a = b + c", name="add")
        self.__f_mult = Function('d', ['a'], "d = 2 * a", name="mult")

    def tearDown(self):
        self.__f_add = None
        self.__f_mult = None

    def test_init(self):
        s = Substitution([self.__f_add], vout='a')
        self.assertEqual(s.vout, 'a')
        self.assertEqual(set(s.vin), set(['b', 'c']))
        # nested and vout not explicitly given
        s = Substitution([self.__f_add, self.__f_mult])
        self.assertEqual(s.vout, 'a')
        self.assertEqual(set(s.vin), set(['b', 'c']))
        # bad order, need also 'a' as input
        s = Substitution([self.__f_mult, self.__f_add], vout='a')
        self.assertEqual(set(s.vin), set(['a', 'b', 'c']))

    def test_execute(self):
        s = Substitution([self.__f_add, self.__f_mult], vout='a')
        res = s.execute({'b': 1, 'c': 2})
        self.assertEqual(res['d'], 6)


if __name__ == '__main__':
        unittest.main()
