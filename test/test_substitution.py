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
        self.assertEqual(str(s.vout), 'a')
        self.assertEqual(set([str(v) for v in s.vin]), set(['b', 'c']))
        # nested and vout not explicitly given
        s = Substitution([self.__f_add, self.__f_mult])
        self.assertEqual(str(s.vout), 'd')
        self.assertEqual(set([str(v) for v in s.vin]), set(['b', 'c']))
        # bad order, need also 'a' as input
        s = Substitution([self.__f_mult, self.__f_add])
        self.assertEqual(str(s.vout), 'a')
        self.assertEqual(set([str(v) for v in s.vin]), set(['a', 'b', 'c']))

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

    def test_diversity(self):
        fa = Function('a', ['a1'], "", name="equals_a")
        fb = Function('b', ['b1'], "", name="equals_b")
        f1 = Function('a', ['b'], "", name="f1")
        se = Substitution([fa])
        s1 = Substitution([fb, f1])
        d_s1 = s1.diversity([se])
        d_se = se.diversity([s1])
        self.assertEqual(d_s1, d_se)
        self.assertEqual(d_s1, 1)
        fc = Function('c', ['c1'], "", name="equals_c")
        f2 = Function('a', ['b', 'c'], "", name="f2")
        s2 = Substitution([fc, fb, f2])
        d = se.diversity([s1, s2])
        self.assertEqual(d, 2)
        d = s1.diversity([s2])
        self.assertEqual(d, 0)
        d = s2.diversity([s1])
        self.assertEqual(d, 1)


if __name__ == '__main__':
        unittest.main()
