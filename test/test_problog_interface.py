import unittest

from model.problog_interface import ProblogInterface
from model.substitution import Substitution


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
        # valid formats
        pli.parse_function("function(a,r1,[b,c])")
        pli.parse_function("function( a , r1 , [b,c])")
        pli.parse_function("function( a , r1 , [ b , c ] )")
        # test initialization of function
        f = pli.parse_function("function( a , r1 , [b,c])")
        self.assertEqual(f.vout, 'a')
        self.assertEqual(set(f.vin), set(['b', 'c']))
        self.assertEqual(f.name, 'r1')
        self.assertEqual(f.code, "a = b + c")
        result = f.execute({'b': -1, 'c': 2})
        self.assertEqual(result['a'], 1)
        # no or ambiguous implementation
        pli.reset()
        with self.assertRaises(Exception):
            f = pli.parse_function("function( a , r1 , [b,c])")
        pli.append('implementation(r1,"a = b + c").')
        pli.append('implementation(r1,"a = b * c").')
        with self.assertRaises(Exception):
            f = pli.parse_function("function( a , r1 , [b,c])")
        # invalid formats
        with self.assertRaises(Exception):
            pli.parse_function("function(a, r1, invalid)")
        with self.assertRaises(Exception):
            pli.parse_function("function(a, r1, [b, c], invalid)")

    def test_parse_substitution(self):
        pli = ProblogInterface()
        pli.append('implementation(r1,"a = b + c").')
        pli.append('implementation(r2,"c = 2 * d").')
        # empty substitution, vout is undefined
        s = pli.parse_substitution("substitution(a,a)")
        self.assertEqual(len(s), 0)
        self.assertEqual(set(s.vin), set())
        s = pli.parse_substitution("substitution(a, [function(a,r1,[b,c]), b, c] )")
        self.assertEqual(len(s), 1)
        self.assertEqual(s.vout, 'a')
        self.assertEqual(set(s.vin), set(['b', 'c']))
        s = pli.parse_substitution("substitution(a, [function(a,r1,[b,c]), b, [function(c,r2,[d]),d]] )")
        self.assertEqual(len(s), 2)
        self.assertEqual(s.vout, 'a')
        self.assertEqual(set(s.vin), set(['b', 'd']))


if __name__ == '__main__':
        unittest.main()
