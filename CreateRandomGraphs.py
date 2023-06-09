import networkx as nx
import random
import numpy 
import sys
import os
from tralda.datastructures import Tree, LCA


def First(Iteratable):
    for x in Iteratable:
        return(x)



def UpdateCotreeGraph(ResultGraph,OriginalGraph,IDToExamine,VertexIDMap,OriginalIDToVertexes):
    #Returnvalue is Original ID to new vertexes ID map
    Returnvalue = set()
    if(OriginalGraph.out_degree(IDToExamine) == 0):
        #is leaf
        NewID = len(VertexIDMap)
        VertexIDMap[IDToExamine] = NewID
        ResultGraph.add_node(NewID)
        ContainedChildren = set([NewID])
        OriginalIDToVertexes[IDToExamine] = ContainedChildren

        Returnvalue = ContainedChildren
    else:
        #is binary
        ChildVertexes = []
        for ChildID in OriginalGraph.successors(IDToExamine):
            NewChildSet = UpdateCotreeGraph(ResultGraph,OriginalGraph,ChildID,VertexIDMap,OriginalIDToVertexes) 
            ChildVertexes.append(NewChildSet)
        Returnvalue.update(ChildVertexes[0])
        Returnvalue.update(ChildVertexes[1])

        if(OriginalGraph.nodes[IDToExamine]["Label"] == 0):
            return Returnvalue
        OriginalIDToVertexes[IDToExamine] = Returnvalue
        for u in ChildVertexes[0]:
            for v in ChildVertexes[1]:
                ResultGraph.add_edge(u,v)
    return(Returnvalue)

# returns the graph corresponding to the cotree, as well as a mapping
# from cotree label to the corresponding vertexes in the new graph
def GetCotreeGraph(InputGraph,RootID):
    ResultGraph = nx.DiGraph()
    VertexIDMap = {}
    OriginalIDToVertexes = {}
    UpdateCotreeGraph(ResultGraph,InputGraph,RootID,VertexIDMap,OriginalIDToVertexes)
    return (ResultGraph,OriginalIDToVertexes)

# modifires graph, SeriesProb not currently used
def LabeledCotree(InputGraph : nx.DiGraph,RootID,SeriesProb):
    #We know that there aren't any cycles, is a tree
    NodesToExamine = []
    #we want the graph to be connected
    InputGraph.nodes[RootID]["Label"] = 1
    NodesToExamine.extend(InputGraph.successors(RootID))
    while len(NodesToExamine) > 0:
        CurrentNode = NodesToExamine.pop()
        ChildNodes = list(InputGraph.successors(CurrentNode))
        InputGraph.nodes[CurrentNode]["Label"] = random.uniform(0,1) < SeriesProb
        NodesToExamine.extend(ChildNodes)


def RemoveDuplicateModules(Candidates,PrimeCount):
    Returnvalue = [Candidates[0]]
    for ProspectiveCandidate in Candidates:
        if(len(Returnvalue) >= PrimeCount):
            break
        PossibleCandidate = True
        for CurrentCandidates in Returnvalue:
            if(len(CurrentCandidates.intersection(ProspectiveCandidate)) > 0):
                PossibleCandidate = False
                break
        if(PossibleCandidate):
            Returnvalue.append(ProspectiveCandidate)
    return(Returnvalue)

def DisturbGraph(InputGraph,VertexMap,EdgeProb,PrimeCount,PrimeSize):
    Candidates = [ i for i in VertexMap.values() if len(i) >= PrimeSize]
    Candidates.sort(key=lambda x: len(x))
    #inefficient duplicate removal
    Candidates = RemoveDuplicateModules(Candidates,PrimeCount)
    for i in range(min(len(Candidates),PrimeCount)):
        #inefficient af
        Nodes = list(Candidates[i])
        for j in range(len(Nodes)):
            for k in range(j+1,len(Nodes)):
                if(Nodes[j] == Nodes[k]):
                    continue
                if(random.uniform(0,1) <= EdgeProb):
                    InputGraph.add_edge(Nodes[j],Nodes[k])



def DisturbedGraphFromTree(InputGraph,RootID,EdgeProb=0.05,SeriesProb=0.50,PrimeCount=4,PrimeSize=20):
    LabeledTree = LabeledCotree(InputGraph,RootID,SeriesProb)
    (NewGraph,VertexMap) = GetCotreeGraph(LabeledTree,RootID)


#tree = Tree.random_tree(20)
#treeNode = First(tree.leaves())
#(NxGraph,RootNode) = tree.to_nx()
#print(NxGraph.nodes)
for i in range(15):
    GraphSize = 500
    SeriesProb = 0.5
    EdgeProb = 0.3
    ModuleCount = 10
    ModuleSize = 20
    OutDir = "CoGraphs"
    if(len(sys.argv) > 1):
        for j in range(1,len(sys.argv)):
            if(j == 1):
                GraphSize = int(sys.argv[1])
            if(j == 2):
                SeriesProb = float(sys.argv[2])/100
            if(j == 3):
                EdgeProb = float(sys.argv[3])/100
            if(j == 4):
                ModuleCount = int(sys.argv[4])
            if(j == 5):
                ModuleSize = int(sys.argv[5])
            if(j == 6):
                OutDir = sys.argv[6]
    if(not os.path.exists(f"{OutDir}")):
        os.makedirs(f"{OutDir}")
    (OriginalTree,RootID) = Tree.random_tree(GraphSize,True).to_nx()
    LabeledCotree(OriginalTree,RootID,SeriesProb)
    (CotreeGraph,VertexMap) = GetCotreeGraph(OriginalTree,RootID)
    DisturbGraph(CotreeGraph,VertexMap,EdgeProb,ModuleCount,ModuleSize)
    nx.write_edgelist(CotreeGraph,f"{OutDir}/{i}.edge")
