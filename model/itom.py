"""Implementation of an itom.

__date__ = 2018-10-18
__author__ = Denise Ratasich

An itom (= information atom) is a tuple including data and an explanation of
this data [Kop14]. Itoms are distributed over the common network interface via
messages.

In SHSA we refer to the data as "value" (abbreviated by v).
Moreover, each itom provides following explanation of the data:
- variable = associated variable or entity
- t = timestamp of the acquisition or generation of the value
and properties:
- name = identifier of the itom

An itom is associated to a (single) variable of the SHSA knowledge base,
however, a variable can be provided by several itoms (variable:itoms -- 1:*).

[Kop14] H. Kopetz. A Conceptual Model for the Information Transfer in
        Systems-of-Systems. In 2014 IEEE 17th International Symposium on
        Object/Component/Service-oriented Real-time Distributed Computing
        (ISORC), pages 17--24, June 2014.

"""

from collections import OrderedDict
from model.variable import Variable


class Itom(Variable):
    """Itom class.

    Note that the timestamp is reset when you set the value.
    Therefore, always set the value first, then the timestamp!

    """

    def __init__(self, name, value, timestamp=None, variable=None):
        self.__value = value
        """Value of the variable given this itom."""
        self.__timestamp = timestamp
        """Timestamp of this itom.

        For instance, use the Unix epoch time:
        - https://www.unixtimestamp.com/
        Or an interval to express uncertainties in time.

        """
        self.__variable = None
        if variable is not None:
            self.__variable = self.toidentifier(variable)
        """Variable this itom corresponds to."""
        # use name and codename of superclass variable
        # to represent itoms name and codename
        super(Itom, self).__init__(name)

    @property
    def variable(self):
        return self.__variable

    @property
    def v(self):
        return self.__value

    @v.setter
    def v(self, value):
        """Set the value of this itom (timestamp is reset to None)."""
        self.__value = value
        self.__timestamp = None

    @property
    def t(self):
        return self.__timestamp

    @t.setter
    def t(self, timestamp):
        """Set the timestamp of this itom in seconds."""
        self.__timestamp = timestamp

    def __str__(self):
        return self._name

    def __eq__(self, other):
        if isinstance(other, Itom):
            return (self._name == other._name) \
                and (self.__variable == other.__variable) \
                and (self.__value == other.__value) \
                and (self.__timestamp == other.__timestamp)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self._name, self.__variable, self.__value, self.__timestamp))


class Itoms(OrderedDict):
    """Dictionary of itoms."""

    def __init__(self, *args, **kwargs):
        # initialize with given list
        itoms_dict = {}
        # get list from optional parameter 'list'
        if 'list' in kwargs.keys():
            itoms_dict = self.__to_dict(kwargs['list'])
            del kwargs['list']
        # get initial dict (argument 0 for OrderedDict)
        try:
            itoms_dict = args[0]
        except Exception as e:
            # no initial dict given
            pass
        # be sure we've got a dict
        try:
            itoms_dict = dict(itoms_dict)
        except TypeError as e:
            # cannot be casted to a dict
            # transform the iterable to a dict with a custom function
            itoms_dict = self.__to_dict(itoms_dict)
        # be sure every element (value) is an itom
        itoms_dict = self.__to_itoms_dict(itoms_dict)
        # initialize dict
        if len(itoms_dict) > 0:
            super(Itoms, self).__init__(itoms_dict, **kwargs)
        else:
            super(Itoms, self).__init__(*args, **kwargs)

    def __to_dict(self, itoms_list):
        itoms_dict = {}
        for itom in itoms_list:
            itoms_dict[itom.name] = itom
        return itoms_dict

    def __to_itoms_dict(self, adict):
        if len(adict) == 0:
            return adict
        itoms_dict = {}
        for k, v in adict.items():
            if not isinstance(v, Itom):
                itoms_dict[k] = Itom(k, v)
            else:
                itoms_dict[k] = v
        return itoms_dict

    @property
    def availability(self):
        """Returns a dictionary of variable->list(itoms)."""
        availability = {}
        for itom in self.values():
            v = itom.variable
            if v not in availability.keys():
                availability[v] = []
            availability[v].append(itom)
        return availability
