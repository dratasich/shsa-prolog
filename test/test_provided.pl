%!/usr/bin/env problog

:- use_module(library(shsa)).


%% a SHSA knowledge base
% (cyclic)


% graph 1
function(a,r11,[b]).
function(b,r12,[a]).

itomsOf(a,[a1]).
itomsOf(b,[b1]).


% graph 2
function(z,r21,[y]).
function(y,r22,[x]).
function(x,r23,[w]).
function(w,r24,[z]).

itomsOf(z,[z1]).
itomsOf(y,[y1]).
itomsOf(w,[w1]).


% graph 3
function(m,r31,[n]).
function(n,r32,[m]).


%% testcases

% provided
query(provided(a)).
query(allProvided([a,b])).

query(provided(y)).
query(provided(z)).

query(not provided(m)).
