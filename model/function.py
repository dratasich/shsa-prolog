"""Implementation of a (SHSA) function.

__date__ = 2018-09-24
__author__ = Denise Ratasich

"""

import textwrap3 as textwrap
from model.variable import Variable, Variables
from model.itom import Itom, Itoms
import copy
import interval


class Function(object):
    """Function class."""

    def __init__(self, vout, vin, code, name="fct", wrap=True):
        """Initialize a function.

        vout -- output variable
        vin -- list/set of input variables
        code -- python executable string
        name -- name of the function (has to be a valid identifier)
        wrap -- flag to wrap the code into a python function

        """
        # be sure vout and vin are variables
        vout = Variable(vout)
        vin = Variables(vin)
        if len(set([str(v) for v in vin]) & set([str(vout)])) > 0:
            raise RuntimeError("Not supported: output variable is also an input.")
        self.__vin = vin
        """List of input variables."""
        self.__vout = vout
        """Output variable."""
        self.__code = code
        """Code to be executed which transforms the input variables to the
        output variable."""
        name_is_identifier = False
        try:
            name_is_identifier = name.isidentifier()
        except AttributeError as e:
            # Python2
            import re, tokenize, keyword
            name_is_identifier = re.match(tokenize.Name + '$', name) \
                                 and not keyword.iskeyword(name)
        if not name_is_identifier:
            raise RuntimeError("Function name is used in code and must follow Python identifier rules.")
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
        # assert str(self.__vout).isidentifier()
        # for v in self.__vin:
        #     assert str(v).isidentifier()
        code = ""
        # create the output itom
        # (shall be local to the created function, so we don't put it into local_vars)
        code_init_vout_itom = "{} = Itom('{}',{},variable='{}')\n".format(
            self.__vout, self.__vout, None, self.__vout)
        if self.__wrap:
            # assert self.__name.isidentifier()
            params = ",".join([v.codename for v in self.__vin])
            code += "def {}({}):\n".format(self.__name, params)
            # code += textwrap.indent(u_code, "    ")
            code += textwrap.indent(code_init_vout_itom, "    ")
            code += textwrap.indent(self.__code, "    ")
            code += "\n    return {}".format(self.__vout)
            code += "\n\n{} = {}({})".format(self.__vout, self.__name, params)
        else:
            code += code_init_vout_itom
            code += self.__code
        return code

    def execute(self, itoms):
        """Executes the function given the itoms.

        itoms -- 'Itoms' object, list or dictionary of itoms

        """
        # make sure its an Itoms-object
        itoms = Itoms(itoms)
        # verify inputs
        if not set([v.name for v in self.__vin]).issubset(
                set([v.name for v in itoms.values()])):
            raise RuntimeError("Missing itoms to execute the function.")
        # generate code
        code = self.__enclosed_code()
        # execute code
        local_vars = {i.codename: i for i in itoms.values()}
        exec(code,
             {'Itom': Itom, 'copy': copy, 'interval': interval},
             local_vars)
        # local_vars may include utils and functions
        # -> keep only inputs and output
        itoms[self.vout.name] = local_vars[self.vout.name]
        return itoms

    def __str__(self):
        return self.__name

    def __eq__(self, other):
        if isinstance(other, Function):
            return (self.__vout == other.__vout) \
                and (set(self.__vin) == set(other.__vin)) \
                and (self.__code == other.__code)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__vout, self.__vin, self.__code))
