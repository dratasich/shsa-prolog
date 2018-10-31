import unittest

from model.function import Function
from model.itom import Itom, Itoms
from interval import interval


class FunctionTestCase(unittest.TestCase):
    """Test cases for class `Function`."""

    def test_init(self):
        f = Function('a', ['b', 'c'], "a = b + c", name="add")
        self.assertEqual(set(f.vin), set(['b', 'c']))
        self.assertEqual(set(f.vout), set(['a']))
        self.assertEqual(f.name, "add")
        with self.assertRaises(Exception):
            f = Function('a', ['a'], "a = 2 * a", name="double")
        # test wrap flag
        self.assertTrue("def" in f.code)
        f = Function('a', ['b', 'c'], "a = b + c", name="add", wrap=False)
        self.assertFalse("def" in f.code)

    def test_execute(self):
        f = Function('a', ['b', 'c'], "a.v = b.v + c.v", name="add")
        a = Itom('a', 0)
        b = Itom('b', 1)
        c = Itom('c', 2)
        itoms = Itoms([a, b, c])
        v = f.execute(itoms)
        self.assertAlmostEqual(v['a'].v, 3)
        b.v = 4; c.v = 2
        v = f.execute(itoms)
        self.assertAlmostEqual(v['a'].v, 6)
        a.v = 0; b.v = 5; c.v = 5
        v = f.execute(itoms)
        self.assertAlmostEqual(v['a'].v, 10)
        with self.assertRaises(Exception):
            f.execute({a.name: a})
        with self.assertRaises(Exception):
            f.execute({b.name: b})
        # test execution without wrapping the code in a function
        f = Function('a', ['b', 'c'], "a.v = b.v + c.v", name="add", wrap=False)
        b.v = 1; c.v = 2
        v = f.execute(itoms)
        self.assertAlmostEqual(v['a'].v, 3)

    def test_equal(self):
        f1 = Function('a', ['b', 'c'], "a = b + c", name="add")
        f2 = Function('a', ['c', 'b'], "a = b + c", name="huhu")
        self.assertTrue(f1 == f2)
        f3 = Function('a', ['c', 'b'], "a = b + c ")
        self.assertFalse(f1 == f3)
        f4 = Function('d', ['b', 'c'], "d = b + c ")
        self.assertTrue(f1 != f4)
        f5 = Function('a', ['b', 'c', 'd'], "a = b + c")
        self.assertTrue(f1 != f5)

    def test_execute_with_interval(self):
        f = Function('a', ['b', 'c'], "a.v = b.v + c.v", name="add")
        b = Itom('b', interval([0.5, 1.5]))
        c = Itom('c', interval([1, 3]))
        o = f.execute(Itoms([b, c]))
        self.assertEqual(o['a'].v, interval([1.5, 4.5]))
        # mix interval arithmetic with scalars
        b = Itom('b', 1)
        o = f.execute(Itoms([b, c]))
        self.assertEqual(o['a'].v, interval([2, 4]))


if __name__ == '__main__':
        unittest.main()
