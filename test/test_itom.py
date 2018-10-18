import unittest

from model.itom import Itom, Itoms


class ItomTestCase(unittest.TestCase):
    """Test cases for class `Itom` and `Itoms`."""

    def test_init_itom(self):
        a = Itom('a', 0)
        self.assertEqual(a.v, 0)
        self.assertEqual(a.t, None)
        a.v = 1
        a.t = 0
        self.assertEqual(a.v, 1)
        self.assertEqual(a.t, 0)
        a.v = 0
        self.assertEqual(a.v, 0)
        self.assertEqual(a.t, None)
        b = Itom('b1', 1, variable='b')
        self.assertEqual(b.variable, 'b')
        c = Itom('c', 2.1)
        self.assertAlmostEqual(c.v, 2.1)

    def test_init_itoms(self):
        a = Itom('a', 0)
        b = Itom('b', 1, variable='b')
        c = Itom('c', 2.1)
        l = Itoms(list=[a, b, c])
        self.assertEqual(len(l), 3)
        self.assertEqual(l['a'].v, 0)
        l = Itoms([a, b, c])
        self.assertEqual(len(l), 3)
        self.assertEqual(l['b'].v, 1)


if __name__ == '__main__':
        unittest.main()
