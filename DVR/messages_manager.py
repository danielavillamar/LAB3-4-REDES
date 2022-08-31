import json
import time
import numpy as np
from aioconsole import ainput
from functions import Functions

"""
Roberto Castillo - 18546

Messages manager class for the XMPP client

>"""

class MessagesManager:

    # Function to send a message to a contact
    async def dispatchMessage(self):
        contact = str(await ainput("JID del usuario al que deseas enviar mensaje: "))
        print("Mensaje:")
        message = str(await ainput(">")) 

        try:
            recipientNode = Functions.useGetID(names_file=self.useNamesFile, JID=contact)
            if(recipientNode in self.bench.columns and self.bench[recipientNode]['neighbour'] is not np.nan and self.bench[recipientNode]['distance'] is not np.inf):
                note = {}
                note["senderNode"] = self.jid
                note["recipientNode"] = contact
                note["jumps"] = 1
                note["distance"] = self.bench[recipientNode]['distance']
                note["nodesList"] = [self.jid]
                note["message"] = message
                self.send_message(mto=Functions.useGetJID(names_file=self.useNamesFile, ID=self.bench[recipientNode]['neighbour']),
                                mbody=json.dumps(note),
                                mtype='chat')
            else:
                print("El mensaje no se puede enviar a esa persona.")
        except:
            print("La persona no forma parte de tus nodos")
    
    #function to send eco message to all neighbours
    def distpatchEco(self):
        for neighbour in self.next_door:
            note = {}
            note["type"] = 'ecoSend'
            note["senderNode"] = self.nickName
            note["recipientNode"] = neighbour
            note["sendTime"] = time.time()
            self.send_message(mto=Functions.useGetJID(names_file=self.useNamesFile, ID=neighbour),
                        mbody=json.dumps(note),
                        mtype='normal')
    
    #function to sen table message to all neighbours
    def dispatchTable(self):
        for neighbour in self.next_door:
            note = {}
            note["type"] = 'table'
            note["senderNode"] = self.nickName
            note["recipientNode"] = neighbour
            note["table"] = self.bench.loc['distance'].to_dict()
            self.send_message(mto=Functions.useGetJID(names_file=self.useNamesFile, ID=neighbour),
                        mbody=json.dumps(note),
                        mtype='normal') 
