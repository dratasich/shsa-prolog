% Tests list library

:- use_module(library(list)).


%% testcases

query(member(1,[1,2,3])).
query(member(3,[1,2,3])).
query(not member(1,[])).
query(not member(4,[1,2,3])).
