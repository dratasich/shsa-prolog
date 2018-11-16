"""Interface between problog and python.

__date__ = 2018-09-26
__author__ = Denise Ratasich


"""

import problog
import pyparsing as pp

from model.function import Function
from model.substitution import Substitution
from model.variable import Variable


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
        # BNF
        # name should at least match 'function' or 'substitution'
        fct_open = pp.Literal("(").suppress()
        fct_close = pp.Literal(")").suppress()
        list_open = pp.Literal("[").suppress()
        list_close = pp.Literal("]").suppress()
        delimiter = pp.Literal(",").suppress()
        # parameters
        identifier = pp.Word(pp.alphanums + "_")
        string = pp.QuotedString('"', multiline=True)
        name = string | identifier
        vlist = pp.Group(list_open + name + pp.ZeroOrMore(delimiter + name) + list_close)
        # shsa 'function': function(vout, relation, [vin1, ..])
        pl_function = pp.Group(pp.Literal("function").suppress() + fct_open \
                        + name('output') + delimiter \
                        + name('relation') + delimiter \
                        + vlist('inputs') + fct_close)
        self.__function_parser = pl_function('function')
        # shsa 'substitution': substitution(vout,vout) or substitution(vout,[function, inputs])
        # while each input can be substituted by a function again
        substitution = pp.Forward()  # placeholder (substitution used recursively)
        substitution << (
            name | \
            pp.Group(list_open + pl_function('function') \
            + pp.OneOrMore(delimiter + substitution).setResultsName('other_substitutions') \
            + list_close).setResultsName('substitution_by_function') \
        )
        pl_substitution = pp.Literal("substitution").suppress() + fct_open \
                            + name('vout') + delimiter \
                            + substitution.setResultsName('substitution') + fct_close
        self.__substitution_parser = pl_substitution
        # itom to variable mapping
        pl_variableOf = pp.Literal("variableOf").suppress() + fct_open \
                        + name('itom') + delimiter \
                        + name('variable') + fct_close
        self.__variableOf_parser = pl_variableOf
        # implementation
        pl_implementation = pp.Literal("implementation").suppress() + fct_open \
                            + name('relation') + delimiter \
                            + string('executable') + fct_close
        self.__implementation_parser = pl_implementation

    def parse_function(self, term):
        """Parses a function string.

        term -- string with the format: function(vout, relation, [vin1, ..])

        """
        result = self.__function_parser.parseString(str(term))
        return self.__get_function_of(result['function'])

    def __get_function_of(self, expr_result):
        """Creates a function object given the parsers result."""
        vout = expr_result['output']
        relation = expr_result['relation']
        vin = expr_result['inputs']
        code = self.__get_code_of(relation)
        return Function(vout, vin, code, name=relation)

    def __get_code_of(self, relation):
        """Returns the code of the relation."""
        result = self.evaluate("query(implementation({},X)).".format(relation))
        if len(result) > 1:
            raise AmbiguousImplementation(relation, result)
        for k, v in result.items():
            if v == 0.0:
                raise NoImplementation(relation)
            # parse query result
            relation, code = self.parse_implementation(k)
            return code
        return ""

    def parse_implementation(self, term):
        """Parses the output of a query 'implementation(relation,code).' and
        returns the relation and code.

        term -- string with the format: implementation(name,string)

        """
        result = self.__implementation_parser.parseString(str(term))
        return result['relation'], result['executable']

    def parse_substitution(self, term):
        """Parses the output of a query 'substitution(root,S).' and returns a
        Substitution object.

        term -- string with the format: substitution(vout,[function..])

        """
        result = self.__substitution_parser.parseString(str(term))
        return self.__get_substitution_of(result['vout'], result['substitution'])

    def __get_substitution_of(self, vout, expr_results):
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
            fct_term = expr_results['function']
        except Exception as e:
            # expr_result does not contain a 'function' (any more)
            # -> it is an itom
            itom_name = str(expr_results)
            code = "# {} = {}\n".format(vout, itom_name)
            # copy (constructor) to copy value and timestamp
            # (we don't know the value and timestamp yet)
            # (value might be an object too -> deepcopy)
            code += "{} = copy.deepcopy({})\n".format(
                vout, Variable.toidentifier(itom_name))
            # change name to variable (its not the original itom!)
            code += "{}.name = '{}'\n".format(vout, vout)
            f = Function(vout, [itom_name], code, name="equals", wrap=False)
            substitution.append(f)
            return substitution
        function = self.__get_function_of(fct_term)
        vin_substitutions = expr_results['other_substitutions']
        assert len(function.vin) == len(vin_substitutions)
        # recursion
        # first add the substitutions of the inputs
        for i, s in enumerate(vin_substitutions):
            substitution.extend(self.__get_substitution_of(function.vin[i], s))
        # finally add the function
        substitution.append(function)
        assert str(substitution.vout) == str(vout)
        return substitution

    def parse_variableOf(self, term):
        """Parses the output of a query 'variableOf(itom,Variable).' and returns the variable.

        term -- string with the format: variableOf(itom,variable)

        """
        result = self.__variableOf_parser.parseString(str(term))
        return result['variable']


class Error(Exception):
    """Base class for Exceptions in this module."""
    pass

class AmbiguousImplementation(Error):
    """Exception raised for multiple `implementation` clauses."""
    pass

class NoImplementation(Error):
    """Exception raised for missing `implementation` clauses."""
    pass
