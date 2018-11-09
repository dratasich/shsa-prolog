import unittest
from interval import interval

from model.itom import Itom, Itoms
from model.monitor import Monitor


class MonitorTestCase(unittest.TestCase):
    """Test cases for class `Itom` and `Itoms`."""

    def setUp(self):
        self.__itoms1 = Itoms([
            Itom('x1', 10, variable='x'),
            Itom('x2', 10.01, variable='x'),
            Itom('a1', 5, variable='a'),
            Itom('b1', 5.1, variable='b'),
            Itom('c1', 4.95, variable='c'),
            Itom('d1', 19, variable='d'),
        ])
        # no error (all intervals intersect in the common domain)
        self.__itoms2 = Itoms([
            Itom('x1', interval([9, 11]), variable='x'),
            Itom('a1', interval([4.9, 5.1]), variable='a'),
            Itom('b1', interval([4, 6]), variable='b'),
        ])
        # error (d1)
        self.__itoms3 = Itoms([
            Itom('x1', interval([9, 11]), variable='x'),
            Itom('a1', interval([4.9, 5.1]), variable='a'),
            Itom('d1', interval([23, 25]), variable='d'),
            # error because: 9..11 does not inersect with 11.5..12.5
        ])

    def tearDown(self):
        self.__itoms1 = None

    def test_init_monitor(self):
        # minimal initialization
        m = Monitor("test/test_py-monitor-simple.pl", 'x')
        self.assertTrue("function(x, r1, [a])." in m.model)
        self.assertEqual(m.domain, 'x')
        self.assertEqual(m.substitutions, None)
        # update model and domain
        m.update("test/test_py-implementation-multiline.pl", 'a')
        self.assertTrue("function(a, r1, [b])." in m.model)
        self.assertEqual(m.domain, 'a')
        # init with itoms
        m = Monitor("test/test_py-monitor-simple.pl", 'x', itoms=self.__itoms1)
        self.assertEqual(len(m.substitutions), 6)

    def test_monitor(self):
        m = Monitor("test/test_py-monitor-simple.pl", 'x')
        failed = m.monitor(self.__itoms1)
        self.assertEqual(len(m.substitutions), 6)
        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0], 'd1')
        # interval itoms
        # recollect substitutions
        failed = m.monitor(self.__itoms2)
        self.assertEqual(len(m.substitutions), 3)
        self.assertEqual(len(failed), 0)
        # erroneous d1
        failed = m.monitor(self.__itoms3)
        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0], 'd1')


if __name__ == '__main__':
        unittest.main()