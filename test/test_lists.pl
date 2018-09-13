% Tests list library

:- use_module(library(lists)).


%% testcases

query(member(1,[1,2,3])).
query(member(3,[1,2,3])).
query(not member(1,[])).
query(not member(4,[1,2,3])).

%query(intersection([1,2],[1,2,3],X)).
query(intersection([1,2],[1,2,3],[1,2])).
query(intersection([1,2],[3,4,5],[])).
query(not intersection([1,2],[1,3,4],[])).
query(not intersection([1,2],[1,2,3],[])).
