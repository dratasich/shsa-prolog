% vote over 3 sensors

% add sensor match (interval overlaps)
% replace probability with the overlap/error
% e.g., 0.8::match(sonar,laser).
%       when error between sonar and laser is 0.2

0.5::match(X,Y).
match(X,Y) :- match(Y,X).

% failures (triple)
0.1::failed(X,Y,Z) :-   match(X,Y),   match(X,Z),   match(Y,Z).
0.2::failed(X,Y,Z) :-   match(X,Y),   match(X,Z), \+match(Y,Z).
0.5::failed(X,Y,Z) :-   match(X,Y), \+match(X,Z),   match(Y,Z).
0.5::failed(X,Y,Z) :-   match(X,Y), \+match(X,Z), \+match(Y,Z).
0.5::failed(X,Y,Z) :- \+match(X,Y),   match(X,Z),   match(Y,Z).
0.5::failed(X,Y,Z) :- \+match(X,Y),   match(X,Z), \+match(Y,Z).
0.9::failed(X,Y,Z) :- \+match(X,Y), \+match(X,Z),   match(Y,Z).
%0.1::failed(X,Y,Z) :- \+match(X,Y), \+match(X,Z), \+match(Y,Z).
% when all sensors mismatch - no idea what probability this can be
