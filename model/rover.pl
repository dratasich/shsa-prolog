%
% SHSA Knowledge Base of Daisy
%
% Denise Ratasich
% 2018-09-05
%
% This file defines the SHSA knowledge base of our mobile robot / rover
% "Daisy".
%

:- use_module(library(shsa)).


% Introducing the time aspect for state-based relations:
%
% - Introduce a timestamp variable for each itom which has a timestamp
% - A timestamp is related to a value and cannot be separated into another
%   variable. This means, we cannot specify
%   itomsOf(variable t_x,[itom_tx1,itom_tx2])
%   because the timestamps itom_tx1 and itom_tx2 are associated to different
%   itoms, i.e., do not represent the same information!
% - Nesting of itoms?

% However, here we assume:
% Each itom provides a timestamp.
providedByItom(t(V),I) :- providedByItom(V,I).
% -> we use t(variable) to denote the timestamp of that input


% SHSA knowledge base of the rover

function(x,rx1,[x,t(x),t,v,w]).
function(x,rx2,[x,t(x),t,vx]).
function(y,ry1,[y,t(y),t,v,w]).
function(y,ry2,[y,t(y),t,vy]).

function(v,rv1,[vx,vy]).
function(v,rv2,[vl,vr]).
function(v,rv3,[v,t(v),t,a]).
function(vx,rvx1,[vx,t(vx),t,ax]).
function(vy,rvy1,[vy,t(vy),t,ay]).

function(w,rw1,[vx,vy]).
function(w,rw2,[vl,vr]).

function(a,ra1,[ax,ay]).

% provided itoms - appended by monitor (flexible availability)

itomsOf(t,[t]).
itomsOf(x,[x]).
itomsOf(y,[y]).
itomsOf(v,[v]).
itomsOf(w,[w_gyro,w_enc]).
itomsOf(a,[a]).

query(provided(t(x))).
query(substitution(x,X)).
query(function(x,rx1,[x,t(x),t,v,w])).
query(allProvided([x,t(x),t,v,w])).
