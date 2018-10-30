%!/usr/bin/env problog

:- use_module(library(shsa)).


%% a SHSA knowledge base
% (very simple)

% structure
function(a, r1, [b]).

% multiline
implementation(r1,"
a.v = 2*b.v
a.t = b.t
").

% add for substitute search
itomsOf(b, [b1]).


% tests are in: test_implementation.py
% here: don't add queries!
