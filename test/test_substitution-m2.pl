%!/usr/bin/env problog

:- use_module(library(shsa)).


%% a SHSA knowledge base
% (cyclic)

% structure
function(a,r1,[b]).
function(a,r2,[c]).
function(b,r31,[c]).
% no visited node implementation, cycles are not (yet) allowed
%function(c,r32,[b]).

% itoms
itomsOf(c,[c1]).


%% testcases

%% % substitution
query(substitution(a,X)).
query(substitution(a,[function(a,r1,[b]), [function(b,r31,[c]), c]])).
query(substitution(a,[function(a,r2,[c]), c])).
