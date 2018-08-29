%!/usr/bin/env problog

:- use_module(library(shsa)).


%% a SHSA knowledge base

% structure
relation(a,r1,[b,c]).
relation(a,r2,[d]).
relation(b,r3,[e]).

% itoms
itomsOf(a,[a1]).
itomsOf(c,[c1]).
itomsOf(d,[d1,d2]).
itomsOf(e,[e1]).

% properties
accuracy(a1,1).
accuracy(d1,1).
accuracy(d2,0.9).


%% testcases

% nodes and edges defined by relation(..)
query(node(a)).
query(node(r1)).
query(variable(a)).
query(function(r1)).
query(variable(b)).
query(variable(c)).
query(edge(r1,a)).
query(edge(b,r1)).
query(edge(c,r1)).
query(not edge(a,c)).
query(not edge(c,a)).

% itoms
query(itom(a1)).
query(not itom(b1)).
query(itom(c1)).
query(itom(d1)).
query(itom(d2)).

% properties
query(accuracy(a1,X)).
query(not accuracy(c1,X)).

% provided
query(providedByItom(a)).
query(not providedByItom(b)).
query(providedByItom(c)).
query(provided(a)).
query(provided(b)).
query(provided(c)).
query(provided(d)).
query(allProvided([d])).
query(allProvided([b,c])).

% substitution
query(substitution(a,F,I)).
query(substitution(a,r1,I)).
query(substitution(b,F,I)).
