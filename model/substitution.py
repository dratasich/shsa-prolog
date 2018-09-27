"""Implementation of a (SHSA) substitution.

__date__ = 2018-09-24
__author__ = Denise Ratasich

This substitution class is similar to the one in the (Python only) shsa
package. The differences are:
- uses the class `Function` to store a relation that can be executed

"""

import re

from model.function import Function


class Substitution(object):
    """Substitution class.

    A substitution is a list of functions. The list represents a procedural
    program corresponding to a postfix traversal of an expression tree. Hence,
    calculated in-order (from 0..end), it calculates the output without
    parentheses needed.

    """

    def __init__(self, root, functions):
        """Initializes a substitution."""
        self.__vout = root
        """Variable to substitute."""
        self.__functions = functions
        """(Ordered) list of functions. When executed in order, the final result is the
        variable root."""
        self.__vin = self.__collect_input_variables()
        """Set of input variables of the substitution."""

    @property
    def output_variable(self):
        return self.__vout

    @property
    def input_variables(self):
        """Returns the input variables needed to apply this substitutions."""
        return list(self.__vin)

    def __collect_input_variables(self):
        """Returns the set of input variables.

        Input variables have no substitute, i.e., there exists no function in
        this substitution.

        """
        vin = set()
        vout = set()
        for f in self.__functions:
            vin.update(set(f.input_variables) - vout)
            vout.add(f.output_variable)
        return vin

    def execute(self, itoms):
        # verify inputs
        if not self.__vin.issubset(set(itoms.keys())):
            raise RuntimeError("Missing itoms to execute the substitution.")
        # generate code: concat all functions
        for f in self.__functions:
            itoms = f.execute(itoms)
        return itoms

    def __str__(self):
        strfcts = [f.output_variable + "=" \
                   + str(f) + "(" + ",".join(f.input_variables) + ");"
                   for f in self.__functions]
        return "\n".join(strfcts)

    def __hash__(self):
        return hash(self.__functions)
