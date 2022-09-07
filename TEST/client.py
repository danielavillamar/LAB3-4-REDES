import asyncio
from pickle import FALSE
from threading import Thread
from unicodedata import name
import slixmpp
import xmpp
import json
from slixmpp.xmlstream import ET
from slixmpp.exceptions import IqError, IqTimeout
from flooding import *
from aioconsole import *
import logging
from lsr import *
from dvr import *

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

dicLetters = {
    "A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7, "I": 8,
    "J": 9, "K": 10, "L": 11, "M": 12, "N": 13, "O": 14, "P": 15, "Q": 16, "R": 17,
    "S": 18, "T": 19, "U": 20, "V": 21, "W": 22, "X": 23, "Y": 24, "Z": 25
  }
class XMPPChat(slixmpp.ClientXMPP):

    def __init__(self, jid, password, algorithmToUse):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.user = jid
        self.algorithmToUse = algorithmToUse
        self.firstTimeFilling = True
        self.G = nx.Graph()
        self.totalNodes = 0
        self.listNodes = {}
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.messageNotifications)

    async def messageNotifications(self, event):
        message = event['body']

        params = message.split(';')

        if (self.user == params[1]):
            await aprint("Llego el mensaje al tu amigo", params)

        message_from = event['from']
        await aprint("Mensaje viene de tu amigo ", params[6])
        jumps = str(int(params[2]) + 1)
        params[2] = jumps
        params[6] = self.user

        listNodes = json.loads(params[4].replace("'", "\""))
        params[7] = list(listNodes.keys())[int(jumps)]
        print(params[7])

        nextNode = list(listNodes.values())[int(jumps)]

        newMessage = ';'.join(params)

        self.send_message(mto=nextNode, mbody=newMessage, mtype='chat')
        await asyncio.sleep(0.5)

    async def start(self, event):
        self.send_presence('chat', 'a')

        await aprint("Welcome! ", self.user)
        await self.get_roster()

        with open("users.txt") as f:
            json_data = json.load(f)
            for i in json_data['config']:
                self.totalNodes+=1
                self.listNodes[i] = json_data['config'][i]

        await aprint("1. Direct Message \n2. Log Out")
        option = await ainput("")
        if option == "1":

            if self.algorithmToUse == '2' or self.algorithmToUse == '3':
                userDestiny = await ainput("Type email to send message: ")
            else:
                userDestiny = 'all'
            
            message = await ainput("Message: ")
            protocolMessage = ""

            if (self.algorithmToUse == "1"):
                namesNodes = []
                nodeSender = ''

                # Fill graph
                with open("topologia.txt") as f:
                    json_data = json.load(f)
                    for i in json_data['config']:
                        for neighbor in json_data['config'][i]:
                            self.G.add_edge(i, neighbor, weight = 1)
                
                for key, val in self.listNodes.items():
                    if val == self.user:
                        nodeSender = key
                destiny = flooding(nodeSender, self.totalNodes, self.G)
            elif (self.algorithmToUse == "2"):

                if (self.firstTimeFilling):
                    self.firstTimeFilling = False
                    G = [] # adjacency matrix
                    namesNodes = []

                    with open("topologia.txt") as f:
                        json_data = json.load(f)
                        sizeMatrix = len(json_data['config'])

                        for i in json_data['config']:
                            lst = [999] * sizeMatrix
                            namesNodes.append(i)
                            for neighbor in json_data['config'][i]:
                                lst[dicLetters[neighbor]] = 1

                            G.append(lst)
                    
                    nodes = namesNodes[1:]

                nodeToSend = list(self.listNodes.keys())[list(self.listNodes.values()).index(userDestiny)]
                numberNode = dicLetters[nodeToSend]
                destiny = lsrAlgorithm(0, numberNode, sizeMatrix, G)
                
                for i in range(len(destiny)):
                    destiny[i] = list(dicLetters.keys())[list(dicLetters.values()).index(destiny[i])]

            elif (self.algorithmToUse == "3"):
                nodeSender = ''

                # Fill graph
                with open("topologia.txt") as f:
                    json_data = json.load(f)

                    print('111')
                    for i in json_data['config']:
                        print('111')
                        for neighbor in json_data['config'][i]:
                            self.G.add_edge(i, neighbor, weight = 1)
                
                for key, val in self.listNodes.items():
                    if val == self.user:
                        nodeSender = key
                
                nodeToSend = list(self.listNodes.keys())[list(self.listNodes.values()).index(userDestiny)]
                print("Tabla PRINT: ")
                for node in list(self.G.nodes):
                    if node != nodeSender:
                        print('Node: ', node, dvr(nodeSender, node, self.G))        
                destiny = dvr(nodeSender, nodeToSend, self.G)
                destiny = destiny['path']
            else:
                exit()

            jumps = "0"
            distance = str(len(destiny))

            # Creating the object to follow with only nodes with emails
            nodesToFollow = {}
            for i in destiny:
                if i in self.listNodes:
                    nodesToFollow[i] = self.listNodes[i]
            
            firstNodeEmail = list(nodesToFollow.values())[0]

            listNodes = str(nodesToFollow)
            print(self.user, nodesToFollow)
            protocolMessage = self.user + ';' + userDestiny + ';' + jumps + ';' + distance + ';' + listNodes + ';' + message + ';' + self.user + ';' + destiny[1]

            self.send_message(mto=firstNodeEmail, mbody=protocolMessage, mtype='chat')
            await asyncio.sleep(0.5)

            await self.start(event)
        elif (option == "2"):
            await aprint("BYE BYE :)")
            self.disconnect()
        else: 
            await aprint("Error en la opción elegida, no existe")
            await self.start(event)

print("--- Log In ---")
email = input("Email: ")
password = input("Password: ")

print("1. Floding \n2. LSR \n3. DVR")
algorithmToUse = input("Please type algorithm to use: ")



chat = XMPPChat(email, password, algorithmToUse) 
chat.register_plugin('xep_0030') # Service Discovery
chat.register_plugin('xep_0199') # XMPP Ping
chat.register_plugin("xep_0085")
chat.register_plugin("xep_0133")
chat.register_plugin('xep_0045') # Mulit-User Chat (MUC)

# Connect to the XMPP server and start processing XMPP stanzas.
chat.connect(disable_starttls=True)
chat.process(forever=False)
