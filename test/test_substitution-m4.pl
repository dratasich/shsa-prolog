%!/usr/bin/env problog

:- use_module(library(shsa)).


%% a SHSA knowledge base
% (a more complex example)

% structure
function(a,r1,[b,c]).
function(b,r2,[d,e]).
function(e,r3,[h,i,j]).
function(c,r4,[f]).
function(f,r5,[g]).

% itoms
itomsOf(c,[c1]).
itomsOf(d,[d1,d2]).
itomsOf(e,[e1]).
itomsOf(g,[g1]).
itomsOf(i,[i1]).
itomsOf(j,[j1]).


%% testcases

%% % substitution
query(substitution(a,X)).
query(substitution(a,[function(a,r1,[b, c]), [function(b,r2,[d, e]), d, e], c])).
query(substitution(a,[function(a,r1,[b, c]), [function(b,r2,[d, e]), d, e], [function(c,r4,[f]), [function(f,r5,[g]), g]]])).
