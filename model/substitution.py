"""Implementation of a (SHSA) substitution.

__date__ = 2018-09-24
__author__ = Denise Ratasich

This substitution class is similar to the one in the (Python only) shsa
package. The differences are:
- uses the class `Function` to store a relation that can be executed

"""

import re
from collections import UserList

from model.function import Function


class Substitution(UserList):
    """Substitution class.

    A substitution is a list of functions. The list represents a procedural
    program corresponding to a postfix traversal of an expression tree. Hence,
    calculated in-order (from 0..end), it calculates the output without
    parentheses needed.

    """

    def __init__(self, *args, **kwargs):
        """Initializes a substitution."""
        # defaults
        self.__vout = None
        """Variable to substitute."""
        # extract substitution related arguments
        if 'vout' in kwargs.keys():
            self.__vout = kwargs['vout']
            del kwargs['vout']
        # initialize list
        super(Substitution, self).__init__(*args, **kwargs)
        # depending on the list of functions: vout and vin can be derived
        self.__update()

    @property
    def vout(self):
        """Returns the output of the last function in the list of substitutions."""
        return self.__vout

    @property
    def vin(self):
        """Returns the input variables needed to apply this substitutions."""
        return list(self.__vin)

    def __add__(self, item):
        super(Substitution, self).__add__(item)
        self.__update()

    def __update(self):
        """Updates the private variables, that are only helpers avoiding re-computation
        when retrieved."""
        if len(self) == 0:
            return
        self.__vout = self[-1].vout
        self.__collect_input_variables(self)

    def __collect_input_variables(self):
        """Returns the set of input variables.

        Input variables have no substitute, i.e., there exists no function in
        this substitution.

        """
        vin = set()
        vout = set()
        for f in self:
            vin.update(set(f.vin) - vout)
            vout.add(f.vout)
        return vin

    def execute(self, itoms):
        # verify inputs
        if not self.__vin.issubset(set(itoms.keys())):
            raise RuntimeError("Missing itoms to execute the substitution.")
        # execute function after function
        for f in self:
            itoms = f.execute(itoms)
        return itoms

    def __str__(self):
        strfcts = [f.vout + "=" \
                   + str(f) + "(" + ",".join(f.vin) + ");"
                   for f in self]
        return "\n".join(strfcts)

    def __hash__(self):
        return hash(self.__functions)
