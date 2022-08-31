from aioconsole import ainput

"""
Roberto Castillo - 18546

Messages manager class for the XMPP client

>"""

class MessagesManager:

    # Function to send a message to a contact
    async def dispatchMessage(self):
    
        foreign_contact = str(await ainput("Email of the user you want to send a message: "))
        
        try:
            print("Message:")
            message = str(await ainput(">")) 
            
            self.send_message(mto=foreign_contact,
                            mbody=message,
                            mtype='chat')
        except:
            print('Can not send file, please try again') 

    #Function to send a message to a group
    async def determineGroupMessage(self):

        self.group_email = str(await ainput("Group name: "))
      
        self.add_event_handler("muc::%s::got_online" % self.group_email, self.itsOnlineInGroup)

        self.plugin['xep_0045'].join_muc(self.group_email, self.nickName)

        try:
            print("Message:")
            message = str(await ainput(">"))
        
            self.send_message(mto=self.group_email,
                            mbody=message,
                            mtype='groupchat')
        except:
            print('Can not send file, please try again') 
    
    #Function to define presence status
    async def definePresenceMessage(self):

        self.use_status = str(await ainput("Status: "))
        
        self.send_presence(pstatus=self.use_status, pnick=self.nickName)
        await self.get_roster()

