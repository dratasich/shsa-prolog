import unittest

from model.problog_interface import ProblogInterface
from model.function import Function
from model.substitution import Substitution
from model.itom import Itom, Itoms


class ImplementationTestCase(unittest.TestCase):
    """Test cases for implementation clauses in a pl-file."""

    def setUp(self):
        self.__pli = ProblogInterface(librarypaths=["model/"])

    def tearDown(self):
        self.__pli = None

    def __get_substitutions(self, query):
        result = self.__pli.evaluate(query)
        S = []
        for k, v in result.items():
            if v == 0.0:
                continue
            s = self.__pli.parse_substitution(str(k))
            S.append(s)
        return S

    def __execute_substitutions(self, S, itoms):
        output = Itoms()
        for i, s in enumerate(S):
            output[s] = s.execute(itoms)
        return output

    def test_implementation_simple(self):
        self.__pli.load("test/test_py-implementation-simple.pl")
        S = self.__get_substitutions("query(substitution(x,S)).")
        # create some dummy data
        x1 = Itom('x1', 2, variable='x')
        x2 = Itom('x2', 2, variable='x')
        a1 = Itom('a1', 1, variable='a')
        b1 = Itom('b1', 1, variable='b')
        c1 = Itom('c1', 1, variable='c')
        d1 = Itom('d1', 4, variable='d')
        itoms = Itoms([x1, x2, a1, b1, c1, d1])
        # execute substitutions
        outputs = self.__execute_substitutions(S, itoms)
        # check
        for output_itoms in outputs.values():
            self.assertAlmostEqual(output_itoms['x'].v, 2)

    def test_implementation_multiline(self):
        self.__pli.reset()
        self.__pli.load("test/test_py-implementation-multiline.pl")
        result = self.__pli.evaluate("query(implementation(r1, X)).")
        relation, code = self.__pli.parse_implementation(list(result)[0])
        self.assertEqual(relation, "r1")
        # create function to execute
        f = Function('a', 'b', code, name='r1')
        itoms = f.execute(Itoms([Itom('b', 1, timestamp=0, variable='b')]))
        self.assertEqual(itoms['a'].v, 2)
        self.assertEqual(itoms['a'].t, 0)
        # execute through substitution
        S = self.__get_substitutions("query(substitution(a,S)).")
        itoms = Itoms([Itom('b1', 1, timestamp=0, variable='b')])
        outputs = self.__execute_substitutions(S, itoms)
        s = list(S)[0]
        self.assertEqual(outputs[s]['a'].v, 2)
        self.assertEqual(outputs[s]['a'].t, 0)

if __name__ == '__main__':
        unittest.main()
