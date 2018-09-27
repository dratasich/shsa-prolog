"""Interface between problog and python.

__date__ = 2018-09-26
__author__ = Denise Ratasich


"""

import re
import problog

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

    def parse_function(self, term):
        """Creates a function object from a function string.

        term -- string with the format: function(vout, relation, [vin1, ..])

        """
        try:
            result = re.search("function\(\s*([0-9a-zA-Z_]*)\s*,\s*([0-9a-zA-Z_]*)\s*,\s*\[(.*)\]\s*\)", term)
            vout = result.group(1)
            relation = result.group(2)
            vin = result.group(3).split(",")
            vin = [v.strip() for v in vin]
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
        try:
            result = re.search("substitution\(\s*([0-9a-zA-Z_]*)\s*,\s*\[(.*)\]\s*\)", term)
            variable = result.group(1)
            subterm = result.group(2)
        except:
            raise RuntimeError("Failed to parse '{}'. {}".format(term, e))
        fcts = __parse_substitution(variable, subterm)
        return Substitution(variable, fcts)

    def __parse_substitution(self, root, term, functions=[]):
        """Recursively parses term for the substitution of root.

        """
        # [..] a substitution with the format: [function(..), input variables]
        # stop condition: root == term or no more starting with a '['
        f = self.__parse_function(term)
        functions.append(f)
        return functions
