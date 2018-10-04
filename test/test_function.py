import unittest

from model.function import Function


class FunctionTestCase(unittest.TestCase):
    """Test cases for class `Function`."""

    def test_init(self):
        f = Function('a', ['b', 'c'], "a = b + c", name="add")
        self.assertEqual(set(f.vin), set(['b', 'c']))
        self.assertEqual(set(f.vout), set(['a']))
        self.assertEqual(f.name, "add")
        with self.assertRaises(Exception):
            f = Function('a', ['a'], "a = 2 * a", name="double")

    def test_execute(self):
        f = Function('a', ['b', 'c'], "a = b + c", name="add")
        v = f.execute({'b': 1, 'c': 2})
        self.assertAlmostEqual(v['a'], 3)
        v = f.execute({'b': 4, 'c': 2})
        self.assertAlmostEqual(v['a'], 6)
        v = f.execute({'a': 0, 'b': 5, 'c': 5})
        self.assertAlmostEqual(v['a'], 10)
        with self.assertRaises(Exception):
            f.execute({'a': 0})
        with self.assertRaises(Exception):
            f.execute({'b': 0})

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


if __name__ == '__main__':
        unittest.main()
