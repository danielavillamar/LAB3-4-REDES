
"""
Roberto Castillo - 18546

Fnctions to recieve important data.

>"""

# This function receives the ID in the topology and returns the JID on alumchat
def get_JID(names_file,ID):
	file = open(names_file, "r")
	file = file.read()
	info = eval(file)
	if(info["type"]=="names"):
		names = info["config"]
		JID = names[ID]
		return(JID)
	else:
		raise Exception('The file has not a valid format for names')

# This function receives the JID on alumchat and returns the ID in the topology
def get_ID(names_file, JID):
	file = open(names_file, "r")
	file = file.read()
	info = eval(file)
	if(info["type"]=="names"):
		names = info["config"]
		JIDS = {v: k for k, v in names.items()}
		name = JIDS[JID]
		return(name)
	else:
		raise Exception('The file has not a valid format for names')

# This function returns a list of the neighbors of a node
def get_neighbors(topology_file, ID):
	file = open(topology_file, "r")
	file = file.read()
	info = eval(file)
	if(info["type"]=="topo"):
		names = info["config"]
		neighbors_IDs = names[ID]
		return(neighbors_IDs)
	else:
		raise Exception('The file has not a valid format for topology')
	return  