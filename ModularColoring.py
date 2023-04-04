import ModularDecomposition.modularDecomp as md
import networkx as nx
import matplotlib.pyplot as plt
import grinpy as gp
import sys
# deterministic resultts
import random
import numpy

from enum import Enum

from collections import deque
from math import *
from functools import partial
import os

class PrimeStrategy(Enum):
    WholeHeuristic = 1
    Quotient = 2

random.seed(246)        # or any integer
numpy.random.seed(4812)

def first(Iterable):
    for x in Iterable:
        return(x)



def RecolorComponents(ComponentsToRecolor,OutColoring,NodeColorMap):
    MaxMap = max( [NodeColorMap[x] for x in ComponentsToRecolor],key=lambda x: len(x))
    for NodeList in ComponentsToRecolor:
        Colors = NodeColorMap[NodeList]
        #recolor, random injective map
        InjectiveMap = {}
        for (Original,New) in zip(Colors,MaxMap):
            InjectiveMap[Original] = New
        for Node in NodeList:
            OutColoring[Node] = InjectiveMap[OutColoring[Node]]
    return(MaxMap)

# returns the color map
def Colorize_Module(OriginalGraph,MD,ColorList,ModuleToColor,Heuristic,Strategy = PrimeStrategy.WholeHeuristic):
    if(len(ModuleToColor) == 1):
        return(set( [ ColorList[first(ModuleToColor)] ]))
    ReturnValue = set()
    Label = MD.nodes[ModuleToColor]['MDlabel']
    ChildrenColorMap = {}
    #postorder traversal
    for Child in MD.successors(ModuleToColor):
        ChildrenColorMap[Child] = Colorize_Module(OriginalGraph,MD,ColorList,Child,Heuristic,Strategy)

    if(Label == '1'):
        #paralell
        for Child in ChildrenColorMap:
            for Color in ChildrenColorMap[Child]:
                ReturnValue.add(Color)
    elif (Label == '0'):
        #series
        MaxMap = max(ChildrenColorMap.values(),key=lambda x: len(x))

        for (Nodelist,Colors) in ChildrenColorMap.items():
            #recolor, random injective map
            InjectiveMap = {}
            for (Original,New) in zip(Colors,MaxMap):
                InjectiveMap[Original] = New
            for Node in Nodelist:
                ColorList[Node] = InjectiveMap[ColorList[Node]]
            
        ReturnValue = MaxMap

    else:
        #prime

        if Strategy == PrimeStrategy.WholeHeuristic:
            #remove coloring for trivial modules, these are the ones we can recolor
            for Child in ChildrenColorMap:
                for Color in ChildrenColorMap[Child]:
                    ReturnValue.add(Color)

            for Child in ModuleToColor:
                ColorList[Child] = -1
            ReturnValue = Heuristic(nx.induced_subgraph(OriginalGraph,ModuleToColor),ColorList,ReturnValue)
        elif Strategy == PrimeStrategy.Quotient:
            QuotientGraph = nx.quotient_graph(OriginalGraph,[x for x in ChildrenColorMap])
            QuotientColoring = {k: -1 for k in ChildrenColorMap}
            AllowedColors = [i for i in range(len(ChildrenColorMap))]
            UsedColors = Greedy(QuotientGraph,QuotientColoring,AllowedColors)
            ColorComponents = {c: [] for c in UsedColors}
            for (Node,Color) in QuotientColoring.items():
                ColorComponents[Color].append(Node)
            for Component in ColorComponents.values():
                ReturnValue.update(RecolorComponents(Component,ColorList,ChildrenColorMap))
    return(ReturnValue)

# Returns a list of colors, and the chromatic number
def Colorize(OriginalGraph,MD,Heuristic,Strategy = PrimeStrategy.WholeHeuristic):
    Root = max([module for module in MD],key=lambda x: len(x))
    Colors = [i for i in range(len(OriginalGraph.nodes))]
    ColorMap = Colorize_Module(OriginalGraph,MD,Colors,Root,Heuristic,Strategy)
    return (Colors,ColorMap)

# hueristic, takes a induced subgraph along with already colored parts
# and then colors the rest.
def Greedy(GraphToColor: nx.DiGraph,CurrentColoring,ColorList):
    ReturnValue = set()
    #completely arbitrary order
    for Node in GraphToColor.nodes:
        if(CurrentColoring[Node] != -1):
            continue
        for Color in ColorList:
            ColorIsValid = True
            for Neighbour in GraphToColor.adj[Node]:
                if(CurrentColoring[Neighbour] == Color):
                    ColorIsValid = False
                    break
            if(ColorIsValid):
                CurrentColoring[Node] = Color
                ReturnValue.add(Color)
                break
    return(ReturnValue)

def DSatur(GraphToColor:  nx.DiGraph,CurrentColoring,ColorList):
    ReturnValue = set()
    DeegreeSortedVertexes = [Node for Node in GraphToColor.nodes]
    DeegreeSortedVertexes.sort(key=lambda node: GraphToColor.degree[node])
    #only assign the first color given that we have not already colored the nodes
    if len([x for x in CurrentColoring if not x == -1]) == 0:
        CurrentColoring[first(DeegreeSortedVertexes)] = first(ColorList)
        ReturnValue.add(first(ColorList))

    for Offset in range(0,len(DeegreeSortedVertexes)):
        MaxIndex = 0
        MaxSatDegree = -1
        for NewOffset in range(0,len(DeegreeSortedVertexes)):
            if(CurrentColoring[DeegreeSortedVertexes[NewOffset]] != -1):
                continue
            SatDegree = len([x for x in GraphToColor.adj[DeegreeSortedVertexes[NewOffset]] if not CurrentColoring[x] == -1])
            if SatDegree > MaxSatDegree:
                MaxIndex = NewOffset
                MaxSatDegree  =SatDegree
        for Color in ColorList:
            ColorIsValid = True
            for Neighbour in GraphToColor.adj[DeegreeSortedVertexes[MaxIndex]]:
                if(CurrentColoring[Neighbour] == Color):
                    ColorIsValid = False
                    break
            if(ColorIsValid):
                CurrentColoring[DeegreeSortedVertexes[MaxIndex]] = Color
                ReturnValue.add(Color)
                break
            
    return(ReturnValue);

nbiter = 300
rep = 30
tabsize = 6
def TabuSearch(GraphToColor: nx.DiGraph,CurrentColoring,K):
    Aspirations = {}
    TabuList = deque()

    #Random K partition
    for Node in GraphToColor:
        CurrentColoring[Node] = random.randrange(0,K)
    
    TotalConflictCount = 0
    
    for Edge in GraphToColor.edges:
        if(CurrentColoring[Edge[0]] == CurrentColoring[Edge[1]]):
            TotalConflictCount += 1
    if(TotalConflictCount == 0):
        return(True)
    for i in range(nbiter):
        RepCount = 0
        BestMove = (100000000,0,0)
        for Node in GraphToColor:
            if(RepCount >= rep):
                break
            ConflictCount = 0
            for Neighbour in GraphToColor.adj[Node]:
                if(CurrentColoring[Node] == CurrentColoring[Neighbour]):
                    ConflictCount += 1
            if(ConflictCount != 0):
                #Calculate new S for the move
                NewColor = random.randrange(0,K)
                #not completely uniform, but whatever
                if(NewColor == CurrentColoring[Node]):
                    NewColor = (NewColor+1) % K
                #calculate the conflict count this new coloring would give
                NewConflict = 0
                for Neigbour in GraphToColor.adj[Node]:
                    if(NewColor == CurrentColoring[Neigbour]):
                        NewConflict += 1
                # This moves total new conflicts
                NewTotalConflict = TotalConflictCount-ConflictCount+NewConflict

                # Check in in tabu
                if( (Node,NewColor) in TabuList):
                    if(not (NewTotalConflict <= Aspirations.setdefault(TotalConflictCount,TotalConflictCount-1))):
                        continue
                if(NewTotalConflict < BestMove[0]):
                    BestMove = (NewTotalConflict,Node,NewColor)
                RepCount += 1
                if(NewTotalConflict < TotalConflictCount):
                    break
        if(BestMove[0] == 100000000):
            break
        Aspirations[TotalConflictCount] = BestMove[0]-1
        TotalConflictCount = BestMove[0]
        TabuList.append( (BestMove[1],BestMove[2]))
        if( len(TabuList) > tabsize):
            TabuList.popleft()
        CurrentColoring[BestMove[1]] = BestMove[2]

        if(TotalConflictCount == 0):
            break

    if(TotalConflictCount == 0):
        return True
    else:
        return False


def BinarySearchCombinator(KIsPossibleHeuristic,GraphToColor,CurrentColoring,ColorList):
    Max = len(ColorList)-1
    Min = 0
    BestColoring = []
    while( Max != Min):
        CurrentGuess = floor( (Min+Max)/2)
        ResultColoring = CurrentColoring.copy()
        IsPossible = KIsPossibleHeuristic(GraphToColor,ResultColoring,CurrentGuess)
        if( IsPossible):
            BestColoring = ResultColoring
            Max = CurrentGuess-1
        else:
            Min = CurrentGuess+1
    if(len(BestColoring) == 0):
        raise Exception("BinarySearchCombinator unable to create a coloring")
    #The coloring a always uses colors 0-len(ColorList)-1, recolor the graph to use the 
    #colors we were allowed to use
    UsedColors = set()
    ColorListVector = list(ColorList)
    for Node in GraphToColor.nodes:
        CurrentColoring[Node] = ColorListVector[ BestColoring[Node]]
        UsedColors.add( ColorListVector[BestColoring[Node]])

    return(UsedColors)

def VerifyColoring(Graph,Coloring):
    ReturnValue = True
    for Node in Graph.nodes:
        for Neighour in Graph.adj[Node]:
            if(Coloring[Node] == Coloring[Neighour]):
                return(False)
    return(ReturnValue)

Test = False
if Test:
    edge_prob = 0.1
    #G = nx.fast_gnp_random_graph(20, edge_prob)
    G = nx.connected_watts_strogatz_graph(20,5,0.1)
    MD = md.modularDecomposition(G)
    (Colors,ColorCount) = Colorize(G,MD,Greedy)
    print(ColorCount,len(ColorCount),Colors)
    print(VerifyColoring(G,Colors))

    nx.write_adjlist(G,"ADJList.txt")
    print(gp.chromatic_number(G))
    nx.draw(G)
    plt.show()
else:
    Filename = os.path.basename(sys.argv[1])
    G = nx.read_edgelist(sys.argv[1],nodetype=int)
    #add any edges lost in translation
    TotalEdges = set(G.nodes)
    MaxNode = max(TotalEdges)
    for i in range(MaxNode):
        if i not in TotalEdges:
            G.add_node(i)
    
    MD = md.modularDecomposition(G)
    Root = max([module for module in MD],key=lambda x: len(x))
    RootType = MD.nodes[Root]['MDlabel']
    Heuristics = {"Tabu search": partial(BinarySearchCombinator,TabuSearch),"Greedy": Greedy,"DSatur": DSatur}
    #Heuristics = {"Greedy": Greedy,"DSatur": DSatur}
    for (Name,Function) in Heuristics.items():
        (Colors,ColorCount) = Colorize(G,MD,Function)
        if(not VerifyColoring(G,Colors)):
            print("Error: whole prime coloring was an invalid coloring",file=sys.stderr)
            exit(1)
        print(Filename,RootType,Name,"WholePrime",len(ColorCount) ,sep=",")
        (Colors,ColorCount) = Colorize(G,MD,Function,PrimeStrategy.Quotient)
        if(not VerifyColoring(G,Colors)):
            print("Error: partial prime coloring was an invalid coloring",file=sys.stderr)
            exit(1)
        print(Filename,RootType,Name,"QuotientPrime",len(ColorCount) ,sep=",")
        (Colors,ColorCount) = Colorize(G,MD,DSatur,PrimeStrategy.Quotient)
        HeuristicColorList = [-1 for i in  range(len(G.nodes))]
        HeuristicAllowedColors = [i for i in  range(len(G.nodes))]
        HeuriticUsedColors = Function(G,HeuristicColorList,HeuristicAllowedColors)
        if(not VerifyColoring(G,HeuristicColorList)):
            print("Error: modular coloring was an invalid coloring",file=sys.stderr)
            exit(1)
        print(Filename,RootType,Name,"WholeHeuristic",len(HeuriticUsedColors) ,sep=",")
    #print(ColorCount,len(ColorCount),Colors)
    #print(VerifyColoring(G,Colors))
