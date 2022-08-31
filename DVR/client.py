import slixmpp
import json
import time
import pandas as pd
import numpy as np
from aioconsole import ainput
from functions import Functions
from messages_manager import MessagesManager
from settings import ECO_TIMER, TABLE_TIMER

global interval

"""
Roberto Castillo - 18546

Client class 

>"""

class Client(slixmpp.ClientXMPP):

    # Constructor of the class starting the client
    def __init__(self, jid, password, login = True):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.is_logged = False
        self.jid = jid
        self.nickName = ''
        self.useNamesFile = ''
        self.useTopoFile = ''
        self.use_status = 'Activo'
        self.next_door = list()
        self.next_doorTimeSend = None
        self.bench = None

        if not login:
            self.add_event_handler("register", self.register)
        
        # Event handler for some important functions
        self.add_event_handler("start", self.start)
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
    async def start(self, event):
        self.send_presence(pstatus=self.use_status)
        await self.get_roster()
        
        self.useTopoFile = 'D:\\Documents\\Semestre022022\\Redes\\LAB3-4-REDES\\topot-demo.txt'
        self.useNamesFile = 'D:\\Documents\\Semestre022022\\Redes\\LAB3-4-REDES\\names-demo.txt'
        
        self.nickName = Functions.useGetID(names_file=self.useNamesFile, JID=self.jid)
        self.next_door = Functions.useGetNeighbors(topology_file=self.useTopoFile, ID=self.nickName)
        self.next_doorTimeSend = np.zeros(len(self.next_door))
        
        self.bench = pd.DataFrame(index=['neighbour', 'distance'], columns=self.next_door + [self.nickName])
        self.bench.loc['distance'] = np.inf        
        self.bench.at['distance', self.nickName] = 0

        MessagesManager.distpatchEco()
        self.schedule('distpatchEco', ECO_TIMER, MessagesManager.distpatchEco, repeat=True)
        self.schedule('dispatchTable', TABLE_TIMER, MessagesManager.dispatchTable, repeat=True)

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
            
            # Dependind on the option selected, the function will be called from its own class
            if(second_menu == 1):
                await MessagesManager.dispatchMessage()

            elif(second_menu == 2):
                print("Cerrando sesión...")
            
            elif(second_menu != 0):
                print("Choose a valid option")
        
        self.cancel_schedule('distpatchEco')
        self.cancel_schedule('dispatchTable')
        self.disconnect()

    async def register(self, iq):
        note = self.Iq()
        note['type'] = 'set'
        note['register']['username'] = self.boundjid.user
        note['register']['password'] = self.password

        try:
            await note.send()
            print("Cuenta creada!")
        except:
            print("Error al crear cuenta, intenta con cambiar el nombre del usuario")
            self.disconnect()
    # Function to recieve messages, if the message is from a group, it will be printed in the group, if not, it will be printed as a direct message
    def message(self, note):
        if note['type'] == 'chat':
            message = json.loads(note['body'])
            if message["recipientNode"] == self.jid:        
                print("---------------New Notification----------------------")
                print(json.dumps(message, indent=4, sort_keys=True))
                print("--------------------------------------------------")
            else:
                message["jumps"] = message["jumps"] + 1
                message["nodesList"].append(self.jid)
                self.send_message(
                        mto=Functions.useGetJID(
                            names_file=self.useNamesFile, 
                            ID=self.bench[Functions.useGetID(names_file=self.useNamesFile, JID=message["recipientNode"])]['neighbour']
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
                    self.bench.at['distance', message["recipientNode"]] = (time.time() - message["sendTime"]) / 2
                    self.bench.at['neighbour', message["recipientNode"]] = message["recipientNode"]     


            elif message['type'] == 'table':
                table = message["table"]
                senderNode = message["senderNode"]
                for node in table.keys():
                    if node != self.nickName:
                        if node not in self.bench.columns:
                            self.bench.at['neighbour', node] = ''
                            self.bench.at['distance', node] = np.inf
                        d = min((self.bench.at['distance', senderNode] + table[node]), self.bench.at['distance', node])
                        if d != self.bench.at['distance', node]:
                            self.bench.at['distance', node] = d
                            self.bench.at['neighbour', node] = senderNode

        