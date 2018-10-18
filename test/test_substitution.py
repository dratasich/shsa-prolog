import unittest

from model.function import Function
from model.substitution import Substitution
from model.itom import Itom, Itoms


class SubstitutionTestCase(unittest.TestCase):
    """Test cases for class `Substitution`."""

    def setUp(self):
        self.__f_add = Function('a', ['b', 'c'], "a.v = b.v + c.v", name="add")
        self.__f_mult = Function('d', ['a'], "d.v = 2 * a.v", name="mult")
        self.__f_add2 = Function('a', ['b', 'c'], "a.v = b.v + c.v", name="add")

    def tearDown(self):
        self.__f_add = None
        self.__f_mult = None

    def test_init(self):
        s = Substitution([self.__f_add])
        self.assertEqual(s.vout, 'a')
        self.assertEqual(set(s.vin), set(['b', 'c']))
        # nested and vout not explicitly given
        s = Substitution([self.__f_add, self.__f_mult])
        self.assertEqual(s.vout, 'd')
        self.assertEqual(set(s.vin), set(['b', 'c']))
        # bad order, need also 'a' as input
        s = Substitution([self.__f_mult, self.__f_add])
        self.assertEqual(s.vout, 'a')
        self.assertEqual(set(s.vin), set(['a', 'b', 'c']))

    def test_execute(self):
        s = Substitution([self.__f_add, self.__f_mult])
        b = Itom('b', 1)
        c = Itom('c', 2)
        itoms = Itoms(list=[b, c])
        variables = s.execute(itoms)
        self.assertEqual(variables['d'].v, 6)
        # function names not unique
        s = Substitution([self.__f_add, self.__f_add2])
        variables = s.execute([b, c])
        self.assertEqual(variables['a'].v, 3)


if __name__ == '__main__':
        unittest.main()
