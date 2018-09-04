%!/usr/bin/env problog

:- use_module(library(shsa)).


%% a SHSA knowledge base
% (very simple)

% structure
function(a,r1,[b]).

% itoms
itomsOf(a,[a1]).
itomsOf(b,[b1]).


%% testcases

%% % substitution
query(substitution(a,X)).
query(substitution(a,a)).
query(substitution(a,[function(a,r1,[b]), b])).
