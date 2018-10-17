%!/usr/bin/env problog

:- use_module(library(shsa)).


%% a SHSA knowledge base
% (a more complex example)

% structure
function(a,r1,[b,c]).
function(a,r2,[c,d]).

% itoms
itomsOf(a,[a1]).
itomsOf(b,[b1]).
itomsOf(c,[c1]).
itomsOf(d,[d1,d2]).


%% testcases

%% % substitution
query(substitution(a,X)).
query(substitution(a,a1)).
query(substitution(a,[function(a,r1,[b, c]), b1, c1])).
query(substitution(a,[function(a,r2,[c, d]), c1, d2])).
