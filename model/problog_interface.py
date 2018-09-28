"""Interface between problog and python.

__date__ = 2018-09-26
__author__ = Denise Ratasich


"""

import re
import problog
import pyparsing as pp

from model.function import Function
from model.substitution import Substitution


class ProblogInterface(object):
    """Interface to problog."""

    def __init__(self, plfiles=[], librarypaths=[]):
        """Initializes the interface."""
        self.reset()
        # models may need the path to custom libraries
        for path in librarypaths:
            problog.library_paths.append(path)
        # concatenate problog (program) files
        for plfile in plfiles:
            self.load(plfile)
        # create parsers for problog
        self.__init_problog_parser()

    @property
    def program(self):
        """Returns the problog program."""
        return self.__program

    def reset(self):
        self.__program = ""
        """Problog program to query."""

    def load(self, problogfile):
        """Appends the program of a problog file."""
        with open(problogfile, 'r') as f:
            program = f.read()
        self.__program += program

    def append(self, programstr):
        """Appends problog code to the program."""
        self.__program += programstr + "\n"

    def evaluate(self, appendstr=""):
        model = problog.program.PrologString(
            self.__program + "\n" + appendstr + "\n")
        result = problog.get_evaluatable().create_from(model).evaluate()
        return result

    def __init_problog_parser(self):
        # matches variable/relation names
        try:
            # BNF
            # name should at least match 'function' or 'substitution'
            fct_name = pp.Word(pp.alphas + "_").setResultsName('function')
            fct_open = pp.Literal("(").suppress()
            fct_close = pp.Literal(")").suppress()
            list_open = pp.Literal("[").suppress()
            list_close = pp.Literal("]").suppress()
            delimiter = pp.Literal(",").suppress()
            # parameters
            identifier = pp.Word(pp.alphanums + "_").setResultsName('identifier')
            alist = pp.Group(list_open + identifier + (delimiter + identifier)*(0,5) + list_close).setResultsName('list')
            parameter = identifier ^ alist
            parameters = pp.Group(parameter + (delimiter + parameter)*(0,5)).setResultsName('parameters')
            # function (general)
            function = fct_name + fct_open + parameters + fct_close
            # shsa 'function': function(vout, relation, [vin1, ..])
            vout = identifier.copy().setResultsName('output')
            relation = identifier.copy().setResultsName('relation')
            vin = alist.copy().setResultsName('inputs')
            shsa_function = pp.Literal("function").suppress() + fct_open \
                            + vout + delimiter \
                            + relation + delimiter \
                            + vin + fct_close
            self.__function_parser = shsa_function
        except Exception as e:
            raise RuntimeError("error parsing")

    def parse_function(self, term):
        """Creates a function object from a function string.

        term -- string with the format: function(vout, relation, [vin1, ..])

        """
        try:
            result = self.__function_parser.parseString(term)
            vout = result['output']
            relation = result['relation']
            vin = result['inputs']
        except Exception as e:
            raise RuntimeError("Failed to parse '{}'. {}".format(term, e))
        code = self.__get_code_of(relation)
        return Function(vout, vin, code, name=relation)

    def __get_code_of(self, relation):
        """Returns the code of the relation."""
        result = self.evaluate("query(implementation({},X)).".format(relation))
        if len(result) > 1:
            raise RuntimeError("Ambiguous implementation for relation {}.".format(relation))
        for k, v in result.items():
            if v == 0.0:
                raise RuntimeError("No code for relation {}.".format(relation))
            # parse query result
            result = re.search("implementation\({},\s*\"(.*)\"\s*\)".format(relation), str(k))
            if result is None:
                raise RuntimeError("Failed to parse '{}'.".format(k))
            return result.group(1)
        return ""

    def parse_substitution(self, term):
        """Parses the output of a query 'substitution(root,S).' and returns a
        Substitution object.

        term -- string with the format: substitution(vout,[function..])

        """
        pass
