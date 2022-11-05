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
 
    def register(self, client):
        """
        Add client to list of managed connections.
        """
        location = get_location(client.http_request_host)
        client_data = Client(client, None, location, time.time())
        self.clients[client.peer] = client_data
 

    def unregister(self, client):
        """
        Remove client from list of managed connections.
        """
        partner = self.clients[client.peer].partner
        if partner != None:
            self.clients[partner.peer].partner = None
            self.clients[partner.peer].object.sendMessage(b"Your partner disconnected, please wait while we reconnect you.")
            self.clients[partner.peer].time = time.time()
        self.clients.pop(client.peer)


 
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
    
    async def matchPartners(self):
        close_client: Client = None
        for client_1 in self.clients.values():
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
                    elif distance(client_1.location, client_2.location) < distance(client_1.location, client_2.location):
                        close_client = client_2

            if close_client == None:
                log.err(f"Failed to find a partner for {client_1.object.peer}")
                print(f"client {client_1.object.peer} has no partner this cycle")

            else:
                client_1.partner = close_client.object
                close_client.partner = client_1.object

        return None
    
    async def loop(self):
        log.msg("In loop")
        while True:
            time.sleep(10)
            log.msg("Starting matching process")
            await self.matchPartners()
                
 
    def communicate(self, client, payload, isBinary):
        """
        Broker message from client to its partner.
        """
        c = self.clients[client.peer]
        if not c.partner:
            log.err(f"No partner for {c.object.peer}")
            c.object.sendMessage(b"Sorry you dont have partner yet, check back in a minute")
        else:
            c.partner.sendMessage(payload)
        
async def start_server(factory):

    # static file server seving index.html as root
    root = File(".")
 
    factory.protocol = SomeServerProtocol
    resource = WebSocketResource(factory)
    # websockets resource on "/ws" path
    root.putChild(b"ws", resource)
 
    site = Site(root)
    reactor.listenTCP(8080, site)
    reactor.run()

async def main():
    task2 = asyncio.create_task(
        factory.loop())

    task1 = asyncio.create_task(
        start_server(factory))



    await task1
    await task2

if __name__ == "__main__":
    #log.startLogging(sys.stdout)
    #factory = ChatDistanceFactory(u"ws://127.0.0.1:8080")
    #asyncio.run(main())

    loc_1 = Location(40.7128, -74.0060) # NYC coordinates
    
    loc_2 = Location(34.0522, -118.2437) # LA coordinates

    loc_3 = 

    print(distance(loc_1, loc_2))

    c1 = Client(None, None, loc_1, 10)
    c2 = Client(None, None, loc_2, 20)
