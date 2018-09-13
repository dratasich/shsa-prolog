%!/usr/bin/env problog

:- use_module(library(shsa)).


%% a SHSA knowledge base
% (cyclic)


% graph 1
function(a,r1,[b]).
function(b,r2,[a]).

itomsOf(a,[a1]).
itomsOf(b,[b1]).


% graph 2
function(z,rr1,[y]).
function(y,rr2,[x]).
function(x,rr3,[w]).
function(w,rr4,[z]).

%itomsOf(z,[z1]).
itomsOf(y,[y1]).
itomsOf(w,[w1]).


%% testcases

% graph 1
%query(substitution(a,X)).
query(substitution(a,[function(a,r1,[b]), b])).
query(substitution(a,a)).

% graph 2
%query(substitution(z,X)).
query(substitution(z,[function(z,rr1,[y]), [function(y,rr2,[x]), [function(x,rr3,[w]), w]]])).
query(substitution(z,[function(z,rr1,[y]), y])).
