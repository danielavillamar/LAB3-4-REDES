# LABORATORIO 3
# Daniela Villamar, Ivan y Roberto

import asyncio
from datetime import datetime
import slixmpp
import networkx as nx
import ast
import logging
from datetime import datetime
import matplotlib.pyplot as plt
from distanceVector import DistanceVector

class Client(slixmpp.ClientXMPP):
    def __init__(self, jid, password, algoritmo, nodo, nodes, names, graph, graph_dict, source):
        super().__init__(jid, password)
        self.received = set()
        self.algoritmo = algoritmo
        self.names = names
        self.graph = graph
        self.dvr = DistanceVector(graph, graph_dict, source, names)
        self.nodo = nodo
        self.nodes = nodes
        self.schedule(name="echo", callback=self.echo_message, seconds=5, repeat=True)
        self.schedule(name="update", callback=self.update_message, seconds=10, repeat=True)
        
        self.connected_event = asyncio.Event()
        self.presences_received = asyncio.Event()

        # Login y mensajes
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.message)
        
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0045') # Multi-User Chat
        self.register_plugin('xep_0199') # Ping


    # Login
    async def start(self, event):
        self.send_presence() 
        await self.get_roster()
        self.connected_event.set()

    # Get mensajes
    async def message(self, msg):
        if msg['type'] in ('normal', 'chat'):
            await self.reply_message(msg['body'])

    # Forward mensajes
    async def reply_message(self, msg):
        message = msg.split('|')
        if message[0] == '1':
            if self.algoritmo == '1':
                # Identifica para quien el mensaje
                if message[2] == self.jid:
                    print("Mesaje para: " +  message[6])
                else:
                    if int(message[3]) > 0:
                        lista = message[4].split(",")
                        # revisa donde paso
                        if self.nodo not in lista:
                            message[4] = message[4] + "," + str(self.nodo)
                            message[3] = str(int(message[3]) - 1)
                            StrMessage = "|".join(message)
                            # Forward a los vecinos
                            for i in self.nodes:
                                self.send_message(
                                    mto=self.names[i],
                                    mbody=StrMessage,
                                    mtype='chat' 
                                )  
                    else:
                        pass
            elif self.algoritmo == '2':
                # Identifica para quien el mensaje
                if message[2] == self.jid:
                    print("Este mensajito es para nosotros (tu) " +  message[6])
                else:
                    # Short Path
                    shortest_neighbor_node = self.dvr.shortest_path(message[2])
                    if shortest_neighbor_node: 
                        if shortest_neighbor_node[1] in self.dvr.neighbors: 
                            StrMessage = "|".join(message)
                            self.send_message(
                                mto=message[2],
                                mbody=StrMessage,
                                mtype='chat' 
                            )
                        else:
                            pass
                    else:
                        pass
            elif self.algoritmo == '3':
                if message[2] == self.jid:
                    print("Este mensajito es para nosotros (tu) " +  message[6])
                else:
                    if int(message[3]) > 0:
                        lista = message[4].split(",")
                        # Si el mensaje no ha pasado por nosotros - forward
                        if self.nodo not in lista:
                            message[4] = message[4] + "," + str(self.nodo)
                            message[3] = str(int(message[3]) - 1)
                            StrMessage = "|".join(message)
                            target = [x for x in self.graph.nodes().data() if x[1]["jid"] == message[2]]
                            shortest = nx.shortest_path(self.graph, source=self.nodo, target=target[0][0])
                            if len(shortest) > 0:
                                self.send_message(
                                    mto=self.names[shortest[1]],
                                    mbody=StrMessage,
                                    mtype='chat' 
                                )  
                    else:
                        pass
        elif message[0] == '2':
            if self.algoritmo == '2':
                esquemaRecibido = message[6]

                # Tabla
                divido = esquemaRecibido.split('-')
                nodos = ast.literal_eval(divido[0])
                aristas = ast.literal_eval(divido[1])
                self.graph.add_nodes_from(nodos)
                self.graph.add_weighted_edges_from(aristas)

                # DVR
                self.dvr.update_graph(nx.to_dict_of_dicts(self.graph))

                # Grafo
                dataneighbors = self.graph.nodes().data()
                dataedges = self.graph.edges.data('weight')
                StrNodes = str(dataneighbors) + "-" + str(dataedges)

                # Pa los vecinos
                for i in self.dvr.neighbors:
                    update_msg = "2|" + str(self.jid) + "|" + str(self.names[i]) + "|" + str(self.graph.number_of_nodes()) + "||" + str(self.nodo) + "|" + StrNodes
                    # Update a todos mis vecinos 
                    self.send_message(
                            mto=self.dvr.names['config'][i],
                            mbody=update_msg,
                            mtype='chat'
                        )
                
                
            elif self.algoritmo == '3':
                # Con flooding - verificar si el mensaje paso por el nodo
                if int(message[3]) > 0:
                    lista = message[4].split(",")
                    if self.nodo not in lista:
                        message[4] = message[4] + "," + str(self.nodo)
                        message[3] = str(int(message[3]) - 1)
                        esquemaRecibido = message[6]
                        StrMessage = "|".join(message)
                        dataneighbors = [x for x in self.graph.nodes().data() if x[0] in self.nodes]
                        dataedges = [x for x in self.graph.edges.data('weight') if x[1] in self.nodes and x[0]==self.nodo]
                        StrNodes = str(dataneighbors) + "-" + str(dataedges)
                        for i in self.nodes:
                            update_msg = "2|" + str(self.jid) + "|" + str(self.names[i]) + "|" + str(self.graph.number_of_nodes()) + "||" + str(self.nodo) + "|" + StrNodes
                            # Forward del update de vecino
                            self.send_message(
                                mto=self.names[i],
                                mbody=StrMessage,
                                mtype='chat' 
                            )
                            # Update a todos mis vecinos 
                            self.send_message(
                                    mto=self.names[i],
                                    mbody=update_msg,
                                    mtype='chat' 
                                )
                        
                        # Tabla
                        divido = esquemaRecibido.split('-')
                        nodos = ast.literal_eval(divido[0])
                        aristas = ast.literal_eval(divido[1])
                        self.graph.add_nodes_from(nodos)
                        self.graph.add_weighted_edges_from(aristas)
                else:
                    pass
        elif message[0] == '3':
            if message[6] == '':
                now = datetime.now()
                timestamp = datetime.timestamp(now)
                mensaje = msg + str(timestamp)
                self.send_message(
                            mto=message[1],
                            mbody=mensaje,
                            mtype='chat' 
                        )
            else:
                difference = float(message[6]) - float(message[4])
                self.graph[self.nodo][message[5]]['weight'] = difference
        else:
            pass

    def echo_message(self):
        for i in self.nodes:
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            mensaje = "3|" + str(self.jid) + "|" + str(self.names[i]) + "||"+ str(timestamp) +"|" + str(i) + "|"
            self.send_message(
                        mto=self.names[i],
                        mbody=mensaje,
                        mtype='chat' 
                    )

    def update_message(self):
        if self.algoritmo == '2':
            
            # Grafo
            dataneighbors = self.graph.nodes().data()
            dataedges = self.graph.edges.data('weight')
            StrNodes = str(dataneighbors) + "-" + str(dataedges)

            # Pa los vecinos
            for i in self.dvr.neighbors:
                update_msg = "2|" + str(self.jid) + "|" + str(self.names[i]) + "|" + str(self.graph.number_of_nodes()) + "||" + str(self.nodo) + "|" + StrNodes
                # Update a todos mis vecinos 
                self.send_message(
                        mto=self.dvr.names[i],
                        mbody=update_msg,
                        mtype='chat'
                    )
            
        elif self.algoritmo == '3':
            dataneighbors = [x for x in self.graph.nodes().data() if x[0] in self.nodes]
            dataedges = [x for x in self.graph.edges.data('weight') if x[1] in self.nodes and x[0]==self.nodo]
            StrNodes = str(dataneighbors) + "-" + str(dataedges)
            for i in self.nodes:
                update_msg = "2|" + str(self.jid) + "|" + str(self.names[i]) + "|" + str(self.graph.number_of_nodes()) + "||" + str(self.nodo) + "|" + StrNodes
                self.send_message(
                        mto=self.names[i],
                        mbody=update_msg,
                        mtype='chat' 
                    )
            
        