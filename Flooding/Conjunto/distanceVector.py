# LABORATORIO 3
# Daniela Villamar, Ivan y Roberto
# Referencias
# https://slixmpp.readthedocs.io/en/latest/event_index.html

import networkx as nx

class DistanceVector():

    def __init__(self, graph, graph_dict, source, names):
        self.graph = graph
        self.graph_dict = graph_dict
        self.source = source
        self.distance, self.predecessor = self.bellman_ford(graph_dict, source)
        self.names = names
        self.neighbors = self.get_neighbors(graph_dict, source)

    def initialize(self, graph_dict, source):
        # Para cada nodo hay un emisor y receptor
        d = {} # destinatario
        p = {} # persona que lo envia
        for node in graph_dict:
            d[node] = float('Inf') 
            p[node] = None
        d[source] = 0 
        return d, p

    def relax(self, node, neighbour, graph_dict, d, p):
        if d[neighbour] > d[node] + graph_dict[node][neighbour]:
            d[neighbour]  = d[node] + graph_dict[node][neighbour]
            p[neighbour] = node

    def bellman_ford(self, graph_dict, source):
        d, p = self.initialize(graph_dict, source)
        for i in range(len(graph_dict)-1): 
            for u in graph_dict:
                for v in graph_dict[u]: 
                    self.relax(u, v, graph_dict, d, p) 
        for u in graph_dict:
            for v in graph_dict[u]:
                assert d[v] <= d[u] + graph_dict[u][v]

        return d, p

    def get_neighbors(self, graph_dict, source):
        # Listado de vecinos

        return list(graph_dict[source].keys())


    def update_graph(self, graph_dict):
        # grafico

        updated_graph = {}

        for node in graph_dict:
            updated_graph[node] = {}
            for neighbor_node in graph_dict[node]:
                updated_graph[node][neighbor_node] = graph_dict[node][neighbor_node]['weight']

        self.graph_dict = updated_graph
        self.distance, self.predecessor = self.bellman_ford(updated_graph, self.source)
        self.neighbors = self.get_neighbors(updated_graph, self.source)

    def shortest_path(self, target):
        # short path

        for key in self.names:
            if self.names[key] == target:
                return nx.bellman_ford_path(self.graph, self.source, key)
        return None
