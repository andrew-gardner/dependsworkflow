#
# Depends
# Copyright (C) 2014 by Andrew Gardner & Jonas Unger.  All rights reserved.
# BSD license (LICENSE.txt for details).
#

from PySide import QtCore, QtNetwork


"""
This module is responsible for inter-process communication between any two
external programs.  It uses The QtNetwork module's QTcpSocket to send and 
receive messages in the form of a Python string.

NOTE:
This module is far from complete, but it serves its limited purpose.
"""


# TODO: What is the best way to report errors from within a module that 
#       inherits from QObject?


###############################################################################
###############################################################################
class BidirectionalCommunicationObject(QtCore.QObject):
    """
    This object holds a QTcpSocket object capable of connecting and communicating
    with another process using a QTcpSocket on given ports.  The port to listen
    for incoming communications is opened immediately, but the port to broadcast
    information is opened just before a message is sent and closed immediately
    thereafter.
    
    A 'stringReceived' QT signal is emitted when the object receives a Python
    string from an external source.
    """

    # Signals
    stringReceived = QtCore.Signal(str)

    def __init__(self, listenPort, broadcastPort=None, parent=None):
        """
        """
        QtCore.QObject.__init__(self, parent)

        # Messages, internal buffers, and data to keep
        self.received = ""
        self.toTransmit = ""
        self.broadcastPort = broadcastPort
        self.listenPort = listenPort

        # A server to listen
        self.tcpServer = QtNetwork.QTcpServer(self)
        if not self.tcpServer.listen(port=listenPort):
            print "Unable to start the server: %s." % self.tcpServer.errorString()
            return
        self.tcpServer.newConnection.connect(self._handleNewConnection)

        # A socket to tell
        self.tcpSocket = QtNetwork.QTcpSocket(self)
        self.tcpSocket.connected.connect(self._composeMessage)
        self.tcpSocket.error.connect(self._displayError)


    ###########################################################################
    ## Interface
    ###########################################################################
    def sendString(self, message):
        """
        The given string is transmitted on the object's broadcast port.
        """
        self.toTransmit = message
        self._sendTcpMessage()


    def setBroadcastPort(self, newBP):
        """
        Set the tcp port this object broadcast on.  This port is not opened
        until just before a message is sent.
        """
        self.broadcastPort = newBP
        

    def close(self):
        """
        Explicitly stops the tcp server from listening for incoming messages.
        """
        self.tcpServer.close()


    ###########################################################################
    ## Server side internals
    ###########################################################################
    def _gatherMessage(self):
        """
        Pull the most recent message out into self.received, insuring its length.
        """
        # Read out the data and insure there's something there
        byteArray = self.sender().readLine()
        if not len(byteArray):
            print "ERROR!"
            return

        # Pull the data packet size out of the first 16-bits & confirm it's all there
        stream = QtCore.QDataStream(byteArray, QtCore.QIODevice.ReadOnly)
        arraySize = stream.readUInt16()
        if arraySize != len(byteArray)-2:
            print "ERROR!"
            
        # Recover the data packet as a Python string object & let everyone know you got something
        self.received = stream.readString()
        self.stringReceived.emit(self.received)

        # Disconnect 
        self.sender().disconnectFromHost()


    def _handleNewConnection(self):
        """
        Get a handle on the next connection, setup its read callback & register 
        it for eventual cleanup.
        """
        clientConnection = self.tcpServer.nextPendingConnection()
        clientConnection.readyRead.connect(self._gatherMessage)
        clientConnection.disconnected.connect(clientConnection.deleteLater)


    ###########################################################################
    ## Client side internals
    ###########################################################################
    def _composeMessage(self):
        """
        Create a message and pass it to the network socket.
        """
        datagram = QtCore.QByteArray()
        out = QtCore.QDataStream(datagram, QtCore.QIODevice.WriteOnly)
        out.setVersion(QtCore.QDataStream.Qt_4_0)
        out.writeUInt16(0)
        out.writeString(self.toTransmit)
        out.device().seek(0)
        out.writeUInt16(datagram.size() - 2)

        written = self.tcpSocket.write(datagram)
        if written != datagram.size():
            print "BidirectionalCommunication error - message not sent"
        self.tcpSocket.flush()
    
    
    def _sendTcpMessage(self):
        """
        Closes then opens a connection to the host - when the connection is made,
        sendMessage kicks in and sends whatever is stored in self.toTransmit
        """
        self.tcpSocket.abort()
        self.tcpSocket.connectToHost('Localhost', self.broadcastPort)
    
    
    def _displayError(self, socketError):
        """
        Prints the given error message to stdout.
        """
        if socketError == QtNetwork.QAbstractSocket.RemoteHostClosedError:
            pass
        elif socketError == QtNetwork.QAbstractSocket.HostNotFoundError:
            print "The host was not found. Please check the host name and port settings."
        elif socketError == QtNetwork.QAbstractSocket.ConnectionRefusedError:
            print "The connection was refused by the peer."
        else:
            print "The following error occurred: %s." % self.tcpSocket.errorString()
