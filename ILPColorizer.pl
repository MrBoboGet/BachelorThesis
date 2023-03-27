:- use_module(library(dcg/basics)).
:- use_module(library(dcg/high_order)).
:- use_module(library(readutil)).
:- initialization(main, main).

idf(idf(Name)) --> string_without(" #\t\n?,[];:",Name),blanks,{string_length(Name,Length),Length > 0}.

adj_list(adj_list(Source,Targets)) --> idf(Source),blanks,sequence(idf," ",Targets),blanks.

comment(Text) --> blanks,"#",string_without("\n",Text),{string_length(Text,Length),Length > 0},blanks.

adj(Rows) --> sequence(comment,_),sequence(adj_list,Rows).

write_list([]).
write_list([Obj|Rest]) :- write(Obj),write(" "),write_list(Rest).

print_rows([]).
print_rows([adj_list(Source,Targets)|Tail]) :- 
    write("Source: "),write(Source),write(" "),write_list(Targets),print_rows(Tail).

line(Text) --> string_without("\n",Text),{string_length(Text,Length),Length > 0},blanks.

lines(line(Lines)) --> sequence(line,Lines).

main([FilePath|_]) :- 
    write("Hello world!\n"),
    read_file_to_codes(FilePath,Data,[]),!,
    write("File parsed!\n"),
    phrase(adj(Rows),Data,[]),
    print_rows(Rows).
    %phrase(adj(Rows),Data,_),!,
    %print_rows(Rows).

