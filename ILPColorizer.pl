:- use_module(library(dcg/basics)).
:- use_module(library(dcg/high_order)).
:- use_module(library(readutil)).
:- use_module(library(simplex)).
:- initialization(main, main).

:- set_prolog_flag(stack_limit, 8_589_934_592).
%parsing
idf(Name) --> string_without(" #\t\n?,[];:",NameCharacters),{string_codes(Name,NameCharacters)},{string_length(Name,Length),Length > 0}.

adj_list(adj_list(Source,Targets)) --> idf(Source),whites,sequence(idf," ",Targets),blanks.

comment(Text) --> blanks,"#",string_without("\n",Text),{string_length(Text,Length),Length > 0},blanks.

adj(Rows) --> sequence(comment,_),sequence(adj_list,Rows).

write_list([]).
write_list([Obj|Rest]) :- write(Obj),write(" "),write_list(Rest).

%extract_value(Operator,LHS,RHS) :- LHS=Operator(RHS).

print_rows([]).
print_rows([adj_list(Source,Targets)|Tail]) :- 
    write("Source: "),write(Source),write(" "),write_list(Targets),write("\n"),print_rows(Tail).

line(Text) --> string_without("\n",Text),{string_length(Text,Length),Length > 0},blanks.

lines(line(Lines)) --> sequence(line,Lines).

%constraint making
vertex_list([],Vertexes) :- Vertexes=[].
vertex_list([adj_list(Source,_)|Tail],Vertexes) :- vertex_list(Tail,SubVertexes),append([Source],SubVertexes,Vertexes).

vertex_color_list(VertexCount,VertexName,ColorList) :- 
    VertexCount >= 0,
    string_concat(VertexName,"_",Prefix),
    string_concat(Prefix,VertexCount,NewAtomName),
    atom_codes(NewAtom,NewAtomName),
    NewCount is VertexCount-1,
    (NewCount = 0,ColorList = [NewAtom] ; 
     vertex_color_list(NewCount,VertexName,SubColors), append([NewAtom],SubColors,ColorList)).

add_singlecolor_constraint(VertexList,S0,S1)  :-
    constraint(VertexList = 1,S0,S1).

edge_constraint(Left,Right,WColor,S0,S1) :- 
    write(Left),write(" "),write(Right),write(" "),write(WColor),write("\n"),
    constraint([Left,Right] =< 1,S0,S2),
    constraint([Left,Right,-1*WColor] =< 0,S2,S1).

add_edge_constraint(Source,WColor,Target,S0,S1) :- 
    foldl(edge_constraint,Source,Target,WColor,S0,S1).

add_edge_constraints(VertexCount,adj_list(Source,Targets),S0,S1) :- 
    vertex_color_list(VertexCount,Source,SourceColorList),
    vertex_color_list(VertexCount,w,WList),
    maplist(vertex_color_list(VertexCount),Targets,TargetsColorList),
    foldl(add_edge_constraint(SourceColorList,WList),TargetsColorList,S0,S1).

add_anycolor_constraint(Lhs,Rhs,S0,S1) :-
    %write(Lhs),write(" "),write(Rhs),write("\n"),
    constraint([Lhs,-1*Rhs] =< 0,S0,S1).

add_anycolor_constraints(ColorVariableList,VariableList,S0,S1) :- 
    foldl(add_anycolor_constraint, VariableList,ColorVariableList,S0,S1).

integer_constraint(Variable,S0,S1) :-
    constraint(integral(Variable),S0,S1).
add_integer_constraints(VariableList,S0,S1) :-
    foldl(integer_constraint,VariableList,S0,S1).

%input handling
main([FilePath|_]) :- 
    read_file_to_codes(FilePath,Data,[]),!,
    phrase(adj(Rows),Data,[]),
    vertex_list(Rows,Vertexes),
    length(Vertexes,VertexCount),!,
    maplist(vertex_color_list(VertexCount),Vertexes,TotalColorList),
    gen_state(S0),
    foldl(add_singlecolor_constraint,TotalColorList,S0,S1),
    foldl(add_edge_constraints(VertexCount),Rows,S1,S2),
    vertex_color_list(VertexCount,w,ObjectiveList),
    foldl(add_integer_constraints,TotalColorList,S2,S3),
    add_integer_constraints(ObjectiveList,S3,S4),
    minimize(ObjectiveList,S4,S5),
    objective(S5,MinimumColorCount),
    write(MinimumColorCount).
    %print_rows(Rows).

