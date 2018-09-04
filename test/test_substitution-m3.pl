%!/usr/bin/env problog

:- use_module(library(shsa)).


%% a SHSA knowledge base
% (chain)

% structure
function(a,r1,[b]).
function(b,r2,[c]).
function(c,r3,[d]).
function(d,r4,[e]).

% itoms
itomsOf(c,[c1]).
itomsOf(e,[e1]).


%% testcases

%% % substitution
query(substitution(a,X)).
query(substitution(a,[function(a,r1,[b]), [function(b,r2,[c]), [function(c,r3,[d]), [function(d,r4,[e]), e]]]])).
query(substitution(a,[function(a,r1,[b]), [function(b,r2,[c]), c]])).
