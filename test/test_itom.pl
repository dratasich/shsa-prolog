%!/usr/bin/env problog

:- use_module(library(shsa)).


%% a SHSA knowledge base

% itoms
itomOf(a,a1).
% b not provided
itomOf(c,c1).
itomsOf(d,[d1,d2]).
itomsOf(e,[e1]).


%% testcases

% itoms
query(itom(a1)).
query(not itom(b1)).
query(itom(c1)).
query(itom(d1)).
query(itom(d2)).
query(itom(e1)).

% map itom to variable
query(variableOf(a1,a)).
query(not variableOf(a1,b)).
query(variableOf(d1,d)).
