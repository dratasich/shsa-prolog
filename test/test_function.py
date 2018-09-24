import unittest

from model.function import Function


class FunctionTestCase(unittest.TestCase):
    """Test cases for class `Function`."""

    def setUp(self):
        self.__f1 = Function('a', ['b', 'c'], "a = b + c", name="add")

    def tearDown(self):
        self.__f1 = None

    def test_execute(self):
        result = self.__f1.execute({'b': 1, 'c': 2})
        self.assertAlmostEqual(result, 3,
                               "wrong execute result")
        result = self.__f1.execute({'b': 4, 'c': 2})
        self.assertAlmostEqual(result, 6,
                               "wrong execute result")
        result = self.__f1.execute({'a': 0, 'b': 5, 'c': 5})
        self.assertAlmostEqual(result, 10,
                               "wrong execute result")
        with self.assertRaises(Exception):
            self.__f1.execute({'a': 0})
        with self.assertRaises(Exception):
            self.__f1.execute({'b': 0})

    def test_equal(self):
        f2 = Function('a', ['c', 'b'], "a = b + c", name="huhu")
        self.assertTrue(self.__f1 == f2)
        f3 = Function('a', ['c', 'b'], "a = b + c ")
        self.assertFalse(self.__f1 == f3)
        f4 = Function('d', ['b', 'c'], "d = b + c ")
        self.assertTrue(self.__f1 != f4)
        f5 = Function('a', ['b', 'c', 'd'], "a = b + c")
        self.assertTrue(self.__f1 != f5)


if __name__ == '__main__':
        unittest.main()
