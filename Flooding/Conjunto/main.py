# LABORATORIO 3
# Daniela Villamar, Ivan y Roberto
# Referencias
# https://slixmpp.readthedocs.io/en/latest/event_index.html

from client import Client
from aioconsole import ainput
import networkx as nx
import getpass
from optparse import OptionParser
import yaml

def settings():
    lector_topo = open("./topo.txt", "r", encoding="utf8")
    lector_names = open("./names.txt", "r", encoding="utf8")
    topo_string = lector_topo.read()
    names_string = lector_names.read()
    topo_yaml = yaml.load(topo_string, Loader=yaml.FullLoader)
    names_yaml = yaml.load(names_string, Loader=yaml.FullLoader)
    return topo_yaml, names_yaml

def createNodes(topo, names, user):
    for key, value in names['config'].items():
        if user == value:
            return key, topo['config'][key]

def createGraph(topo, names, user):
    graph = {}
    source = None

    for key, value in topo['config'].items():
        graph[key] = {}
        for node in value:
            graph[key][node] = float('inf') 
            if names['config'][node] == user:
                source = node
    
    return graph, source

def graphPlot(topo, names):
    G = nx.DiGraph()
    G.add_nodes_from(G.nodes(data=True))
    G.add_edges_from(G.edges(data=True))

    for key, value in names['config'].items():
            G.add_node(key, jid=value)

    for key, value in topo['config'].items():
        for i in value:
            G.add_edge(key, i, weight=1)

    return G


# Client
async def main(xmpp: Client):
    corriendo = True
    while corriendo:
        print("""
        +-+-+-+-+-+-+-+-+-+-++-+-+
        +         WELCOME        +
        +-+-+-+-+-+-+-+-+-+-++-+-+
        1. Manda un mensaje
        2. Como usar este chat?
        3. Salir
        """)
        opcion = await ainput("Porfavor, selecciona una opción: ")
        if opcion == '1':
            destinatario = await ainput("Con quien quieres empezar el chat? ")
            activo = True
            while activo:
                mensaje = await ainput("Escribe tu mensaje: ")
                if (mensaje != 'volver') and len(mensaje) > 0:
                    if xmpp.algoritmo == '1':
                        mensaje = "--" + str(xmpp.jid) + "--" + str(destinatario) + "--" + str(xmpp.graph.number_of_nodes()) + "||" + str(xmpp.nodo) + "--" + str(mensaje)
                        for i in xmpp.nodes:
                            xmpp.send_message(
                                mto=xmpp.names[i],
                                mbody=mensaje,
                                mtype='chat' 
                            )
                    elif xmpp.algoritmo == '2':
                        # Shortest path
                        mensaje = "--" + str(xmpp.jid) + "--" + str(destinatario) + "--" + str(xmpp.graph.number_of_nodes()) + "||" + str(xmpp.nodo) + "--" + str(mensaje)
                        shortest_neighbor_node = xmpp.dvr.shortest_path(destinatario)
                        if shortest_neighbor_node: 
                            if shortest_neighbor_node[1] in xmpp.dvr.neighbors: # Listado de vecinos
                                # Se manda el msj
                                xmpp.send_message(
                                    mto=xmpp.names[shortest_neighbor_node[1]],
                                    mbody=mensaje,
                                    mtype='chat' 
                                )
                            else:
                                pass
                        else:
                            pass

                    elif xmpp.algoritmo == '3':
                        target = [x for x in xmpp.graph.nodes().data() if x[1]["jid"] == destinatario]
                        mensaje = "--" + str(xmpp.jid) + "--" + str(destinatario) + "--" + str(xmpp.graph.number_of_nodes()) + "||" + str(xmpp.nodo) + "--" + str(mensaje)
                        shortest = nx.shortest_path(xmpp.graph, source=xmpp.nodo, target=target[0][0])
                        if len(shortest) > 0:
                            xmpp.send_message(
                                mto=xmpp.names[shortest[1]],
                                mbody=mensaje,
                                mtype='chat' 
                            )
                    else:
                        xmpp.send_message(
                            mto=destinatario,
                            mbody=mensaje,
                            mtype='chat' 
                        )
                elif mensaje == 'volver':
                    activo = False
                else:
                    pass
        elif opcion == '2':
            corriendo = False
            xmpp.disconnect()
        else:
            pass



if __name__ == '__main__':
    # Parser de options
    optp = OptionParser()
    optp.add_option('-j', '--jid', dest='jid', help='JID to use')
    optp.add_option('-p', '--password', dest='password', help='password to use')
    optp.add_option('-a', '--algoritmo', dest='algoritmo', help='algoritmo a usar')
    opts, args = optp.parse_args()

    topo, names = settings()

    if opts.jid is None:
        opts.jid = input("Ingresa tu usuario - user@alumchat.fun: ")
    if opts.password is None:
        opts.password = getpass.getpass("Ingresa el password: ")
    if opts.algoritmo is None:
        opts.algoritmo = input("Selecciona un algoritmo: \n1. Flooding \n2. Distance Vector \n3. Link State \n")

    graph_dict, source = createGraph(topo, names, user=opts.jid)
    nodo, nodes = createNodes(topo, names, opts.jid)
    graph = graphPlot(topo, names)

    xmpp = Client(opts.jid, opts.password, opts.algoritmo, nodo, nodes, names['config'], graph, graph_dict, source)
    xmpp.connect()
    xmpp.loop.run_until_complete(xmpp.connected_event.wait())
    xmpp.loop.create_task(main(xmpp))
    xmpp.process(forever=False)