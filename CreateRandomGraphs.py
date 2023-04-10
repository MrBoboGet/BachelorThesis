import networkx as nx
import random
import numpy 
from tralda.datastructures import Tree, LCA

random.seed(246)        # or any integer
numpy.random.seed(4812)


def First(Iteratable):
    for x in Iteratable:
        return(x)

# returns the graph corresponding to the cotree, as well as a mapping
# from cotree label to the corresponding vertexes in the new graph
def GetCotreeGraph(InputGraph):
    pass

# modifires graph
def LabeledCotree(InputGraph,SeriesProb):
    pass

def DisturbedGraphFromTree(InputTree,EdgeProb=0.05,SeriesProb=0.50,PrimeCount=4,PrimeDepth=2):
    LabeledTree = LabeledCotree(InputTree,SeriesProb)
    (NewGraph,VertexMap) = GetCotreeGraph(LabeledTree)
    pass


tree = Tree.random_tree(20)
treeNode = First(tree.leaves())
(NxGraph,RootNode) = tree.to_nx()
print(NxGraph.nodes)
#for i in range(20):
#    G = DisturbedGraphFromTree(Tree.random_tree(250))
#    nx.write_edgelist(G,f"RandomGraphs/{i}.edge")
