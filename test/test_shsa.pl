%!/usr/bin/env problog

:- use_module(library(shsa)).


%% a SHSA knowledge base

% structure
function(a,r1,[b,c,d]).
function(b,r2,[e]).
function(a,r3,[f]).
function(f,r4,[g,h,i,j]).

% itoms
itomsOf(a,[a1]).
% b not provided
itomsOf(c,[c1]).
itomsOf(d,[d1,d2]).
itomsOf(e,[e1]).
% f,g,h,i,j not provided

% properties
accuracy(a1,1).
% accuracy of c1 missing
accuracy(d1,1).
accuracy(d2,0.9).
accuracy(e1,1).


%% testcases

% nodes and edges defined by relation(..)
query(variable(a)).
query(relation(r1)).
query(variable(b)).
query(variable(c)).

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
query(providedByItom(a,_)).
query(not providedByItom(b,_)).
query(providedByItom(c,_)).
query(provided(a)).
query(provided(b)).
query(provided(c)).
query(provided(d)).
query(allProvided([d])).
query(allProvided([b,c,d])).
query(not allProvided([b,f])).
