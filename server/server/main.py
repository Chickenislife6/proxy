import sys
import random
import time
from typing import Dict
 
from twisted.web.static import File
from twisted.python import log
from twisted.web.server import Site
from twisted.internet import reactor, ssl
 
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS
 
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
        if self.clients.get(client.peer) == None:
            return
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
                    elif distance(client_1.location, client_2.location) < distance(client_1.location, client_2.location):
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
        
def start_server():
    # # static file server seving index.html as root
    # root = File(".")
    # factory = ChatDistanceFactory(u"ws://0.0.0.0:8080")
    # factory.protocol = SomeServerProtocol
    # resource = WebSocketResource(factory)
    # # websockets resource on "/wss" path
    # root.putChild(b"ws", resource)
    


    # # factory = ChatDistanceFactory(u"ws://0.0.0.0:8080")
    # # factory.protocol = SomeServerProtocol
    # # resource = WebSocketResource(factory)
    # # # websockets resource on "/ws" path
    # # root.putChild(b"ws", resource)

 
    # site = Site(root)
    # reactor.listenTCP(8080, site)
    # reactor.run()

    # ssl.create_default_context
    factory = ChatDistanceFactory()
    factory.protocol = SomeServerProtocol
    listenWS(factory, )
    reactor.listenTCP(8080, factory, )
    reactor.run()


if __name__ == "__main__":
    log.startLogging(sys.stdout)
    start_server()
