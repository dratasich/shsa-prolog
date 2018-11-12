%!/usr/bin/env problog

:- use_module(library(shsa)).


%% a SHSA knowledge base
% with several provided itoms representing ROS topics

% structure
function(dmin, r1, [distances]).
function(dmin, r2, [map, pose]).

% itoms
itomsOf(dmin, ["/emergency_stop/dmin"]).
itomsOf(distances, ["/laser", "/p2os/sonar"]).
itomsOf(pose, ["/amcl/pose"]).


%% testcases

%% % substitution
query(substitution(dmin,X)).
substitution(dmin,"/emergency_stop/dmin").
substitution(dmin,[function(dmin,r1,[distances]), "/laser"]).
substitution(dmin,[function(dmin,r1,[distances]), "/p2os/sonar"]).
