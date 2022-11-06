import asyncio
import sys
import random
import time
from typing import Dict
 
from twisted.web.static import File
from twisted.python import log
from twisted.web.server import Site
from twisted.internet import reactor
 
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
 
from autobahn.twisted.resource import WebSocketResource
from SomeServerProtocol import SomeServerProtocol
from datatypes import Client, Location

from location import distance, get_location, intersect
 
 

 
 
class ChatDistanceFactory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        super(ChatDistanceFactory, self).__init__(*args, **kwargs)
        self.clients: Dict[str, Client] = {}
        self.url_set: Dict[Client, str] = {}
 
    def register(self, client: SomeServerProtocol):
        """
        Add client to list of managed connections.
        """
        location = get_location(client.http_request_host)
        client_data = Client(client, None, location, time.time())
        self.clients[client.peer] = client_data # maps the client object to the string associated with the client.
        self.url_set.update({client_data : client.http_request_uri}) # adds the client and their associated URL to the database.

        # handles whether or not another client has joined with the same URL
        for client_inst in self.url_set:
            if client_inst == client_data:
                continue
            if client_inst.partner != None:
                continue
            if self.url_set[client_inst] == self.url_set[client_data]: # connects the two clients as partners
                client_data.partner == client_inst.object
                client_inst.partner == client_data.object

 

    def unregister(self, client): # unregisters a client and stars searching for a new one for their former partner
        """
        Remove client from list of managed connections.
        """
        partner = self.clients[client.peer].partner
        if partner != None:
            self.clients[partner.peer].partner = None
            self.clients[partner.peer].object.sendMessage(b"Your partner disconnected, please wait while we reconnect you.")
            self.clients[partner.peer].time = time.time()

        # remove client instances from both dictionaries
        self.clients.pop(client.peer)
        self.url_set.pop(client)


 
    def findPartner(self, client):
        """
        Find chat partner for a client. Check if there any of tracked clients
        is idle. If there is no idle client just exit quietly. If there is
        available partner assign him/her to our client.
        """
        available_partners = [c for c in self.clients if c != client.peer and not self.clients[c]["partner"]]
        if not available_partners:
            self.clients[client.peer].object.sendMessage(b"There is no partner at the moment, please wait")
            print("no partners for {} check in a moment".format(client.peer))
        else:
            partner_key = random.choice(available_partners)
            self.clients[partner_key]["partner"] = client
            self.clients[client.peer]["partner"] = self.clients[partner_key]["object"]
    
    def matchPartners(self):
        
        close_client: Client = None
        for client_1 in self.clients.values():
            log.msg(f"Matching for {client_1.object.peer}")
            if client_1.partner != None:
                continue

            for client_2 in self.clients.values():
                if client_2.partner != None:
                    continue
                if client_1 == client_2:
                    continue
                if intersect(client_1, client_2):
                    if close_client == None:
                        close_client = client_2
                    elif distance(client_1.location, client_2.location) < distance(client_1.location, close_client.location):
                        close_client = client_2

            if close_client == None:
                log.err(f"Failed to find a partner for {client_1.object.peer}")
                print(f"client {client_1.object.peer} has no partner this cycle")

            else:
                client_1.partner = close_client.object
                close_client.partner = client_1.object

        return None

 
    def communicate(self, client, payload, isBinary):
        self.matchPartners()
        """
        Broker message from client to its partner.
        """
        c = self.clients[client.peer]
        if not c.partner:
            log.err(f"No partner for {c.object.peer}")
            c.object.sendMessage(b"Sorry you dont have partner yet, check back in a minute")
        else:
            c.partner.sendMessage(payload)
        
def start_server(factory):

    # static file server seving index.html as root
    root = File(".")
 
    factory.protocol = SomeServerProtocol
    resource = WebSocketResource(factory)
    # websockets resource on "/ws" path
    root.putChild(b"ws", resource)
 
    site = Site(root)
    reactor.listenTCP(8080, site)
    reactor.run()

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    factory = ChatDistanceFactory(u"ws://127.0.0.1:8080")
    start_server(factory)