%!/usr/bin/env problog

:- use_module(library(shsa)).


% SHSA knowledge base

function(x, r1, [a]).
function(x, r2, [b]).
function(x, r3, [c]).
function(x, r4, [d]).

% to create executable substitutions: define implementations of the relations
implementation(r1, "x.v = 2 * a.v").
implementation(r2, "x.v = 2 * b.v").
implementation(r3, "x.v = 2 * c.v").
implementation(r4, "x.v = 0.5 * d.v").

% here: don't add availability (appended by monitor)

% tests are in: test_monitor.py
% here: don't add queries!
