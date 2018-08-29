%% ProbLog library for SHSA knowledge base

:- use_module(library(list)).


% node .. variable or function
% a relation is a function out = f([in1, in2, ..])
node(X) :- variable(X).
node(X) :- function(X).
variable(O) :- relation(O,F,I).
variable(V) :- relation(O,F,I), member(V,I).
function(F) :- relation(O,F,I).
% structure from relation(..) facts
edge(F,O) :- relation(O,F,I).
edge(V,F) :- relation(O,F,I), member(V,I).

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
substitution(O,F,IL) :- relation(O,F,IL),
                        allProvided(IL).
