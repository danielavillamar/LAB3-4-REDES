
"""
Roberto Castillo - 18546

Functions class 

>"""

class Functions:

	#This function receives the ID in the topology and returns the JID on alumchat
	def useGetJID(names,ID):
		document = open(names, "r")
		document = document.read()
		information = eval(document)
		if(information["type"]=="names"):
			names = information["config"]
			JID = names[ID]
			return(JID)
		else:
			raise Exception('The document has not a valid format for names')

	# This function receives the JID on alumchat and returns the ID in the topology
	def useGetID(names, JID):
		document = open(names, "r")
		document = document.read()
		information = eval(document)
		if(information["type"]=="names"):
			names = information["config"]
			JIDS = {v: k for k, v in names.items()}
			name = JIDS[JID]
			return(name)
		else:
			raise Exception('The document has not a valid format for names')


	# This function returns a list of the neighbors of a node
	def useGetNeighbors(topology, ID):
		document = open(topology, "r")
		document = document.read()
		information = eval(document)
		if(information["type"]=="topo"):
			names = information["config"]
			neighbors_IDs = names[ID]
			return(neighbors_IDs)
		else:
			raise Exception('The document has not a valid format for topology')
		return  