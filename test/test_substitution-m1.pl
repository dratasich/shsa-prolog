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
itomsOf(c,[c1]).
itomsOf(d,[d1,d2]).
itomsOf(e,[e1]).


%% testcases

%% % substitution
query(substitution(a,X)).
query(substitution(a,a)).
query(substitution(a,[function(a,r1,[b, c, d]), [function(b,r2,[e]), e], c, d])).
% f cannot be substituted
query(not substitution(f,X)).
