from aioconsole import ainput
from slixmpp.xmlstream.asyncio import asyncio
from tabulate import tabulate
import pandas as pd

"""
Roberto Castillo - 18546

Contacts manager class for the XMPP client

>"""

doze = 3

class ContactsManager:

    # Function to print the list of contacts
    async def contactsList(self):

        connections = []
        
        await asyncio.sleep(doze)

        roster = self.client_roster.groups()
        for group in roster:
            for jid in roster[group]:
                status = 'Away'
                conexions = self.client_roster.presence(jid)                           
                for answer, pres in conexions.items():
                    if pres['status']:
                        status = pres['status']

                connections.append([
                    jid,
                    status
                ])
                connections

        if len(connections)==0:
            print('There are no connections online') 
        else:
            df = pd.DataFrame(connections, columns = ['Email', 'Status'])
            print(tabulate(df, headers='keys', tablefmt='psql'))
    
    # Function to add a new contact
    async def newContact(self):
        try:
            addContact = str(await ainput("Email: "))
            self.send_presence_subscription(pto=addContact)
            print('The user has been added')
        except:
            print('Something happened adding the user, try again')
    
    # Get the information of a single contact
    async def contactInformation(self):

        contact = str(await ainput("Email: "))
        connections = []
        
        await asyncio.sleep(doze)

        roster = self.client_roster.groups()
        for group in roster:
            for jid in roster[group]:
                status = 'Away'
                sub = self.client_roster[jid]['subscription']
                name = self.client_roster[jid]['name']
                conexions = self.client_roster.presence(jid)                           
                for res, pres in conexions.items():
                    if pres['status']:
                        status = pres['status']
                if contact == jid:
                    connections.append([
                        jid,
                        name,
                        sub,
                        status
                    ])
                connections

            df = pd.DataFrame(connections, columns = ['Email', 'Name', 'Suscription', 'Status'])
            print(tabulate(df, headers='keys', tablefmt='psql'))

    # Remove the own user of the client
    async def removeUser(self):

        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['remove'] = True

        try:
            await resp.send()
            print("User succesfuly deleted!")
        except:
            print("User may not be deleted, try again")