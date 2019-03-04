"""SHSA monitor.

__date__ = 2018-11-08
__author__ = "Denise Ratasich"

The monitor compares given itoms by transfering the itoms first into the common
domain. Relations probably have to be concatenated -> to substitutions.

Copied and adapted from the original SHSA package
(https://github.com/dratasich/shsa).

"""

from collections import OrderedDict, deque
from interval import interval, inf
import itertools
import numpy as np
import re
import problog

from model.itom import Itom, Itoms
from model.problog_interface import ProblogInterface


class BaseMonitor(object):
    """Base class for monitors."""

    def __init__(self, model, domain, itoms=[], librarypaths=["./model/"]):
        """Initialize the monitor.

        model -- SHSA knowledge base collecting the relations between
            variables.
        domain -- Common domain (a variable in the knowledge base) where the
            itoms will be compared to each other.
        itoms -- Itoms-object holding inputs to the monitor.
        librarypaths -- Set paths of problog libraries used in model.
        filter_window_size -- Set the size of the window for the median filter.

        """
        self.__pli = ProblogInterface(librarypaths=librarypaths)
        self.__pli.load(model)
        """SHSA knowledge base."""
        self.__domain = domain
        """Variable domain where the itoms shall be compared."""
        self.__itoms = Itoms(itoms)
        """Available itoms or last itoms monitored.
        Used to identify a change in the itoms."""
        self.__substitutions = None
        """List of substitutions used to bring the itoms into the common domain."""
        # workaround: for ROS monitor (subscribe based on model)
        try:
            self.__substitutions = self.__collect_substitutions(itoms)
            # workaround: triggers reset on first monitor (necessary to fully initialize)
            self.__itoms = Itoms(itoms)
        except problog.engine.UnknownClause as e:
            # no itomsOf in the problog model (needed to find substitutions)
            # we will try later (monitor)
            pass
        # debugging
        self._debug_callback = None
        """Called at the end of monitor(.) to debug the monitor step."""

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
        """Returns the list of substitutions used to bring the itoms into the common
        domain."""
        return self.__substitutions

    def update(self, model, domain):
        """Resets the model and the domain, i.e., variable to monitor."""
        self.__domain = domain
        self.__pli.reset()
        self.__pli.load(model)

    def set_debug_callback(self, fct):
        self._debug_callback = fct
        return

    def __collect_substitutions(self, itoms=[]):
        """Find relations from variables (given itoms) to domain."""
        program = "\n"
        if "itomsOf" not in self.__pli.program and len(itoms) > 0:
            # be sure itoms is of the right type 'Itoms'
            itoms = Itoms(itoms)
            # append available itoms to program with "itomsOf(variable,[itom1,..])"
            for variable, il in itoms.availability.items():
                assert variable is not None and variable != ""
                names = [i.name for i in il]
                program += "itomsOf({},[{}]).\n".format(variable, ','.join(names))
            program += "\n"
        if len(itoms) > 0:
            assert "itomsOf" in program or "itomsOf" in self.__pli.program
        # get all valid substitutions for the domain
        # -> query problog knowledge base
        program += "query(substitution({},S)).".format(self.__domain)
        result = self.__pli.evaluate(program)
        S = []
        for r in result.keys():
            s = self.__pli.parse_substitution(str(r))
            S.append(s)
        if len(itoms) == 0:
            # set itoms used (default value)
            for s in S:
                for v in s.vin:
                    self.__itoms[v.name] = Itom(v.name, 0.0, variable=v.name)
        return S

    def __recollect(self, itoms):
        recollected = False
        if self.__substitutions is None \
           or set(itoms.keys()) != set(self.__itoms.keys()):
            self.__substitutions = self.__collect_substitutions(itoms)
            recollected = True
        return recollected

    def _monitor(self, itoms, reset=False):
        raise NotImplementedError

    def monitor(self, itoms):
        itoms = Itoms(itoms)
        # recollect substitutions if itoms changed
        reset = self.__recollect(itoms)
        self.__itoms = itoms  # save to identify changes in the next monitor step
        # monitor implemented in sub class
        failed = self._monitor(itoms, reset)
        # done
        return failed


class Monitor(BaseMonitor):
    """Monitor transfers itoms to a given common domain exploiting a SHSA model and
    checks for equality by interval arithmetic.

    """

    def __init__(self, model, domain, itoms=[], librarypaths=["./model/"],
                 average_filter_window_size=0, median_filter_window_size=0,
                 buffer_size=1):
        """Initialize the monitor.

        model -- SHSA knowledge base collecting the relations between
            variables.
        domain -- Common domain (a variable in the knowledge base) where the
            itoms will be compared to each other.
        itoms -- Itoms-object holding inputs to the monitor.
        librarypaths -- Set paths of problog libraries used in model.
        filter_window_size -- Set the size of the window for the corresponding
            filter.
        buffer_size -- Size of the itoms buffer.
            Itoms are put in a queue to compensate delayed itoms.

        """
        # number of past monitor calls the comparison uses the itoms from
        self.__buffer_size = buffer_size
        """Length of queue of saved itoms."""
        # filters
        self.__median_window = None
        """Window to apply np.median to the monitor results."""
        if median_filter_window_size > 0:
            self.__median_window = deque(maxlen=median_filter_window_size)
        self.__average_window = None
        """Window to apply np.average to the monitor results."""
        if average_filter_window_size > 0:
            self.__average_window = deque(maxlen=average_filter_window_size)
        # init BaseMonitor
        super(Monitor, self).__init__(model, domain, itoms=itoms,
                                      librarypaths=librarypaths)

    @property
    def buffer_size(self):
        """Returns the size of the buffer."""
        return self.__buffer_size

    def _comparable(self, itoms):
        """Returns true when the timestamps of the itoms overlap."""
        itoms = list(itoms)
        overlap = interval([-inf, inf])
        for itom in itoms:
            # in case no timestamps are used, assume the values can be compared
            try:
                if itom.t is None:
                    return True
            except AttributeError as e:
                # no itom at all (could be a simple integer)
                return True
            overlap = overlap & itom.t
        return overlap != interval() #(overlap[0][1] - overlap[0][0]) == 0

    def _itoms_for_substitution(self, s, available_itoms):
        """Returns a list of possible inputs for the given substitution s.

        Generate and return collections for an execution of s.
        A collection contains exactly one itom per input of s
        and all timestamps of the itoms in a collection overlap.

        """
        # filter itoms that are inputs of s, sorted by signal
        itoms = {v.name: [itom for itom in available_itoms
                          if itom.name == v.name]
                 for v in s.vin}
        # combine inputs -> cartesian product of inputs
        combs = itertools.product(*itoms.values())
        itoms = [c for c in combs if self._comparable(c)]
        return itoms

    def _pairs_for_comparison(self, outputs):
        """Returns combinations of outputs to compare againts."""
        # pairwise
        comparables = []
        for si, oi in outputs:
            for sj, oj in outputs:
                if si == sj:
                    continue
                if not self._comparable([oi, oj]):
                    continue
                comparables.append((si, sj, oi, oj))
        return comparables

    def _error(self, v, w):
        """Returns the error between two itoms."""
        v = interval(v)
        w = interval(w)
        error = max(0, max(v[0][0], w[0][0]) - min(v[0][1], w[0][1]))
        overlap = 0
        intersection = v & w
        if len(intersection) > 0:
            overlap = abs(intersection[0][1] - intersection[0][0])
        else:
            assert error > 0
            overlap = 0
        return error, overlap

    def _compare(self, itoms, reset=False):
        """Calculate errors between substitutions.

        Returns an error matrix of size nxn and related information.
        - n .. number of substitutions

        Indices correspond to substitution indices.

        This method considers measurements with uncertain value and time.

        """
        # itoms have changed, monitor has been re-initialized with new substitutions
        if reset:
            # reset queue
            self.__queue = deque(maxlen=self.__buffer_size)
        # save itoms for some time to compensate/make use of late itoms
        self.__queue.append(itoms)
        # execute substitutions with a feasable set of itoms
        outputs = []
        for i, s in enumerate(self.substitutions):
            # flatten queue
            all_itoms = [itom for itoms in self.__queue for itom in itoms.values()]
            # collect combinations of inputs for the substitution
            inputs = self._itoms_for_substitution(s, all_itoms)
            # save output itom only
            # keep links to substitutions -> tuple (substitution, output)
            outputs.extend([(i, s.execute(v)[s.vout.name]) for v in inputs])
        # values to compare
        comparables = self._pairs_for_comparison(outputs)
        # compare: error matrix (non-overlap of intervals)
        n = len(self.substitutions)
        error = np.zeros((n, n))
        overlap = np.zeros((n, n))
        for si, sj, oi, oj in comparables:
            error[si][sj], overlap[si][sj] = self._error(oi.v, oj.v)
        return error, overlap, outputs

    def _monitor(self, itoms, reset=False):
        """Fault detection on given itoms.

        itoms -- dictionary of itoms

        Returns the substitution with the highest error (from the substitutions
        with error > 0). If everything is fine, None is returned.

        """
        # itoms have changed, monitor has been re-initialized with new substitutions
        if reset:
            # reset filter
            if self.__average_window is not None:
                self.__average_window.clear()
            if self.__median_window is not None:
                self.__median_window.clear()  # reset filter
        # calculate error between substitutions
        error, _, outputs = self._compare(itoms, reset)
        # sum error per substitution
        error = error.sum(1)
        # filter (apply average first and then filter outliers with median)
        if self.__average_window is not None:
            self.__average_window.append(error)
            error = np.average(np.array(self.__average_window), axis=0)
        if self.__median_window is not None:
            self.__median_window.append(error)
            error = np.median(np.array(self.__median_window), axis=0)
        # return the substitution with the biggest error
        failed = None
        if sum(error) > 0:
            idx = list(error).index(max(error))
            failed = self.substitutions[idx]
        # debug
        if self._debug_callback is not None:
            self._debug_callback(itoms, outputs, error, failed)
        # done
        return failed


class BayesMonitor(Monitor):
    """Monitor transfers itoms to a given common domain exploiting a SHSA model and
    checks for equality by interval arithmetic and a Bayesian network.

    """

    def _match_probabilities(self, error_matrix, overlap_matrix, values):
        assert error_matrix.shape == overlap_matrix.shape
        m, n = error_matrix.shape
        # number of time steps
        t = int(m / n)
        # calculate interval size per value
        uncertainty = np.zeros(len(values))
        for i, v in enumerate(values):
            v = interval(v)
            uncertainty[i] = v[0][1] - v[0][0]
        # scale and cut matrices by uncertainty
        for i in range(m):
            for j in range(n):
                u = min(uncertainty[i], uncertainty[j])
                overlap_matrix[i, j] = overlap_matrix[i, j] / u
                assert overlap_matrix[i, j] <= 1
                error_matrix[i, j] = min(1, error_matrix[i, j] / u)
        # reduce matrices (time handling)
        error_sub_matrices = np.vsplit(error_matrix, t)
        overlap_sub_matrices = np.vsplit(overlap_matrix, t)
        error = np.ones((n, n))
        for a in error_sub_matrices:
            error = np.minimum(a, error)
        overlap = np.zeros((n, n))
        for a in overlap_sub_matrices:
            overlap = np.maximum(a, overlap)
        # join vice-versa errors (min error, max overlap)
        e = np.ones((n, n))
        for i in range(n):
            for j in range(n):
                e[i, j] = min(error[i, j], error[j, i])
        error = e
        o = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                o[i, j] = max(overlap[i, j], overlap[j, i])
        overlap = o
        # init probabilities
        match = np.full((n, n), 0.5)
        # increase probabilities depending on error or overlap
        for i in range(n):
            for j in range(n):
                match[i, j] -= 0.4 * error[i, j]
                match[i, j] += 0.4 * overlap[i, j]
        return match

    def _match(self, error_matrix):
        m, n = error_matrix.shape
        # number of time steps
        t = int(m / n)
        # reduce matrix (time handling)
        error_sub_matrices = np.vsplit(error_matrix, t)
        error = np.ones((n, n))
        for a in error_sub_matrices:
            error = np.minimum(a, error)
        # join vice-versa errors (min error, max overlap)
        e = np.ones((n, n))
        for i in range(n):
            for j in range(n):
                e[i, j] = min(error[i, j], error[j, i])
        error = e
        # init match
        match = np.full((n, n), True)
        for i in range(n):
            for j in range(n):
                if error[i, j] > 0:
                    match[i, j] = False
        return match

    def _monitor(self, itoms, reset=False):
        # calculate error between substitutions
        error, overlap, outputs, values = self._compare(itoms, reset)
        match = self._match(error)
        assert np.equal(match, match.transpose()).all()
        pli = ProblogInterface(librarypaths=[])
        assert len(match) == 3
        pli.load("model/vote3.pl")
        program = ""
        for i in range(0,len(match)):
            for j in range(i+1,len(match)):
                m = str(match[i, j]).lower()
                program += "evidence(match(s{},s{}), {}).\n".format(i, j, m)
        for i in range(len(match)):
            program += "query(failed(s{}, s{}, s{})).\n".format(i, (i+1)%3, (i+2)%3)
        result = pli.evaluate(program)
        probs = result.values()  # probabilities
        # return substitution with highest failure probability
        failed = None
        if min(probs) > 0.49:  # 0.5 .. no idea if a failure occured or not
            idx = list(probs).index(max(probs))
            failed = self.substitutions[idx]
        return failed
