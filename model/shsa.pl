%
% SHSA - Self-Healing by Structural Adaptation
%
% Denise Ratasich
% 2018-08-29
%
% This library defines structure and meaning of a SHSA knowledge base. The
% definitions are derived from the [SH-PGSA paper]. Furthermore, it gives
% clauses to substitute variables (in depth-first search style from
% [Hoeftberger]).
%
% [SH-PGSA paper] D. Ratasich, T. Preindl, K. Selyunin, and R. Grosu.
% Self-Healing by Property-Guided Structural Adaptation. In 2018 IEEE 1st
% International Conference on Industrial Cyber-Physical Systems (ICPS), pages
% 199--205, May 2018.
%
% [Hoeftberger] Oliver Höftberger. Knowledge-based Dynamic Reconfiguration for
% Embedded Real-Rime Systems. PhD thesis, Technische Universität Wien, 2015.
%

:- use_module(library(lists)).


% node .. variable or function
% a relation is a function out = f([in1, in2, ..])
variable(O) :- function(O,_,_).
variable(V) :- function(_,_,I), member(V,I).
relation(R) :- function(_,R,_).

% define implementation of a relation in your model
% the python implementation allows to have a value (.v) and a timestamp (.t)
% - implementation(r1, "b.v = 2*a.v")

% itom .. information atom of a variable
% itoms are set available by
% - itomOf(variable,itom) or
% - itomsOf(variable,[itom1, itom2, ..])
itomOf(V,I) :- itomsOf(V,IL), member(I,IL).

% mapping itom to variable
variableOf(I,V) :- itomOf(V,I).

% identify itoms or represent availability, i.e., itom(name)=true, or not
itom(I) :- itomOf(_,I).

% Note, we do not check if V is a variable, or R is a relation (the interpreter
% would need to search a corresponding function which makes the check slow)!

% the associated variable to an itom is provided (by the existing itom)
% a variable can also be provided by a substitution
providedByItom(V,I) :- itomOf(V,I).
provided(V) :- providedByItom(V,_).
provided(V) :- function(V,_,IL), allProvided(IL).

% all variables of a list are provided
allProvided([]).
allProvided([H|T]) :- provided(H), allProvided(T).


%
% substitution
% - recursive implementation (DFS)
%

% a valid substitution of O
substitution(O,FL) :- substitution(O,FL,[]).

substitution(O,I,Visited) :- providedByItom(O,I).
substitution(O,[function(O,R,IL)|FLinputs],Visited) :-
    function(O,R,IL),
    intersection([O|IL],Visited,[]),
    substitutionInputs(IL,FLinputs,[O|Visited]).

% collects one substitution for each variable in the list [V|Rest]
substitutionInputs([],[],Visited).
substitutionInputs([V|Rest],[FLvar|FLrest],Visited) :-
    substitution(V,FLvar,Visited),
    substitutionInputs(Rest,FLrest,Visited).
