import networkx as nx
import matplotlib.pyplot as plt
import json
import numpy as np
import pandas as pd
import random
from operator import attrgetter

G = nx.Graph()

def dvr(currentNode, targetNode, G):

    bellmanFordResults = []
    for n in G.neighbors(currentNode):
        weight = G.get_edge_data(currentNode, n)['weight']
        neighborShortestPath = nx.shortest_path(G, n, targetNode)
        sum = 0
        for edge in range(len(neighborShortestPath) - 1):
            sum += G.get_edge_data(neighborShortestPath[edge], neighborShortestPath[edge + 1])['weight']

        bellmanFordResults.append({"source": n, "target": targetNode, "result": weight + sum, "path": [currentNode] + neighborShortestPath})

    return min(bellmanFordResults, key=lambda x: x['result'])