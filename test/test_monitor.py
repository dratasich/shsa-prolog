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
            Itom('d1', interval([19.5, 20.5]), variable='d'),
        ])
        # error (d1)
        self.__itoms2_err = Itoms([
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
        # static availability (itomsOf are part of the model)
        m = Monitor("test/test_py-monitor-static.pl", 'x')
        self.assertEqual(len(m.substitutions), 3)

    def test_monitor(self):
        m = Monitor("test/test_py-monitor-simple.pl", 'x')
        failed = m.monitor(self.__itoms1)
        self.assertEqual(len(m.substitutions), 6)
        self.assertTrue(failed in m.substitutions)
        self.assertTrue('d1' in failed.vin)
        # interval itoms
        # recollect substitutions
        failed = m.monitor(self.__itoms2)
        self.assertEqual(len(m.substitutions), 3)
        self.assertEqual(failed, None)
        # erroneous
        failed = m.monitor(self.__itoms2_err)
        self.assertTrue('d1' in failed.vin)

    def test_monitor_filter(self):
        # trigger error after the second error in succession
        m = Monitor("test/test_py-monitor-simple.pl", 'x', filter_window_size=3)
        failed = m.monitor(self.__itoms2)
        self.assertEqual(failed, None)
        failed = m.monitor(self.__itoms2)
        self.assertEqual(failed, None)
        failed = m.monitor(self.__itoms2_err)
        self.assertEqual(failed, None)
        failed = m.monitor(self.__itoms2_err)
        self.assertNotEqual(failed, None)


if __name__ == '__main__':
        unittest.main()
