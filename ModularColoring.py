import ModularDecomposition.modularDecomp as md
import networkx as nx
import matplotlib.pyplot as plt

# deterministic resultts
import random
import numpy

random.seed(246)        # or any integer
numpy.random.seed(4812)

def first(Iterable):
    for x in Iterable:
        return(x)


# returns the color map
def Colorize_Module(OriginalGraph,MD,ColorList,ModuleToColor,Heuristic):
    if(len(ModuleToColor) == 1):
        return(set( [ ColorList[first(ModuleToColor)] ]))
    ReturnValue = set()
    Label = MD.nodes[ModuleToColor]['MDlabel']
    ChildrenColorMap = {}
    #postorder traversal
    for Child in MD.successors(ModuleToColor):
        ChildrenColorMap[Child] = Colorize_Module(OriginalGraph,MD,ColorList,Child,Heuristic)

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
        #remove coloring for trivial modules, these are the ones we can recolor
        for Child in ChildrenColorMap:
            for Color in ChildrenColorMap[Child]:
                ReturnValue.add(Color)

        for Child in ModuleToColor:
            ColorList[Child] = -1
        ReturnValue = Heuristic(nx.induced_subgraph(OriginalGraph,ModuleToColor),ColorList,ReturnValue)
    return(ReturnValue)

# Returns a list of colors, and the chromatic number
def Colorize(OriginalGraph,MD,Heuristic):
    Root = max([module for module in MD],key=lambda x: len(x))
    Colors = [i for i in range(len(Root))]
    ColorMap = Colorize_Module(OriginalGraph,MD,Colors,Root,Heuristic)
    return (Colors,ColorMap)

# hueristic, takes a induced subgraph along with already colored parts
# and then colors the rest.
def Greedy(GraphToColor: nx.DiGraph,CurrentColoring,ColorList):
    ReturnValue = set()
    #completely arbitrary order
    for Node in GraphToColor.nodes:
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


def VerifyColoring(Graph,Coloring):
    ReturnValue = True
    for Node in Graph.nodes:
        for Neighour in Graph.adj[Node]:
            if(Coloring[Node] == Coloring[Neighour]):
                return(False)
    return(ReturnValue)

edge_prob = 0.1
G = nx.fast_gnp_random_graph(10, edge_prob)
MD = md.modularDecomposition(G)
(Colors,ColorCount) = Colorize(G,MD,Greedy)
print(ColorCount,len(ColorCount),Colors)
print(VerifyColoring(G,Colors))

nx.write_adjlist(G,"ADJList.txt")
nx.draw(G)
plt.show()
