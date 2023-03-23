import ModularDecomposition.modularDecomp as md

def first(Iterable):
    for x in Iterable:
        return(x)
# hueristic, takes a induced subgraph along with already colored parts
# and then colors the rest.

# Returns a list of colors, and the chromatic number
def Colorize(OriginalGraph,MD,Heuristic):
    Root = max([module for module in MD],key=lambda x: len(x))
    Colors = [i for i in range(len(Root))]
    ColorMap = Colorize_Module(MD,Colors,Root)
    return (Colors,len(ColorMap))

# returns the color map
def Colorize_Module(OriginalGraph,MD,ColorList,ModuleToColor,Heuristic):
    if(len(ModuleToColor) == 1):
        return(set(ColorList[ [x for x in ModuleToColor][0]]}))
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
        MaxMap = max(ChildrenColorMap,key=lambda x: len(x))

        for (Nodelist,Colors) in ChildrenColorMap.items():
            #recolor, random injective map
            InjectiveMap = {}
            for (Original,New) in zip(Colors,MaxMap):
                InjectiveMap[Original] = New
            for Node in Nodelist:
                ColorMap[Node] = InjectiveMap[ColorMap[Node]]
            
        ReturnValue = MaxMap

    else:
        #prime

        #remove coloring for trivial modules, these are the ones we can recolor
        for Child in MB.nodes[[ModuleToColor]:
            if(len(Child) == 1):
                ColorList[first(Child)] = -1
        ReturnValue = Heuristic(ColorList,OriginalGraph,Child)
    return(ReturnValue)

def Greedy():
    pass
