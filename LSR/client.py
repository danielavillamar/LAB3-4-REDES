import slixmpp
from slixmpp.xmlstream.asyncio import asyncio
from aioconsole import ainput
from contacts_manager import ContactsManager
from messages_manager import MessagesManager

"""
Roberto Castillo - 18546

Client class 

>"""

class Client(slixmpp.ClientXMPP):
    
    # Constructor of the class starting the client
    def __init__(self, jid, password, login = True):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.is_logged = False
        self.nickName = ''
        self.group_email = ''
        self.use_status = 'Active'
        self.use_recieved = set()
        self.use_recieved_presenses = asyncio.Event()

        if not login:
            self.add_event_handler("register", self.register)
        
        # Event handler for some important functions
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("changed_status", self.presensesWaiting)
        self.add_event_handler("message", self.message)
        self.add_event_handler("groupchat_message", self.groupMessage)

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
        
        self.nickName = str(await ainput("Write a nickname: "))

        self.is_logged = True
        second_menu = 0
        
        while second_menu != 7 and second_menu != 8:
            try:
                second_menu = int(await ainput(""" 

Choose the number of the option you want to do:
1. Show all contacts and status
2. Add a new contact
3. Show contact details
4. Send a direct message
5. Send a message to a group
6. Change your status
7. Logout
8. Delete my account

>"""))
            except: 
                second_menu = 0
                print("Choose a valid option")                
      
            self.send_presence(pstatus=self.use_status)
            await self.get_roster()

            # Dependind on the option selected, the function will be called from its own class
            if(second_menu == 1):
                await ContactsManager.contactsList(self)

            elif(second_menu == 2):
                await ContactsManager.newContact(self)
            
            elif(second_menu == 3):
                await ContactsManager.contactInformation(self)
            
            elif(second_menu == 4):
                await MessagesManager.dispatchMessage(self)
            
            elif(second_menu == 5):
                await MessagesManager.determineGroupMessage(self)
            
            elif(second_menu == 6):
                await MessagesManager.definePresenceMessage(self)
            
            elif(second_menu == 7):
                print("Login out...")
            
            elif(second_menu == 8):
                await ContactsManager.removeUser(self)
            
            elif(second_menu != 0):
                print("Choose a valid option")
        
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
            print("Something happened creating your account, try changing your email")
            self.disconnect()

    # Function to manage presences
    def presensesWaiting(self, pres):

        self.use_recieved.add(pres['from'].bare)
        if len(self.use_recieved) >= len(self.client_roster.keys()):
            self.use_recieved_presenses.set()
        else:
            self.use_recieved_presenses.clear()

    # Function to recieve messages, if the message is from a group, it will be printed in the group, if not, it will be printed as a direct message
    def message(self, note):
        if note['type']  in ('normal', 'chat'):
            print("----------------New Notification----------------------")
            print(f"{note['from'].username}: {note['body']}")
        
        elif note['type'] == 'groupchat':
            print("----------------New Notification----------------------")
            print(f"Grupo ({note['from'].username}): {note['body']}")
        else :
            print(note)
            
    # Notifications for mentions in group messages
    def groupMessage(self, note):
        if(note['mucnick'] != self.nickName and self.nickName in note['body']):
            print(f"Someone mentioned you in a group ({note['from'].username})")

    # Function to know if the user is logged in or not in a group
    def itsOnlineInGroup(self, presence):
        if presence['muc']['nick'] != self.nickName:
            print(f"{presence['muc']['nick']} it is online in group ({presence['from'].bare})")
