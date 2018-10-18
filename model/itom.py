"""Implementation of an itom.

__date__ = 2018-10-18
__author__ = Denise Ratasich

"""

from collections import OrderedDict


class Itom(object):
    """Itom class."""

    def __init__(self, name, value, timestamp=None, variable=None):
        self.__name = name
        """Name of this itom."""
        self.__value = value
        """Value of the variable given this itom."""
        self.__timestamp = timestamp
        """Timestamp of this itom in seconds.

        For instance, use the Unix epoch time:
        - https://www.unixtimestamp.com/

        Note that the timestamp is reset when you set the value. Therefore,
        always set the value first, then the timestamp.

        """
        self.__variable = variable
        """Variable this itom corresponds to."""

    @property
    def name(self):
        return self.__name

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
        return self.__name

    def __eq__(self, other):
        return (self.__name == other.__name) \
            and (self.__variable == other.__variable) \
            and (self.__value == other.__value) \
            and (self.__timestamp == other.__timestamp)

    def __hash__(self):
        return hash((self.__name, self.__variable, self.__value, self.__timestamp))


class Itoms(OrderedDict):
    """List of itoms."""

    def __init__(self, *args, **kwargs):
        # initialize with given list
        itoms_dict = {}
        # get list from optional parameter 'list'
        if 'list' in kwargs.keys():
            itoms_dict = self.__to_dict(kwargs['list'])
            del kwargs['list']
        # get list from first argument if available
        try:
            itoms_dict = self.__to_dict(args[0])
        except Exception as e:
            pass
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
