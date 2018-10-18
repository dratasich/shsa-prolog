%!/usr/bin/env problog

:- use_module(library(shsa)).


%% a SHSA knowledge base
% with several provided itoms per variable
% leading to a high number of possible substitutions

% structure
function(a,r1,[b,c]).
function(a,r2,[d]).
function(b,r3,[c]).

% itoms
itomsOf(a,[a1,a2]).
itomsOf(b,[b1]).
itomsOf(c,[c1,c2]).
itomsOf(d,[d1]).


%% testcases

%% % substitution
query(substitution(a,X)).
query(substitution(a,a1)).
query(substitution(a,a2)).
query(substitution(a,[function(a,r2,[d]), d1])).
query(substitution(a,[function(a,r1,[b, c]), b1, c1])).
query(substitution(a,[function(a,r1,[b, c]), b1, c2])).
query(substitution(a,[function(a,r1,[b, c]), [function(b,r3,[c]), c1], c1])).
query(substitution(a,[function(a,r1,[b, c]), [function(b,r3,[c]), c1], c2])).
query(substitution(a,[function(a,r1,[b, c]), [function(b,r3,[c]), c2], c1])).
query(substitution(a,[function(a,r1,[b, c]), [function(b,r3,[c]), c2], c2])).
