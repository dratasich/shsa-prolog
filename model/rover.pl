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
% - Introduce a timestamp variable for each itom
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

% kinematic model
% see also "Probabilistic Robotics"

% robot pose (x,y,h) = (location, heading)
% heading = 0 -> points to direction of x-axis
function(x, rx1, [x_last,t(x_last),t,v,w]).
function(x, rx2, [x_last,t(x_last),t,vx]).
function(y, ry1, [y_last,t(y_last),t,v,w]).
function(y, ry2, [y_last,t(y_last),t,vy]).
function(h, rh1, [h_last,t(h_last),t,w]).

function(v, rv1, [vx,vy]).
function(v, rv2, [vl,vr]).
function(v, rv3, [v_last,t(v_last),t,a]).
function(vx,rvx1,[vx_last,t(vx_last),t,ax]).
function(vx,rvx2,[x,t,x_last,t(x_last)]).
function(vy,rvy1,[vy_last,t(vy_last),t,ay]).
function(vy,rvy2,[y,t,y_last,t(y_last)]).

function(w, rw1, [vx,vy]).
function(w, rw2, [vl,vr]).
function(w, rw3, [h,t,h_last,t(h_last)]).
function(w, rw4, [t,x,x_last,t(x_last),y,y_last,t(y_last)]).

function(a, ra1, [ax,ay]).

% provided itoms will be appended by monitor
% - why: flexible/changing availability is possible
% - implementation: available itoms extracted from the csv
