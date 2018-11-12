%!/usr/bin/env problog

:- use_module(library(shsa)).


% SHSA knowledge base

function(x, r1, [a]).
function(x, r2, [b]).

% to create executable substitutions: define implementations of the relations
implementation(r1, "x.v = 2 * a.v").
implementation(r2, "x.v = 0.5 * b.v").

% availability is static, so we put it here right away
itomsOf(x, [x1, x2]).
itomsOf(a, [a1]).

% tests are in: test_monitor.py
% here: don't add queries!
