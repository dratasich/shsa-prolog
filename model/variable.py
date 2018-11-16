"""Implementation of a variable.

__date__ = 2018-11-15
__author__ = Denise Ratasich

A variable is an identifier in python code and refers to a physical entity.

"""

import re


class Variable(object):
    """Variable class."""

    def __init__(self, name):
        self._name = str(name)
        """Name of this variable."""
        self._codename = self.toidentifier(name)
        """Python-safe name of this variable."""

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        """Set the name of this variable (codename is set too)."""
        self._name = str(name)
        self._codename = self.toidentifier(name)

    @property
    def codename(self):
        return self._codename

    @staticmethod
    def toidentifier(string):
        """Converts a string to valid Python identifier (if necessary)."""
        if string is None:
            return string
        # be sure it's a string
        string = str(string)
        string_is_identifier = False
        try:
            string_is_identifier = string.isidentifier()
        except AttributeError as e:
            # Python2
            import tokenize, keyword
            string_is_identifier = re.match(tokenize.Name + '$', string) \
                                   and not keyword.iskeyword(string)
        if string_is_identifier:
            # nothing to do
            return string
        # extracted from
        # https://gist.github.com/JamesPHoughton/3a3f87c6662bf5c9eccc9f2206e228fd
        # see also https://docs.python.org/3.7/reference/lexical_analysis.html#identifiers
        s = string.lower()  # only a style guideline
        s = s.strip()
        # spaces or '/' to underscores
        s = re.sub('[\\s\\t\\n\/]+', '_', s)
        # drop all other invalid characters
        s = re.sub('[^0-9a-zA-Z_]', '', s)
        # remove leading characters until we find a letter or underscore
        s = re.sub('^[^a-zA-Z_]+', '', s)
        return s

    def __str__(self):
        return self._name

    def __eq__(self, other):
        if isinstance(other, Variable):
            return (self._name == other._name)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._name)


class Variables(list):
    """List of variable."""

    def __init__(self, *args, **kwargs):
        # get initial list (argument 0 for OrderedDict)
        try:
            alist = args[0]
        except Exception as e:
            # no initial dict given
            pass
        # be sure we've got a list of variables
        alist = list([Variable(e) for e in alist])
        # initialize list
        super(Variables, self).__init__(alist, **kwargs)
