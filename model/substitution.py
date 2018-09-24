"""Implementation of a (SHSA) substitution.

__date__ = 2018-09-24
__author__ = Denise Ratasich

This substitution class is similar to the one in the (Python only) shsa
package. The differences are:
- initialized with the output of a Prolog query
- uses the class `Function` to store a relation that can be executed

"""

import re

from model.function import Function


class Substitution(object):
    """Substitution class."""

    def __init__(self, root, term):
        """Initializes a substitution."""
        self.__root = root
        """Variable to substitute."""
        self.__functions = self.__parse_substitution(root, term)
        """(Ordered) list of functions. When executed in order, the final result is the
        variable root."""
        self.__vin = self.__collect_input_variables()
        """Input variables of the substitution."""

    @property
    def input_variables(self):
        """Returns the input variables needed to apply this substitutions."""
        return self.__vin

    def execute(self, itoms):
        # go through all functions and pass on the result
        # add result to itoms?
        # (concat all function strings and execute)
        pass

    def __parse_substitution(self, root, term):
        """Recursively parses term for the substitution of root."""
        # [..] a substitution with the format: [function(..), input variables]
        # stop condition: root == term or no more starting with a '['
        f = self.__parse_function(term)
        return [f]

    def __parse_function(self, term):
        """Creates a function object from a string.

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
        return Function(vout, vin, code)

    def __get_code_of(self, relation):
        # TODO: get code of relation
        # problog query implementation(rel,X)?!
        return ""

    def __collect_input_variables(self):
        """Returns the list of input variables.

        Input variables have no substitute, i.e., there exists no function in
        this substitution.

        """
        pass

    def __str__(self):
        res = ""
        for f in self.__functions:
            res += str(f) + "\n"
        return res

    def __hash__(self):
        return hash(self.__functions)
