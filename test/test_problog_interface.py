import unittest

from model.problog_interface import ProblogInterface, AmbiguousImplementation
from model.substitution import Substitution
from model.itom import Itom, Itoms


class ProblogInterfaceTestCase(unittest.TestCase):
    """Test cases for class `ProblogInterface`."""

    def test_init(self):
        pli = ProblogInterface()
        self.assertEqual(pli.program, "")
        pli.load("test/test_lists.pl")
        self.assertNotEqual(pli.program, "")
        pli = ProblogInterface(["test/test_shsa.pl"], ["model/"])
        self.assertNotEqual(pli.program, "")
        pli.reset()
        self.assertEqual(pli.program, "")
        pli.append("query(itom(X)).")
        self.assertNotEqual(pli.program, "")
        with self.assertRaises(Exception):
            problog = ProblogInterface("test")

    def test_evaluate(self):
        pli = ProblogInterface(["test/test_shsa.pl"], ["model/"])
        # evaluate all queries in test_shsa.pl
        # (testcase -> should all return true)
        result = pli.evaluate()
        self.assertEqual(sum(result.values()), len(result.values()))
        # program without queries
        pli.reset()
        pli.append("itom(a).")
        # evaluate a query without adding it to the program
        result = pli.evaluate("query(itom(X)).")
        self.assertEqual(len(result), 1)

    def test_parse_function(self):
        pli = ProblogInterface()
        # problog needs some clauses to be able to evaluate (e.g., get the code)
        # the code is retrieved from an implementation(relation_name,..) clause
        pli.append('implementation(r1,"a = b + c").')
        pli.append('implementation(rstep,"a = (t - t(a_last))*0.1 + a_last").')
        pli.append('implementation(r2,"a = 2*b").')
        # single input
        f = pli.parse_function("function(a,r2,[b])")
        self.assertEqual(f.vout, 'a')
        self.assertEqual(set(f.vin), set(['b']))
        self.assertEqual(f.name, 'r2')
        result = f.execute({'b': 1})
        self.assertEqual(result['a'], 2)
        # valid formats
        pli.parse_function("function(a,r1,[b,c])")
        pli.parse_function("function( a , r1 , [b,c])")
        pli.parse_function("function( a , r1 , [ b , c ] )")
        pli.parse_function("function( a, rstep, [t, a_last, t(a_last)])")
        # test initialization of function
        f = pli.parse_function("function( a , r1 , [b,c])")
        self.assertEqual(f.vout, 'a')
        self.assertEqual(set(f.vin), set(['b', 'c']))
        self.assertEqual(f.name, 'r1')
        self.assertTrue("a = b + c" in f.code)
        result = f.execute({'b': -1, 'c': 2})
        self.assertEqual(result['a'], 1)
        # no implementation (unknown clause)
        pli.reset()
        with self.assertRaises(Exception):
            f = pli.parse_function("function( a , r1 , [b,c])")
        # ambiguous implementation
        pli.append('implementation(r1,"a = b + c").')
        pli.append('implementation(r1,"a = b * c").')
        with self.assertRaises(AmbiguousImplementation):
            f = pli.parse_function("function( a , r1 , [b,c])")
        # invalid formats (parse errors)
        with self.assertRaises(Exception):
            pli.parse_function("function(a, r1, invalid)")
        with self.assertRaises(Exception):
            pli.parse_function("function(a, r1, [b, c], invalid)")
        # any string as identifiers
        pli.reset()
        b = Itom('/bb/b', [1, 2, 3])
        pli.append('implementation(equal, "a = {}").'.format(b))
        f = pli.parse_function("function(a, equal, [{}]).".format(b))
        v = f.execute([b])
        self.assertEqual(len(v['a'].v), 3)

    def test_parse_substitution(self):
        pli = ProblogInterface()
        s = pli.parse_substitution("substitution(a,a1)")
        self.assertEqual(len(s), 1)
        self.assertEqual(set(s.vin), set(['a1']))
        # simple tests
        pli.append('implementation(r1,"a = b + c").')
        pli.append('implementation(r2,"c = 2 * d").')
        pli.append('implementation(rstep,"a = (t - t(a_last))*0.1 + a_last").')
        s = pli.parse_substitution("substitution(a, [function(a,r1,[b,c]), b1, c1] )")
        self.assertEqual(len(s), 3)
        self.assertEqual(s.vout, 'a')
        self.assertEqual(set(s.vin), set(['b1', 'c1']))
        s = pli.parse_substitution("substitution(a, [function(a,r1,[b,c]), b1, [function(c,r2,[d]),d1]] )")
        self.assertEqual(len(s), 4)
        self.assertEqual(s.vout, 'a')
        self.assertEqual(set(s.vin), set(['b1', 'd1']))
        s = pli.parse_substitution("substitution(a, [function(a,rstep,[t, a_last, t(a_last)]), t_clock, a1_last, t(a1_last)] )")
        self.assertEqual(len(s), 4)
        self.assertEqual(s.vout, 'a')
        self.assertEqual(set(s.vin), set(['t_clock', 'a1_last', 't(a1_last)']))

    def test_parse_and_execute_substitution(self):
        pli = ProblogInterface()
        pli.append('implementation(r1, "x.v = 2 * a.v").')
        # parse
        s = pli.parse_substitution("substitution(x, [function(x,r1,[a]), a1] )")
        self.assertEqual(s.vout, 'x')
        self.assertEqual(set(s.vin), set(['a1']))
        self.assertEqual(len(s), 2)
        # execute
        a1 = Itom('a1', 1)
        result = s.execute(Itoms([a1]))
        self.assertEqual(result['x'].v, 2)
        # ambiguous implementation
        pli.append('implementation(r1, "x.v = 4 * a.v").')
        with self.assertRaises(AmbiguousImplementation):
            s = pli.parse_substitution("substitution(x, [function(x,r1,[a]), a1] )")
        # no implementation
        pli.reset()
        with self.assertRaises(Exception):
            s = pli.parse_substitution("substitution(x, [function(x,r1,[a]), a1] )")
        # any string as itom identifiers
        pli.reset()
        b = Itom('/p2os/sonar', [1, 2, 3])
        pli.append('implementation(min, "a.v = min(b.v)").')
        s = pli.parse_substitution("substitution(a, [function(a, min, [b]), {}]).".format(b))
        print(s)
        v = s.execute([b])
        self.assertEqual(v['a'].v, 1)

    def test_parse_variableOf(self):
        pli = ProblogInterface()
        v = pli.parse_variableOf("variableOf(a1,a)")
        self.assertEqual(v, 'a')

    def test_parse_implementation(self):
        pli = ProblogInterface()
        relation, execstr = pli.parse_implementation('implementation(r1,"a = 2*b")')
        self.assertEqual(relation, 'r1')
        self.assertEqual(execstr, "a = 2*b")


if __name__ == '__main__':
        unittest.main()
