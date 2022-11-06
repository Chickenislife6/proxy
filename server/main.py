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
        self.url_set: Dict[str, Client] = {}
 
    def register(self, client: SomeServerProtocol):
        """
        Add client to list of managed connections.
        """
        location = get_location(client.http_request_host)
        client_data = Client(client, None, location, time.time())
        self.clients[client.peer] = client_data # maps the client object to the string associated with the client.

        if client.http_request_uri != "/":
            if self.url_set.get(client.http_request_uri, None) != None:
                self.url_set[client.http_request_uri].partner = client
                client_data.partner = self.url_set[client.http_request_uri].object
                self.url_set.pop(client.http_request_uri)
            else:
                self.url_set[client.http_request_uri] = client_data # adds the client and their associated URL to the database.


    def unregister(self, client): # unregisters a client and stars searching for a new one for their former partner
        """
        Remove client from list of managed connections.
        """
        if self.clients.get(client, None) == None:
            return
        partner = self.clients[client.peer].partner
        if partner != None:
            self.clients[partner.peer].partner = None
            self.clients[partner.peer].object.sendMessage(b"Your partner disconnected, please wait while we reconnect you.")
            self.clients[partner.peer].time = time.time()

        # remove client instances from both dictionaries
        self.clients.pop(client.peer)
        self.url_set.pop(client, None)
    
    def matchPartners(self):
        close_client: Client = None
        for client_1 in self.clients.values():
            log.msg(f"Matching for {client_1.object.peer}")
            
            if client_1.partner != None:
                continue
            if client_1 in self.url_set.values():
                continue

            for client_2 in self.clients.values():
                if client_2.partner != None:
                    continue
                if client_2 in self.url_set.values():
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
        c = self.clients[client.peer]

        if c.partner == None:
            self.matchPartners()
        """
        Broker message from client to its partner.
        """
        if not c.partner:
            log.err(f"No partner for {c.object.peer}")
            c.object.sendMessage(b"Sorry you dont have partner yet, check back in a minute")
        else:
            c.partner.sendMessage(payload)
        
def start_server(factory):
    # static file server seving index.html as root
    root = File(".")
    factory = ChatDistanceFactory()
    factory.protocol = SomeServerProtocol
    # websockets resource on "/ws" path
 
    reactor.listenTCP(8080, factory)
    reactor.run()

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    factory = ChatDistanceFactory(u"ws://127.0.0.1:8080")
    start_server(factory)
