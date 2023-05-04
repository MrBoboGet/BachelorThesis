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
import time

class PrimeStrategy(Enum):
    WholeHeuristic = 1
    Quotient = 2
    LargestModuleFirst = 3
    NoPrime = 4

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

    if(not Label == 'p' or (Strategy == PrimeStrategy.Quotient)):
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
            for Child in ModuleToColor:
                ReturnValue.add(Child)
                ColorList[Child] = -1
            ReturnValue = Heuristic(nx.induced_subgraph(OriginalGraph,ModuleToColor),ColorList,ReturnValue)
        elif Strategy == PrimeStrategy.Quotient:
            if(len(ModuleToColor) < 20):
                for Child in ModuleToColor:
                    ReturnValue.add(Child)
                    ColorList[Child] = -1
                ReturnValue = Heuristic(nx.induced_subgraph(OriginalGraph,ModuleToColor),ColorList,ReturnValue)
            else:
                QuotientGraph = nx.quotient_graph(OriginalGraph,[x for x in ChildrenColorMap])
                QuotientColoring = {k: -1 for k in ChildrenColorMap}
                AllowedColors = [i for i in range(len(ChildrenColorMap))]
                UsedColors = RLF(QuotientGraph,QuotientColoring,AllowedColors)
                ColorComponents = {c: [] for c in UsedColors}
                for (Node,Color) in QuotientColoring.items():
                    ColorComponents[Color].append(Node)
                for Component in ColorComponents.values():
                    ReturnValue.update(RecolorComponents(Component,ColorList,ChildrenColorMap))
        elif Strategy == PrimeStrategy.LargestModuleFirst:
            LargestModuleCount = -1
            LargestModule = -1
            for Module in MD.successors(ModuleToColor):
                if(len(Module) > LargestModuleCount):
                    LargestModuleCount = len(Module)
                    LargestModule = Module
            ColorsToUse = Colorize_Module(OriginalGraph,MD,ColorList,LargestModule,Heuristic,Strategy)
            for Node in ModuleToColor:
                ColorsToUse.add(Node)
                if( Node in LargestModule):
                    continue
                ColorList[Node] = -1
            ReturnValue = Heuristic(nx.induced_subgraph(OriginalGraph,ModuleToColor),ColorList,ColorsToUse)
        elif Strategy == PrimeStrategy.NoPrime:
            for Child in ModuleToColor:
                ReturnValue.add(Child)
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
            ReturnValue.add(CurrentColoring[Node])
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
                ReturnValue.add(CurrentColoring[DeegreeSortedVertexes[NewOffset]])
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

def GetMaxIndex(Iteratable):
    ReturnValue = 0
    MaxValue = -1
    i = 0
    for Item in Iteratable:
        if(Item > MaxValue):
            MaxValue = Item
            ReturnValue = i
        i += 1
    return ReturnValue

def RLF(GraphToColor: nx.DiGraph,CurrentColoring,ColorList):
    #Supporting coloring other stuff requires map
    #MaxIndex = max(GraphToColor.nodes)+1
    #IsAdjecent = [False]*MaxIndex
    #Degree = [0]*MaxIndex
    #TotalNodes = set(GraphToColor.nodes)
    #ComponentNodes = set()
    IsAdjecent = {i: False for i in GraphToColor.nodes}
    Degree = {i: 0 for i in GraphToColor.nodes}
    TotalNodes = set(GraphToColor.nodes)
    ComponentNodes = set()

    CurrentColor = 0
    
    for Node in GraphToColor.nodes:
        Degree[Node] = len(GraphToColor.adj[Node])
    while len(TotalNodes) > 0:
        MaxNode = 0
        MaxValue = -1
        for Node in TotalNodes:
            if(Degree[Node] > MaxValue):
                MaxValue = Degree[Node]
                MaxNode = Node
        ComponentNodes.add(MaxNode)
        for Neighbour in GraphToColor.adj[MaxNode]:
            IsAdjecent[Neighbour] = True

        Candidates = set()
        for Node in TotalNodes:
            if(Node != MaxNode and not IsAdjecent[Node]):
                Candidates.add(Node)
        while len(Candidates) > 0:
            MaxCandidate = -1
            MaxAdjecent = -1
            for Node in Candidates:
                if(IsAdjecent[Node]):
                    continue
                AdjecentCount = 0
                for Neighbour in GraphToColor.adj[Node]:
                    if(IsAdjecent[Neighbour]):
                        AdjecentCount += 1
                if(AdjecentCount > MaxAdjecent):
                    MaxCandidate = Node
                    MaxAdjecent = AdjecentCount
            if(MaxCandidate == -1):
                break
            ComponentNodes.add(MaxCandidate)
            for Neighbour in GraphToColor.adj[MaxCandidate]:
                Degree[Neighbour] -= 1
                IsAdjecent[Neighbour] = True
            Candidates.remove(MaxCandidate)
        for Node in ComponentNodes:
            CurrentColoring[Node] = CurrentColor
        TotalNodes = TotalNodes.difference(ComponentNodes)
        #resetting state
        ComponentNodes = set()
        for i in range(len(IsAdjecent)):
            IsAdjecent[i] = False
        CurrentColor += 1
    #lazy
    #ColorMap = {i[0]: i[1] for i in enumerate(ColorList)}
    ColorMap = {i[0]: i[1] for i in enumerate(ColorList)}
    ReturnValue = set()
    for Node in GraphToColor:
        CurrentColoring[Node] = ColorMap[CurrentColoring[Node]]
        ReturnValue.add(CurrentColoring[Node])
    return ReturnValue

nbiter = 1500
rep = 100
tabsize = 7
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

def LinearSearchCombinator(KIsPossibleHeuristic,GraphToColor,CurrentColoring,ColorList):
    DSaturColors = RLF(GraphToColor,CurrentColoring,ColorList)
    CurrentK = len(DSaturColors)-1
    BestColoring = []
    while True and CurrentK > 0:
        ResultColoring = CurrentColoring.copy()
        IsPossible = KIsPossibleHeuristic(GraphToColor,ResultColoring,CurrentK)
        if(IsPossible):
            BestColoring = ResultColoring
            CurrentK -= 1
        else:
            break
    if(len(BestColoring) == 0):
        return(DSaturColors)
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

def CoColorNumber(Graph,MD,CurrentModule,Coloring):
    ReturnValue = set()
    if(len(CurrentModule) == 1):
        return(set([Coloring[first(CurrentModule)]]))
    Label = MD.nodes[CurrentModule]['MDlabel']
    if Label == "p":
        return(set())
    for ChildModule in MD.successors(CurrentModule):
        ReturnValue.update(CoColorNumber(Graph,MD,ChildModule,Coloring))
    return(ReturnValue)

def GetCoVertices(MD,CurrentModule):
    ReturnValue = set()
    if(len(CurrentModule) == 1):
        return(CurrentModule)
    Label = MD.nodes[CurrentModule]['MDlabel']
    if Label == "p":
        return(set())
    for ChildModule in MD.successors(CurrentModule):
        ReturnValue.update(GetCoVertices(MD,ChildModule))
    return(ReturnValue)
def GetCoGraph(Graph,MD,Root):
    CoVertices = GetCoVertices(MD,Root)
    return(nx.induced_subgraph(Graph,CoVertices))

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
    #Heuristics = {"Tabu search": partial(BinarySearchCombinator,TabuSearch),"Greedy": Greedy,"DSatur": DSatur}
    Heuristics = {"RLF": RLF,"Greedy": Greedy,"DSatur": DSatur,"TabuCol": partial(LinearSearchCombinator,TabuSearch)}
    Strategys = {"WholePrime":
            PrimeStrategy.WholeHeuristic,"Quotient":  PrimeStrategy.Quotient}
    #Strategys = {"WholePrime": PrimeStrategy.WholeHeuristic,"Quotient":  PrimeStrategy.Quotient,"LargestModuleFirst": PrimeStrategy.LargestModuleFirst}
    #Heuristics = {"Tabu search": partial(LinearSearchCombinator,TabuSearch)}

    #GreedyColors = [i for i in range(len(G.nodes))]
    #GreedyMap = Colorize_Module(G,MD,GreedyColors,Root,Greedy,PrimeStrategy.NoPrime)
    #CoColorCount = len(CoColorNumber(G,MD,Root,GreedyColors))

    #CoVertices = GetCoVertices(MD,Root)
    #NonPrimeColorCount = len(set( [ GreedyColors[i] for i in CoVertices]))

    for (Name,Function) in Heuristics.items():
        for (StrategyName,Strategy) in Strategys.items():
            Colors = [i for i in range(len(G.nodes))]
            StartTime = time.perf_counter()
            ColorCount = Colorize_Module(G,MD,Colors,Root,Function,Strategy)
            EndTime = time.perf_counter()
            #CurrentCoColorCount = len(CoColorNumber(G,MD,Root,Colors))
            #TestCoColorCount = len(set([Colors[i] for i in CoVertices]))
            if(not VerifyColoring(G,Colors)):
                print(f"Error: Heuristic {Name} with strategy {StrategyName} resulted in an invalid coloring",file=sys.stderr)
                exit(1)
            print(Filename,RootType,Name,StrategyName,len(ColorCount),EndTime-StartTime,sep=",")

        HeuristicColorList = [-1 for i in  range(len(G.nodes))]
        HeuristicAllowedColors = [i for i in  range(len(G.nodes))]
        StartTime = time.perf_counter()
        HeuriticUsedColors = Function(G,HeuristicColorList,HeuristicAllowedColors)
        EndTime = time.perf_counter()
        #CurrentCoColorCount = len(CoColorNumber(G,MD,Root,HeuristicColorList))
        #TestCoColorCount = len(set([HeuristicColorList[i] for i in CoVertices]))
        if(not VerifyColoring(G,HeuristicColorList)):
            print("Error: modular coloring was an invalid coloring",file=sys.stderr)
            exit(1)
        print(Filename,RootType,Name,"WholeGraph",len(HeuriticUsedColors),EndTime-StartTime ,sep=",")
    #print(ColorCount,len(ColorCount),Colors)
    #print(VerifyColoring(G,Colors))
