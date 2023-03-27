:- use_module(library(dcg/basics)).
:- use_module(library(dcg/high_order)).
:- use_module(library(readutil)).
:- initialization(main, main).


%parsing
idf(Name) --> string_without(" #\t\n?,[];:",NameCharacters),{string_codes(Name,NameCharacters)},{string_length(Name,Length),Length > 0}.

adj_list(adj_list(Source,Targets)) --> idf(Source),whites,sequence(idf," ",Targets),blanks.

comment(Text) --> blanks,"#",string_without("\n",Text),{string_length(Text,Length),Length > 0},blanks.

adj(Rows) --> sequence(comment,_),sequence(adj_list,Rows).

write_list([]).
write_list([Obj|Rest]) :- write(Obj),write(" "),write_list(Rest).

extract_value(Operator,LHS,RHS) :- LHS=Operator(RHS).

print_rows([]).
print_rows([adj_list(Source,Targets)|Tail]) :- 
    write("Source: "),write(Source),write(" "),write_list(Targets),write("\n"),print_rows(Tail).

line(Text) --> string_without("\n",Text),{string_length(Text,Length),Length > 0},blanks.

lines(line(Lines)) --> sequence(line,Lines).

%constraint making
vertex_list([],Vertexes) :- Vertexes=[].
vertex_list([adj_list(Source,_)|Tail],Vertexes) :- vertex_list(Tail,SubVertexes),append([Source],SubVertexes,Vertexes).

vertex_color_list(1,VertexName,ColorList) :- 
    string_concat(VertexName,1,NewAtomName),
    atom_codes(NewAtom,NewAtomName),
    ColorList = [NewAtom].

vertex_color_list(VertexCount,VertexName,ColorList) :- 
    VertexCount =\= 1,
    string_concat(VertexName,VertexCount,NewAtomName),
    atom_codes(NewAtom,NewAtomName),
    NewCount is VertexCount-1,
    vertex_color_list(NewCount,VertexName,SubColors),
    append([NewAtom],SubColors,ColorList).

has_is_colored_constraints(VertexList,S0,S1)  :-
    length(VertexList,VertexCount).



%input handling
main([FilePath|_]) :- 
    write("Hello world!\n"),
    read_file_to_codes(FilePath,Data,[]),!,
    %string_codes(StringData,Data),
    %write(StringData),!,
    write("File parsed!\n"),
    phrase(adj(Rows),Data,[]),
    print_rows(Rows),
    vertex_list(Rows,Vertexes),
    write(Vertexes),
    vertex_color_list(10,a,ColorList),
    write(ColorList),
    length(Vertexes,VertexCount),
    maplist(vertex_color_list(VertexCount),Vertexes,TotalColorList),
    write(TotalColorList).
    %phrase(adj(Rows),Data,_),!,
    %print_rows(Rows).

