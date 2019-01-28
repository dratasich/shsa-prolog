%!/usr/bin/env problog

:- use_module(library(shsa)).


% SHSA knowledge base

% 2 itoms a1, x1 represent the same variable x
% however, a1 is faster than x1
% so we introduce a delay relation so we can compare a1 with x1
function(x, delay, [a]).

implementation(delay, "
value_cur = a.v

try:
    queue.insert(0, value_cur)
except:
    # init variables
    delay = 2
    queue = [value_cur]  # maybe (deep-)copy is necessary
    value_del = value_cur

# provide correct values as soon as the queue is full
if len(queue) >= delay + 1:
    value_del = queue.pop()

# assign a delayed value to x
x.v = value_del
").


% here: don't add availability
% itomsOf(..) will be appended by the monitor!

% tests are in: test_monitor.py
% here: don't add queries!
