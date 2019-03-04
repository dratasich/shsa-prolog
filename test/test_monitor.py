import unittest
from interval import interval

from model.itom import Itom, Itoms
from model.monitor import Monitor, BayesMonitor


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
        self.assertNotEqual(m.substitutions, None)
        self.assertEqual(len(m.substitutions), 6)
        # static availability (itomsOf are part of the model)
        m = Monitor("test/test_py-monitor-static.pl", 'x')
        self.assertNotEqual(m.substitutions, None)
        self.assertEqual(len(m.substitutions), 3)

    def test_monitor(self):
        m = Monitor("test/test_py-monitor-simple.pl", 'x')
        failed = m.monitor(self.__itoms1)
        self.assertEqual(len(m.substitutions), 6)
        self.assertTrue(failed in m.substitutions)
        self.assertTrue('d1' in [v.name for v in failed.vin])
        # interval itoms
        # recollect substitutions
        failed = m.monitor(self.__itoms2)
        self.assertEqual(len(m.substitutions), 3)
        self.assertEqual(failed, None)
        # erroneous
        failed = m.monitor(self.__itoms2_err)
        self.assertTrue('d1' in [v.name for v in failed.vin])

    def test_monitor_filter(self):
        # trigger error after the second error in succession
        m = Monitor("test/test_py-monitor-simple.pl", 'x', median_filter_window_size=3)
        failed = m.monitor(self.__itoms2)
        self.assertEqual(failed, None)
        failed = m.monitor(self.__itoms2)
        self.assertEqual(failed, None)
        failed = m.monitor(self.__itoms2_err)
        self.assertEqual(failed, None)
        failed = m.monitor(self.__itoms2_err)
        self.assertNotEqual(failed, None)

    def test_debug(self):
        m = Monitor("test/test_py-monitor-simple.pl", 'x')
        # check callback invocation
        class Callback(object):
            def __init__(self):
                self.called = False
            def callback(self, itoms, outputs, values, error, failed):
                self.called = True
        c = Callback()
        m.set_debug_callback(c.callback)
        m.monitor(self.__itoms2)
        self.assertTrue(c.called)
        # check variables we get for debugging
        def clbk(itoms, outputs, values, error, failed):
            self.assertEqual(self.__itoms2, itoms)
            self.assertEqual(len(values), 3)
            self.assertEqual(len(error), 3)  # error for each substitution
            self.assertEqual(sum(error), 0)  # no error
        m.set_debug_callback(clbk)
        m.monitor(self.__itoms2)

    def test_time_uncertainty(self):
        m = Monitor("test/test_py-monitor-simple.pl", 'x')
        # itoms with uncertainties in time
        iok = Itoms([
            Itom('x1', interval([9, 11]), timestamp=interval([0.1, 0.2]), variable='x'),
            Itom('a1', interval([5, 6]), timestamp=interval([0.15, 0.25]), variable='a'),
            Itom('b1', interval([4, 8]), timestamp=interval([0.1, 0.3]), variable='b'),
        ])
        failed = m.monitor(iok)
        self.assertEqual(failed, None)
        # some itoms timestamps do not overlap
        ilate = Itoms([
            Itom('x1', interval([9, 11]), timestamp=interval([0.0, 0.09]), variable='x'),
            Itom('a1', interval([5, 6]), timestamp=interval([0.15, 0.25]), variable='a'),
            Itom('b1', interval([4, 8]), timestamp=interval([0.1, 0.3]), variable='b'),
        ])
        failed = m.monitor(ilate)
        self.assertEqual(failed, None)

    def test_monitor_with_delay_model(self):
        m = Monitor("test/test_py-monitor-delay-simple.pl", 'x')
        # delayed step function (x1 is slower than a1)
        i0 = Itoms([Itom('a1', 0, variable='a'), Itom('x1', 0, variable='x')])
        i1 = Itoms([Itom('a1', 1, variable='a'), Itom('x1', 0, variable='x')])
        i2 = Itoms([Itom('a1', 1, variable='a'), Itom('x1', 1, variable='x')])
        failed = m.monitor(i0)
        self.assertEqual(failed, None)
        failed = m.monitor(i0)
        self.assertEqual(failed, None)
        failed = m.monitor(i1)
        self.assertEqual(failed, None)
        # x1 (value is still 0) doesn't follow a1 (v=1)
        failed = m.monitor(i1)
        self.assertNotEqual(failed, None)
        failed = m.monitor(i2)
        self.assertEqual(failed, None)
        # delay = 2 timesteps
        m = Monitor("test/test_py-monitor-delay-general.pl", 'x')
        failed = m.monitor(i0)
        self.assertEqual(failed, None)
        failed = m.monitor(i0)
        self.assertEqual(failed, None)
        failed = m.monitor(i1)
        self.assertEqual(failed, None)
        failed = m.monitor(i1)
        self.assertEqual(failed, None)
        failed = m.monitor(i1)
        self.assertNotEqual(failed, None)
        failed = m.monitor(i2)
        self.assertEqual(failed, None)


if __name__ == '__main__':
        unittest.main()
