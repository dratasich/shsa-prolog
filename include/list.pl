%% ProbLog library for list

% check if X is member of the list T
% or get members of the list
member(X,[X|T]).
member(X,[H|T])  :-  member(X,T).
