"""Implementation of a (SHSA) substitution.

__date__ = 2018-09-24
__author__ = Denise Ratasich

This substitution class is similar to the one in the (Python only) shsa
package. The differences are:
- uses the class `Function` to store a relation that can be executed

"""

import re

from model.function import Function
from model.itom import Itoms


class Substitution(list):
    """Substitution class.

    A substitution is a list of functions. The list represents a procedural
    program corresponding to a postfix traversal of an expression tree. Hence,
    calculated in-order (from 0..end), it calculates the output without
    parentheses needed.

    """

    def __init__(self, *args, **kwargs):
        """Initializes a substitution."""
        # initialize list
        super(Substitution, self).__init__(*args, **kwargs)

    @property
    def vout(self):
        """Returns the output variable of the last function."""
        if len(self) == 0:
            return None
        return self[-1].vout

    @property
    def vin(self):
        """Returns the input variables needed to apply this substitutions."""
        if len(self) == 0:
            return set()
        return self.__collect_input_variables()

    @property
    def code(self):
        """Returns code from functions in execution order."""
        string = ""
        for f in self:
            string += f.code
        return string

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
        """Execute the substitution and returns all variables.

        itoms -- dictionary of itom-name->'Itom'-object. These will be passed
          as local variables to the functions.

        Passes itoms through the functions. Output variables of functions may
        be appended (variable-name->'Itom'-object). However, the last variable
        assigned is 'this.vout' which is the result of the substitution given
        the inputs 'itoms'. The value (and possibly a timestamp) of 'this.vout'
        can be retrieved from the returned variables ('this.vout.v').

        """
        # make sure its an Itoms-object
        itoms = Itoms(itoms)
        # verify inputs
        if not set([v.name for v in self.vin]).issubset(
                set([v.name for v in itoms.values()])):
            raise RuntimeError("Missing itoms to execute the substitution.")
        # execute function after function
        for f in self:
            itoms = f.execute(itoms)
        return itoms

    def __str__(self):
        strinputs = "inputs({});".format(self.vin)
        strfcts = [str(f.vout) + "=" \
                   + str(f) + "(" + ",".join([str(v) for v in f.vin]) + ");"
                   for f in self]
        return strinputs + "\n" + "\n".join(strfcts)

    def __hash__(self):
        return hash(self.__str__())

    def diversity(self, other_substitutions):
        """Provides a measure of difference in inputs to the given substitutions.

        substitutions -- list of substitutions to compare to.

        Count the own inputs that are not in another substitution.
        """
        diversity = 0
        my_inputs = self.vin
        for s in other_substitutions:
            difference = my_inputs - s.vin
            diversity = diversity + len(difference)
        return diversity
