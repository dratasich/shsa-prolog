%
% SHSA Knowledge Base to test monitor.py
%
% Denise Ratasich
% 2018-10-23
%

:- use_module(library(shsa)).


% SHSA knowledge base

function(x, rx1, [a]).
function(x, rx2, [b]).
function(x, rx3, [c]).
function(x, rx4, [d]).

% to create executable substitutions: define implementations of the relations
implementation(rx1, "x.v = a.v").
implementation(rx2, "x.v = b.v").
implementation(rx3, "x.v = c.v").
implementation(rx4, "x.v = d.v").

% provided itoms will be appended by monitor
% - why: flexible/changing availability is possible
% - implementation: available itoms extracted from the csv
