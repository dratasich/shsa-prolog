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
            identifier = pp.Word(pp.alphanums + "_").setResultsName('identifier').setName('identifier')
            alist = pp.Group(list_open + identifier + (delimiter + identifier)*(0,5) + list_close).setResultsName('list')
            parameter = identifier ^ alist
            parameters = pp.Group(parameter + pp.ZeroOrMore(delimiter + parameter)).setResultsName('parameters')
            # function (general)
            function = fct_name + fct_open + parameters + fct_close
            # shsa 'function': function(vout, relation, [vin1, ..])
            vout = identifier.copy().setResultsName('output')
            relation = identifier.copy().setResultsName('relation')
            vin = alist.copy().setResultsName('inputs')
            pl_function = pp.Group(pp.Literal("function").suppress() + fct_open \
                            + vout + delimiter \
                            + relation + delimiter \
                            + vin + fct_close).setResultsName('function')
            self.__function_parser = pl_function
            # shsa 'substitution': substitution(vout,vout) or substitution(vout,[function, inputs])
            # while each input can be substituted by a function again
            substitution = pp.Forward()  # placeholder (substitution used recursively)
            substitution << (
                identifier | \
                pp.Group(list_open + pl_function \
                + pp.OneOrMore(delimiter + substitution).setResultsName('other_substitutions') \
                + list_close).setResultsName('substitution_by_function') \
            )
            pl_substitution = pp.Literal("substitution").suppress() + fct_open \
                                + vout + delimiter \
                                + substitution.setResultsName('substitution') + fct_close
            self.__substitution_parser = pl_substitution
        except Exception as e:
            raise RuntimeError("error parsing")

    def parse_function(self, term):
        """Parses a function string.

        term -- string with the format: function(vout, relation, [vin1, ..])

        """
        try:
            result = self.__function_parser.parseString(term)
        except Exception as e:
            raise RuntimeError("Failed to parse '{}'. {}".format(term, e))
        return self.__get_function_of(result['function'])

    def __get_function_of(self, expr_result):
        """Creates a function object given the parsers result."""
        try:
            vout = expr_result['output']
            relation = expr_result['relation']
            vin = expr_result['inputs']
        except Exception as e:
            raise RuntimeError("Failed to create function from {}. {}".format(expr_result, e))
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
        try:
            result = self.__substitution_parser.parseString(term)
            s = self.__get_substitution_of(result['substitution'])
        except Exception as e:
            raise RuntimeError("Failed to parse '{}'. {}".format(term, e))
        return s

    def __get_substitution_of(self, expr_results):
        """Recursively constructs a substitution object from parsing results.

        The recursion stops when no more function can be detected. In this case
        an empty substitution is returned (no functions). In case of a
        function, this method is called again (recursively) processing the
        inputs of the function first. When it returns the function is
        added. This depth-first approach ensures functions are in the right
        order to be executed. The last function calculates vout of this
        substitution.

        """
        substitution = Substitution()
        # stop condition
        try:
            function = expr_results['function']
            vin_substitutions = expr_results['other_substitutions']
        except Exception as e:
            # no more function to add (it is an identifier only)
            # so return the substitution as it is
            return substitution
        # recursion
        try:
            # first add the substitutions of the inputs
            for s in vin_substitutions:
                substitution.extend(self.__get_substitution_of(s))
            # finally add the function
            substitution.append(self.__get_function_of(function))
        except Exception as e:
            raise e
        return substitution
