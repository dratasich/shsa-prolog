%!/usr/bin/env problog

:- use_module(library(shsa)).


%% a SHSA knowledge base
% (very simple)

% structure
function(a, r1, [b]).
implementation(r1, "b = 2*a").


%% testcases

query(relation(r1)).
query(implementation(r1, X)).
