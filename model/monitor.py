"""SHSA monitor.

__date__ = 2018-11-08
__author__ = "Denise Ratasich"

The monitor compares given itoms by transfering the itoms first into the common
domain. Relations probably have to be concatenated -> to substitutions.

Copied and adapted from the original SHSA package
(https://github.com/dratasich/shsa).

"""

from collections import OrderedDict
import numpy as np
from interval import interval

from model.itom import Itom, Itoms
from model.problog_interface import ProblogInterface


class Monitor(object):
    """Monitor transfers itoms to a given common domain exploiting a SHSA model and
    checks for equality.

    """

    def __init__(self, model, domain, itoms=[], librarypaths=["./model/"]):
        """Initialize the monitor.

        model -- SHSA knowledge base collecting the relations between
            variables.
        domain -- Common domain (a variable in the knowledge base) where the
            itoms will be compared to each other.
        itoms -- Itoms-object holding inputs to the monitor.
        """
        self.__pli = ProblogInterface(librarypaths=librarypaths)
        self.__pli.load(model)
        """SHSA knowledge base."""
        self.__domain = domain
        """Variable domain where the itoms shall be compared."""
        self.__itoms = itoms
        """Available itoms or last itoms monitored.
        Used to identify a change in the itoms."""
        self.__substitutions = None
        """Substitutions used to bring the itoms into the common domain."""
        if itoms is not None and len(itoms) > 0:
            self.__substitutions = self.__collect_substitutions(itoms)

    @property
    def model(self):
        """Returns the underlying SHSA model."""
        return self.__pli.program

    @property
    def domain(self):
        """Returns the monitoring domain."""
        return self.__domain

    @property
    def substitutions(self):
        """Returns the monitoring domain."""
        return self.__substitutions

    def update(self, model, domain):
        """Resets the model and the domain, i.e., variable to monitor."""
        self.__domain = domain
        self.__pli.reset()
        self.__pli.load(model)

    def __collect_substitutions(self, itoms):
        """Find relations from variables (given itoms) to domain."""
        # be sure itoms is of the right type 'Itoms'
        itoms = Itoms(itoms)
        # append available itoms to program with "itomsOf(variable,[itom1,..])"
        program = "\n"
        for variable, il in itoms.availability.items():
            names = [i.name for i in il]
            program += "itomsOf({},[{}]).\n".format(variable, ','.join(names))
        program += "\n"
        # get all valid substitutions for the domain
        # -> query problog knowledge base
        result = self.__pli.evaluate(
            program + "query(substitution({},S)).".format(self.__domain)
        )
        S = []
        for r in result.keys():
            s = self.__pli.parse_substitution(str(r))
            S.append(s)
        return S

    def monitor(self, itoms):
        """Fault detection on given itoms.

        itoms -- dictionary of itoms

        Returns the failed itom names.

        """
        # recollect substitutions, typically, when itoms change
        if self.__substitutions is None \
           or set(itoms.keys()) is not set(self.__itoms.keys()):
            self.__substitutions = self.__collect_substitutions(itoms)
        self.__itoms = itoms  # save to identify changes in the next monitor step
        # transform: bring to common domain
        outputs = Itoms()
        for i, s in enumerate(self.__substitutions):
            result = s.execute(itoms)
            outputs[s] = result[self.__domain]
        # values to compare
        values = [output.v for output in outputs.values()]
        # compare: squared error matrix (non-overlap of intervals)
        se = np.zeros((len(values), len(values)))
        for i, v in enumerate(values):
            for j, w in enumerate(values):
                # error between (non-interval) values
                #se[i,j] = (v - w) * (v - w)
                # intersect intervals
                v = interval(v)
                w = interval(w)
                se[i,j] = max(0, max(v[0][0], w[0][0]) - min(v[0][1], w[0][1]))
        # sum error per substitution
        error = se.sum(1)
        # return the inputs of the substitution with the biggest error
        failed = []
        if min(error) > 0:
            idx = list(error).index(max(error))
            failed.extend(self.__substitutions[idx].vin)
        return failed