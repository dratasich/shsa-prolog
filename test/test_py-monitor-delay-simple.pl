%!/usr/bin/env problog

:- use_module(library(shsa)).


% SHSA knowledge base

% 2 itoms a1, x1 represent the same variable x
% however, a1 is faster than x1
% so we introduce a delay relation so we can compare a1 with x1
function(x, delay, [a]).

implementation(delay, "
try:
    a_delayed = a_current
    a_current = a
except:
    # init variables
    a_delayed = a
    a_current = a

# assign a delayed value to x
x.v = a_delayed.v
").

% here: don't add availability
% itomsOf(..) will be appended by the monitor!

% tests are in: test_monitor.py
% here: don't add queries!
