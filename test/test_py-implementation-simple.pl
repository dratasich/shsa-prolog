%!/usr/bin/env problog

:- use_module(library(shsa)).


% SHSA knowledge base

function(x, r1, [a]).
function(x, r2, [b]).
function(x, r3, [c]).
function(x, r4, [d]).

% itoms
itomsOf(x, [x1, x2]).
itomsOf(a, [a1]).
itomsOf(b, [b1]).
itomsOf(c, [c1]).
itomsOf(d, [d1]).

% to create executable substitutions: define implementations of the relations
implementation(r1, "x.v = 2 * a.v").
implementation(r2, "x.v = 2 * b.v").
implementation(r3, "x.v = 2 * c.v").
implementation(r4, "x.v = 0.5 * d.v").


% tests are in: test_implementation.py
% here: don't add queries!
