%% ProbLog library for SHSA knowledge base

:- use_module(library(lists)).


% node .. variable or function
% a relation is a function out = f([in1, in2, ..])
node(X) :- variable(X).
node(X) :- relation(X).
variable(O) :- function(O,_,_).
variable(V) :- function(_,_,I), member(V,I).
relation(R) :- function(_,R,_).
% structure from function(..) facts
edge(R,O) :- function(O,R,_).
edge(V,R) :- function(_,R,I), member(V,I).

% itom .. information atom of a variable
% itoms may be available, i.e., itom(name)=true, or not
itom(I) :- itomsOf(_,IL), member(I,IL).

% the associated variable to an itom is provided (by the existing itom)
% a variable can also be provided by a substitution
providedByItom(V,I) :- variable(V), itomsOf(V,IL),
                     member(I,IL), itom(I).
provided(V) :- providedByItom(V,_).
provided(V) :- function(V,_,IL),
               allProvided(IL).

% all variables of a list are provided
allProvided([]).
allProvided([H|T]) :- provided(H), allProvided(T).


%
% substitution
% - recursive implementation
% - limitations: no cycles allowed (needs visited node implementation)

% a valid substitution of O
substitution(O,O) :- providedByItom(O,_).
substitution(O,[function(O,R,IL)|FLinputs]) :-
    function(O,R,IL), allProvided(IL),
    substitutionInputs(IL,FLinputs).

% collects one substitution for each variable in the list [V|Rest]
substitutionInputs([],[]).
substitutionInputs([V|Rest],[FLvar|FLrest]) :-
    substitution(V,FLvar),
    substitutionInputs(Rest,FLrest).
