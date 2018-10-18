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


% SHSA knowledge base of the rover

% kinematic model
% see also "Probabilistic Robotics"

% robot pose (x,y,h) = (location, heading)
% heading = 0 -> points to direction of x-axis
function(x, rx1, [x_last,t,v,w]).
function(x, rx2, [x_last,t,vx]).
function(y, ry1, [y_last,t,v,w]).
function(y, ry2, [y_last,t,vy]).
function(h, rh1, [h_last,t,w]).

function(v, rv1, [vx,vy]).
function(v, rv2, [vl,vr]).
function(v, rv3, [v_last,t,a]).
function(vx,rvx1,[vx_last,t,ax]).
function(vx,rvx2,[x,t,x_last]).
function(vy,rvy1,[vy_last,t,ay]).
function(vy,rvy2,[y,t,y_last]).

function(w, rw1, [vx,vy]).
function(w, rw2, [vl,vr]).
function(w, rw3, [h,t,h_last]).
function(w, rw4, [t,x,x_last,y,y_last]).

function(a, ra1, [ax,ay]).


% to create executable substitutions: define implementations of the relations
implementation(rx1, "").
implementation(rx2, "").
implementation(ry1, "").
implementation(ry2, "").
implementation(rh1, "").
implementation(rv1, "").
implementation(rv2, "").
implementation(rv3, "").
implementation(rvx1, "").
implementation(rvx2, "").
implementation(rvy1, "").
implementation(rvy2, "").
implementation(rw1, "").
implementation(rw2, "").
implementation(rw3, "").
implementation(rw4, "").
implementation(ra1, "").


% provided itoms will be appended by monitor
% - why: flexible/changing availability is possible
% - implementation: available itoms extracted from the csv
