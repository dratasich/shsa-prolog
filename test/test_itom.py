import unittest

from model.itom import Itom, Itoms
from interval import interval


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
        empty = Itoms()
        a = Itom('a', 0)
        b = Itom('b', 1, variable='b')
        c = Itom('c', 2.1)
        l = Itoms(list=[a, b, c])
        self.assertEqual(len(l), 3)
        self.assertEqual(l['a'].v, 0)
        l = Itoms([a, b, c])
        self.assertEqual(len(l), 3)
        self.assertEqual(l['b'].v, 1)

    def test_availability(self):
        a1 = Itom('a1', 0, variable='a')
        a2 = Itom('a2', 1, variable='a')
        b1 = Itom('b1', 2.1, variable='b')
        itoms = Itoms([a1, a2, b1])
        av = itoms.availability
        self.assertEqual(len(av.keys()), 2)
        self.assertEqual(len(av['a']), 2)
        self.assertTrue('a1' in [itom.name for itom in av['a']])
        self.assertEqual(len(av['b']), 1)

    def test_interval(self):
        a = Itom('a', interval([0.9, 1.1]))
        self.assertTrue(1 in a.v)


if __name__ == '__main__':
        unittest.main()
