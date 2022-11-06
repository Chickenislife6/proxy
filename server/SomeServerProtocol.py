from autobahn.twisted.websocket import WebSocketServerProtocol

class SomeServerProtocol(WebSocketServerProtocol):
    
    def onOpen(self):

        """
        Connection from client is opened. Fires after opening
        websockets handshake has been completed and we can send
        and receive messages.
 
        Register client in factory, so that it is able to track it.
        Try to find conversation partner for this client.
        """
        self.factory.register(self)
        # self.factory.findPartner(self)
 
    def connectionLost(self, reason):
        """
        Client lost connection, either disconnected or some error.
        Remove client from list of tracked connections.
        """
        self.factory.unregister(self)
 
    def onMessage(self, payload, isBinary):
        """
        Message sent from client, communicate this message to its conversation partner,
        """
        self.factory.communicate(self, payload, isBinary)
 