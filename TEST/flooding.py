import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def flooding(initialNode, totalNodes, G):
    visitedNodes = []
    visitedNodes.append(initialNode)

    while len(visitedNodes) != totalNodes:
        for m in visitedNodes:
            initialNode = m
            for n in G.neighbors(initialNode):
                if n not in visitedNodes:
                    visitedNodes.append(n)

    return visitedNodes

    