"""Implementation of a (SHSA) function.

__date__ = 2018-09-24
__author__ = Denise Ratasich

"""

import textwrap


class Function(object):
    """Function class."""

    def __init__(self, vout, vin, code, name="fct", wrap=True):
        if len(set(vin) & set([vout])) > 0:
            raise RuntimeError("Not supported: output variable is also an input.")
        self.__vin = vin
        """List of input variables."""
        self.__vout = vout
        """Output variable."""
        self.__code = code
        """Code to be executed which transforms the input variables to the
        output variable."""
        self.__name = name
        """Name of the function."""
        self.__wrap = wrap
        """Indicates if the code shall be wrapped into a function (will be
        called as specified in 'name')."""

    @property
    def vin(self):
        return self.__vin

    @vin.setter
    def vin(self, vin):
        self.__vin = vin

    @property
    def vout(self):
        return self.__vout

    @vout.setter
    def vout(self, vout):
        self.__vout = vout

    @property
    def code(self):
        return self.__enclosed_code()

    @property
    def name(self):
        return self.__name

    def __enclosed_code(self):
        # # prepend utils to code (additional python files with functions
        # # that may be used in the relations)
        # u_code = ""
        # if self.__model.utils is not None:
        #     u_code += "# utils\n\n"
        #     for filename in self.__model.utils:
        #         with open(filename) as f:
        #             u_code += f.read() + "\n"
        # enclose the code with a function such that the code (includes
        # variables, possibly functions) is local in the defined function
        # `execute` (otherwise we would have to call `global fct`)
        code = ""
        if self.__wrap:
            params = ",".join(self.__vin)
            code += "def " + self.__name + "(" + params + "):\n"
            # code += textwrap.indent(u_code, "    ")
            code += textwrap.indent(self.__code, "    ")
            code += "\n    return " + self.__vout
            code += "\n\n" + self.__vout + " = " + self.__name + "(" + params + ")"
        else:
            code += self.__code
        return code

    def execute(self, itoms):
        """Executes the function given the value per input variable.

        itoms -- Dictionary of variable->value.

        """
        # verify inputs
        if not set(self.__vin).issubset(set(itoms.keys())):
            raise RuntimeError("Missing itoms to execute the function.")
        # generate code
        code = self.__enclosed_code()
        # execute code
        local_vars = itoms
        exec(code, None, local_vars)
        return local_vars

    def __str__(self):
        return self.__name

    def __eq__(self, other):
        return (self.__vout == other.__vout) \
            and (set(self.__vin) == set(other.__vin)) \
            and (self.__code == other.__code)

    def __hash__(self):
        return hash((self.__vout, self.__vin, self.__code))
