from client import Client
import socket

class Command(object):

    def __init__(self, host, port=7999):
        if host != "":
            self.connect(host,port)

    def connect (self, host, port=7999): 
        self.cli = Client(host, port)

    def disconnect(self):
        self.cli.close()

    # Position
    def GetPosition(self):
        r = self.cli.send("GetPosition\n")
        if len(r) == 3:
            return [float(x) for x in r]

    def CheckConnection(self):
        try:
            self.GetPosition()
            return True
        except socket.error:
            return False

    def ResetPosition(self):
        return self.cli.send("ResetPosition\n")
    
    def SetPosition(self, x, y, heading):
        return self.cli.send("SetPosition;" + str(x) + ";" + str(y) + ";" + str(heading) + "\n")
    
    def StopAll(self):
        return self.cli.send("StopAll\n")
    
    # Path
    def ResetPath(self):
	return self.cli.send("ResetPath\n")

    def ExecutePath(self):
        return self.cli.send("ExecutePath\n")
     
    def AddPathForwardRelative(self, distance):
        return self.cli.send("AddPathForward;" + str(distance) + "\n")
     
    def AddPathRotateRelative(self, theta):
        return self.cli.send("AddPathRotate;" + str(theta) + "\n")

    # da fare precedere sempre da un addpath heading
    def AddPathForwardAbsolute(self, x, y):
        return self.cli.send("AddPathFA;" + str(x) + ";" + str(y) + "\n")
    
    def AddPathRotateAbsolute(self, theta):
        return self.cli.send("AddPathRA;" + str(theta) + "\n")

    def AddPathHeading(self, x, y):
        return self.cli.send("AddPathHD;" + str(x) + ";" + str(y) + "\n")
     
    def AddPathGoIOsfl(self, x, y):
        return self.cli.send("AddPathGo;" + str(x) + ";" + str(y) + "\n")

    def ExecPathForward(self, distance):
        return self.cli.send("ExecPathForward;" + str(distance) + "\n")
    
    def ExecPathRotate(self, theta):
        return self.cli.send("ExecPathRotate;" + str(theta) + "\n")
    
    def ExecPathForwardAbsolute(self, x, y):
        return self.cli.send("ExecPathFA;" + str(x) + ";" + str(y) + "\n")
    
    def ExecPathRotateAbsolute(self, theta):
        return self.cli.send("ExecPathRA;" + str(theta) + "\n")

    def ExecPathHeading(self, x, y):
        return self.cli.send("ExecPathHD;" + str(x) + ";" + str(y) + "\n")
    
    def ExecPathGoIOsfl(self, x, y):
        return self.cli.send("ExecPathGo;" + str(x) + ";" + str(y) + "\n")

    ##aggiungere exec traiettoria circolare, dato il raggio
