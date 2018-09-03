%% ProbLog library for SHSA knowledge base

:- use_module(library(lists)).


% node .. variable or function
% a relation is a function out = f([in1, in2, ..])
node(X) :- variable(X).
node(X) :- relation(X).
variable(O) :- function(O,F,I).
variable(V) :- function(O,F,I), member(V,I).
relation(F) :- function(O,F,I).
% structure from function(..) facts
edge(F,O) :- function(O,F,I).
edge(V,F) :- function(O,F,I), member(V,I).

% itom .. information atom of a variable
% itoms may be available, i.e., itom(name)=true, or not
itom(I) :- itomsOf(V,IL), member(I,IL).

% the associated variable to an itom is provided (by the existing itom)
% a variable can also be provided by a substitution
providedByItom(V) :- variable(V), itomsOf(V,IL),
                     member(I,IL), itom(I).
provided(V) :- providedByItom(V).
provided(V) :- substitution(V,F,IL).

% all variables of a list are provided
allProvided([]).
allProvided([H|T]) :- provided(H), allProvided(T).

% substitution
substitution(O,F,IL) :- function(O,F,IL),
                        allProvided(IL).
