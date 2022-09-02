import json
import numpy as np
from aioconsole import ainput
from functions import get_ID, get_JID

class MessagesManager:
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
                print("Message sent.")
        except:
            print("User does not exist in your nodes")