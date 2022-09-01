import slixmpp
import json
import time
import pandas as pd
import numpy as np
from aioconsole import ainput
from functions import get_ID, get_JID, get_neighbors
from messages_manager import MessagesManager
from settings import ECO_TIMER, TABLE_TIMER

"""
Roberto Castillo - 18546

Client class 

>"""

global interval

class Client(slixmpp.ClientXMPP):

    # Constructor of the class starting the client
    def __init__(self, jid, password, login = True):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.is_logged = False
        self.jid = jid
        self.names_file = ''
        self.topo_file = ''
        self.nickName = ''
        self.use_status = 'Activo'
        self.neighbors = list()
        self.neighborsTimeSend = None
        self.table = None

        if not login:
            self.add_event_handler("register", self.register)
        
        # Event handler for some important functions
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

        #Setting all necessary plugins
        self.register_plugin('xep_0030') 
        self.register_plugin('xep_0004') 
        self.register_plugin('xep_0066') 
        self.register_plugin('xep_0077') 
        self.register_plugin('xep_0199') 
        self.register_plugin('xep_0045') 
        self.register_plugin('xep_0085') 
        self.register_plugin('xep_0096') 
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')
        self.register_plugin('xep_0071')
        self.register_plugin('xep_0128')
        self.register_plugin('xep_0363')

    # Function to the second menu in the application
    async def session_start(self, event):
        self.send_presence(pstatus=self.use_status)
        await self.get_roster()
        
        self.topo_file = 'D:\\Documents\\Semestre022022\\Redes\\LAB3-4-REDES\\topo-demo.txt'
        self.names_file = 'D:\\Documents\\Semestre022022\\Redes\\LAB3-4-REDES\\names-demo.txt'
        
        self.nickName = get_ID(names_file=self.names_file, JID=self.jid)
        self.neighbors = get_neighbors(topology_file=self.topo_file, ID=self.nickName)
        self.neighborsTimeSend = np.zeros(len(self.neighbors))
        
        self.table = pd.DataFrame(index=['neighbour', 'distance'], columns=self.neighbors + [self.nickName])
        self.table.loc['distance'] = np.inf        
        self.table.at['distance', self.nickName] = 0

        self.send_eco()
        self.schedule('send_eco', ECO_TIMER, self.send_eco, repeat=True)
        self.schedule('send_table', TABLE_TIMER, self.send_table, repeat=True)

        self.is_logged = True
        second_menu = 0
        
        while second_menu != 2:
            try:
                second_menu = int(await ainput(""" 

Choose the number of the option you want to do:

1. Send a direct message
2. Logout

>"""))
            except: 
                second_menu = 0
                print("Choose a valid option")                
      
            self.send_presence(pstatus=self.use_status)
            await self.get_roster()
            
            if(second_menu == 1):
                await self.dispatchMessage()

            elif(second_menu == 2):
                print("Login out...")
            
            elif(second_menu != 0):
                print("Choose a valid option")
        
        self.cancel_schedule('send_eco')
        self.cancel_schedule('send_table')
        self.disconnect()

    # Function to register a new user
    async def register(self, iq):
        note = self.Iq()
        note['type'] = 'set'
        note['register']['username'] = self.boundjid.user
        note['register']['password'] = self.password

        try:
            await note.send()
            print("You have created your account!")
        except:
            print("Something happened creating your account, check your credentials")
            self.disconnect()

    # Function to recieve messages and notifications
    def message(self, note):
        if note['type'] == 'chat':
            message = json.loads(note['body'])
            if message["recipientNode"] == self.jid:        
                print("----------------Notification----------------------")
                print(json.dumps(message, indent=4, sort_keys=True))
            else:
                message["jumps"] = message["jumps"] + 1
                message["nodesList"].append(self.jid)
                self.send_message(
                        mto=get_JID(
                            names_file=self.names_file, 
                            ID=self.table[get_ID(names_file=self.names_file, JID=message["recipientNode"])]['neighbour']
                            ),
                        mbody=json.dumps(message),
                        mtype='chat')
        
        elif note['type'] == 'normal':
            message = json.loads(note['body'])
            
            if message['type'] == 'ecoSend':
                message['type'] = 'ecoResponse'
                self.send_message(mto=str(note['from']).split('/')[0],
                            mbody=json.dumps(message),
                            mtype='normal')

            elif message['type'] == 'ecoResponse': 
                if(time.time() - message["sendTime"] > 1):
                    message['type'] = 'ecoSend'
                    message["sendTime"] = time.time()
                    self.send_message(mto=str(note['from']).split('/')[0],
                                mbody=json.dumps(message),
                                mtype='normal')
                else:   
                    self.table.at['distance', message["recipientNode"]] = (time.time() - message["sendTime"]) / 2
                    self.table.at['neighbour', message["recipientNode"]] = message["recipientNode"]     


            elif message['type'] == 'table':
                table = message["table"]
                senderNode = message["senderNode"]
                for node in table.keys():
                    # Adds the sender node to the nodesList
                    if node != self.nickName:
                        if node not in self.table.columns:
                            self.table.at['neighbour', node] = ''
                            self.table.at['distance', node] = np.inf
                        #Check if the sender node is a neighbor of the node
                        d = min((self.table.at['distance', senderNode] + table[node]), self.table.at['distance', node])
                        if d != self.table.at['distance', node]:
                            self.table.at['distance', node] = d
                            self.table.at['neighbour', node] = senderNode

    # Function to send eco messages
    def send_eco(self):
        for neighbour in self.neighbors:
            note = {}
            note["type"] = 'ecoSend'
            note["senderNode"] = self.nickName
            note["recipientNode"] = neighbour
            note["sendTime"] = time.time()
            self.send_message(mto=get_JID(names_file=self.names_file, ID=neighbour),
                        mbody=json.dumps(note),
                        mtype='normal')
    #function to send table messages
    def send_table(self):
        for neighbour in self.neighbors:
            note = {}
            note["type"] = 'table'
            note["senderNode"] = self.nickName
            note["recipientNode"] = neighbour
            note["table"] = self.table.loc['distance'].to_dict()
            self.send_message(mto=get_JID(names_file=self.names_file, ID=neighbour),
                        mbody=json.dumps(note),
                        mtype='normal') 

    # Function to send a message to a contact
    async def dispatchMessage(self):

        contact = str(await ainput("Email of the user you want to send a message: "))
        print("Mensaje:")
        message = str(await ainput(">")) 

        try:
            recipientNode = get_ID(names_file=self.names_file, JID=contact)
            if(recipientNode in self.table.columns and self.table[recipientNode]['neighbour'] is not np.nan and self.table[recipientNode]['distance'] is not np.inf):
                note = {}
                note["senderNode"] = self.jid
                note["recipientNode"] = contact
                note["jumps"] = 1
                note["distance"] = self.table[recipientNode]['distance']
                note["nodesList"] = [self.jid]
                note["message"] = message
                self.send_message(mto=get_JID(names_file=self.names_file, ID=self.table[recipientNode]['neighbour']),
                                mbody=json.dumps(note),
                                mtype='chat')
            else:
                print("Message can not be sent to this user.")
        except:
            print("User does not exist in your nodes")

        