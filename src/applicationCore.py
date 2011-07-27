import wx
import thread
from threading import *
import time
from client.command import Command
import socket

##NAVIGATION MODE
IO_SFL = 1
ABSOLUTE = 2

## FILE CONSTANTS ##
NONE = 0
OPEN_REQUESTED = 1
SAVE_REQUESTED = 2

## SOCKET CONSTANTS ##
NOT_CONNECTED = 0
CONNECTED = 2
CONNECTING = 1
ERROR = -1
SEND_TRAJ = 3
STOP = 4

## GRAPH CONSTANTS##
RESET = 6

MODIFYING = 2
NOT_MODIFIED = 0

ADDED_POINT = 5
MOVED_POINT = 1
MODIFIED_POINT = 7

UNDO_REQUESTED = 3
REDO_REQUESTED = 4

class TrajectoryManager:
    def __init__(self):
        self.trajectory = []

    def AddPoint(self,pt):
        self.trajectory.append(pt)

    def AddPoints(self,points_list):
        points_list.reverse()
        self.trajectory = points_list + self.trajectory
        #print self.trajectory
    
    def RemovePoint(self):
        del self.trajectory[-1]

    def GetPointsList(self):
        return self.trajectory

    def GetPoint(self,index): #index is meant to be one-based
        if len(trajectory)<index:
            return (-1,-1)
        else:
            return trajectory[index]
        
    def ResetTrajectory(self):
        self.trajectory = []

class Memento:
    def __init__(self):
        self.undoCache = []
        self.redoCache = []
        self.maxDim = 20

    ### selectors and predicates ###
    def ResetUndoCache(self):
        self.undoCache = []
        
    def ResetRedoCache(self):
        self.redoCache = []
    
    def AddToUndoCache(self,element):
        self.undoCache.insert(0,element)
        if len(self.undoCache) > self.maxDim:
            del self.undoCache[self.maxDim]
        
    def PickFirstUndoElement(self):
        toReturn = self.undoCache[0]
        del self.undoCache[0]
        if toReturn[0] != "reset":
            self.redoCache.insert(0,toReturn)
        return toReturn

    def PickFirstRedoElement(self):
        toReturn = self.redoCache[0]
        #print toReturn
        del self.redoCache[0]
        self.undoCache.insert(0,toReturn)
        return toReturn

    def isUndoListEmpty(self):
        if self.undoCache == []:
            return True
        else:
            return False

    def isRedoListEmpty(self):
        if self.redoCache == []:
            return True
        else:
            return False
    
    #### a debug method ####
    def PrintCaches(self):
        print "UndoCache:",self.undoCache
        print "RedoCache:",self.redoCache

class connectionHandler(Thread):
    def __init__(self,mainFrame,socketCondition,DEBUG):
        Thread.__init__(self)
        self.setDaemon(True)

        self.DEBUG = DEBUG
        self.mainFrame = mainFrame
        self.socket = None
        self.status = NOT_CONNECTED
        self.socketCondition = socketCondition
        
    def run(self):
        while True:
            if self.socket == None:
                if self.DEBUG:
                    print "connectionHandler: socket is None"
                while True:
                    self.socketCondition.acquire()
                    self.socketCondition.wait()
                    self.connectionDialog = self.mainFrame.GetConnectionDialog()
                    self.ip = self.connectionDialog.GetIP()
                    self.socketCondition.notify()
                    self.status = CONNECTING
                    self.connectionDialog.SetConnectionStatus(self.status)
                    self.socketCondition.release()

                    try:
                        if self.DEBUG:
                            print "connectionHandler: trying to connect"
                            print self.ip
                        self.socket = Command(self.ip)
                        self.status = CONNECTED
                        self.mainFrame.SetSocketStatus(self.status)
                        self.mainFrame.SetStatusBarConnected(self.ip)
                        self.connectionDialog.SetConnectionStatus(self.status)
                        if self.DEBUG:
                            print "connectionHandler: connected"
                        self.socketCondition.acquire()
                        self.socketCondition.notify()
                        self.socketCondition.release()
                        break

                    except socket.error,socket.timeout:
                        self.status = ERROR
                        self.mainFrame.SetSocketStatus(NOT_CONNECTED)
                        self.connectionDialog.SetConnectionStatus(self.status)
                        if self.DEBUG:
                            print "connectionHandler: error"
                        self.socketCondition.acquire()
                        self.socket = None
                        self.socketCondition.notify()
                        self.socketCondition.release()
            else:
                while True:
                    if self.socket.CheckConnection():
                        self.socketCondition.acquire()
                        self.socketCondition.wait(0.1)
                        command = self.mainFrame.GetCommand()
                        if command == SEND_TRAJ:
                            if self.mainFrame.GetNavMode() == IO_SFL:
                                points_list = self.mainFrame.GetGridValues()
                                for point in points_list:
                                    self.socket.AddPathGoIOsfl(float(point[0]),float(point[1]))
                                    if self.DEBUG:
                                        print "connectionHandler: adding to the path:",(x,y)
                                self.socket.ExecutePath()
                                if self.DEBUG:
                                    print "connectionHandler: executing the path"
                            elif self.mainFrame.GetNavMode() == ABSOLUTE:
                                points_list = self.mainFrame.GetGridValues()
                                for point in points_list:
                                    self.socket.AddPathForwardAbsolute(float(point[0]),float(point[1]))
                                    if self.DEBUG:
                                        print "connectionHandler: adding to the path:",(x,y)
                                self.socket.ExecutePath()
                                if self.DEBUG:
                                    print "connectionHandler: executing the path"
                                pass            
                        elif command ==  STOP:
                            self.socket.StopAll()
                            self.socket.ResetPath()

                        else:
                            (x,y,theta)=self.socket.GetPosition()
                            if self.DEBUG:
                                print "connectionHandler: real-time position:",(x,y)
                            self.mainFrame.GetTable().AddGetPositionPoint
                            ## receiving other informations...##
                    else:
                        if self.DEBUG:
                            print "connectionHandler: connection is down"
                            self.mainFrame.DisplayConnectionWarning()
                            self.mainFrame.SetStatusBarNotConnected()
                            self.socketCondition.release()
                        self.socket = None
                        break

class fileHandler(Thread):
    def __init__(self,mainFrame,fileCondition,memento_manager,DEBUG):
        Thread.__init__(self)
        self.setDaemon(True)

        self.DEBUG = DEBUG
        self.mainFrame = mainFrame
        self.status = NONE
        self.fileCondition = fileCondition
        self.memento_manager = memento_manager

    def run(self):
        while True:
            self.fileCondition.acquire()
            self.fileCondition.wait()
            (self.status,self.path) = self.mainFrame.GetPath()
            if self.status == NONE:
                pass
            elif self.status == SAVE_REQUESTED:
                f=open(self.path,"w")
                list_points = self.mainFrame.GetGridValues()
                print list_points
                for r in range (len(list_points)):
                    f.write(list_points[r][0]+"\n")
                    f.write(list_points[r][1]+"\n")
                f.close()
            elif self.status == OPEN_REQUESTED:
                f = open(self.path,"r")
                file_list = []
                for element in f.readlines():
                    file_list.append(element)

                points_list = []
                i = 0
                while (i<len(file_list)):
                    points_list.append((file_list[i],file_list[i+1]))
                    i += 2
                print points_list
                self.mainFrame.SetGridValues(points_list)
                self.mainFrame.SetGridStatus(NOT_MODIFIED)
                self.memento_manager.ResetUndoCache()
                self.memento_manager.ResetRedoCache()
                self.mainFrame.SetUndo(False)
                self.mainFrame.SetRedo(False)
            
class applicationCore(Thread):
    def __init__(self,mainFrame,mementoCondition,socketCondition,fileCondition,DEBUG):
        Thread.__init__(self)
        self.setDaemon(True)
        self.DEBUG = DEBUG

        if DEBUG: 
            print "      ___           ___           ___     "
            print "     /\  \         /\  \         /\__\    "
            print "    /::\  \       /::\  \       /::|  |   "
            print "   /:/\:\  \     /:/\:\  \     /:|:|  |   "
            print "  /::\~\:\  \   /::\~\:\  \   /:/|:|__|__ "
            print " /:/\:\ \:\__\ /:/\:\ \:\__\ /:/ |::::\__\ "
            print " \/_|::\/:/  / \/_|::\/:/  / \/__/~~/:/  / "
            print "    |:|::/  /     |:|::/  /        /:/  /  "
            print "    |:|\/__/      |:|\/__/        /:/  /   "
            print "    |:|  |        |:|  |         /:/  /    "
            print "     \|__|         \|__|         \/__/     "
            print "+---------------------------+"
            print "|Application Core starting  |"
        self.traj_manager = TrajectoryManager()
        self.memento_manager = Memento()
        self.mementoCondition = mementoCondition
        self.socketCondition = socketCondition
        self.fileCondition = fileCondition

        if DEBUG:
            if self.traj_manager != None:
                print "|traj_manager: started      |"
            else:
                print "|traj_manager: FAILED       |"
            if mainFrame != None:
                print "|mainFrame: started         |"
            else:
                print "|mainFrame: FAILED          |"
            if mementoCondition != None and self.memento_manager != None:
                print "|mementoCache: started      |"
            else:
                print "|mementoCache: FAILED       |"

        self.mainFrame = mainFrame
        self.table = self.mainFrame.GetTable()
        self.socketThread = connectionHandler(self.mainFrame,self.socketCondition,DEBUG)
        self.fileThread = fileHandler(self.mainFrame,self.fileCondition,self.memento_manager,DEBUG)


        if DEBUG:
            if self.fileThread != None:
                print "|fileManager: started       |"
            else:
                print "|fileManager: FAILED        |"
            if self.socketThread != None:
                print "|connectionHandler: started |"
            else:
                print "|connectionHandler: FAILED  |"
            print "|RRM is ready and working   |"   
            print "+---------------------------+"

    def run(self):
        self.socketThread.start()
        self.fileThread.start()
        while True:
            
            self.mementoCondition.acquire()
            self.mementoCondition.wait()
            
            if self.DEBUG:
                print "appl_Core: graph has been edited"

            grid_status = self.mainFrame.GetGridStatus()
            if grid_status == ADDED_POINT:
                self.memento_manager.AddToUndoCache(('added',self.mainFrame.GetGridValues()[-1]))
                self.mainFrame.SetGridStatus(NOT_MODIFIED)
                if self.DEBUG:
                    self.memento_manager.PrintCaches()
                    
            elif grid_status == MOVED_POINT:
                if self.DEBUG:
                    print "appl_Core: a point has been moved"
                movedPointInfo = self.mainFrame.GetMovedPointInfo()
                self.memento_manager.AddToUndoCache(('moved',movedPointInfo))
                if self.DEBUG:
                    self.memento_manager.PrintCaches()
                            
            elif grid_status == UNDO_REQUESTED:
                if self.DEBUG:
                    print "appl_Core: UNDO requested from user"
                command = self.memento_manager.PickFirstUndoElement()
                
                if command[0] == "added":
                    grid_list = self.mainFrame.GetGridValues()
                    if self.DEBUG:
                        print grid_list
                    del grid_list[-1] ## rimuove l'ultimo elemento
                    if self.DEBUG:
                        print grid_list
                    self.mainFrame.SetGridValues(grid_list)
                    
                elif command[0] == "reset":
                    self.mainFrame.SetGridValues(command[1])
                    
                elif command[0] == "moved":
                    grid_list = self.mainFrame.GetGridValues()
                    if self.DEBUG:
                        print grid_list
                    del grid_list[command[1][0]]
                    grid_list.insert(command[1][0],command[1][1])
                    if self.DEBUG:
                        print grid_list
                    self.mainFrame.SetGridValues(grid_list)
                    
                if self.DEBUG:
                    self.memento_manager.PrintCaches()
                self.mainFrame.SetGridStatus(NOT_MODIFIED)

                if self.memento_manager.isUndoListEmpty():
                    self.mainFrame.SetUndo(False)
                self.mainFrame.SetRedo(True)
                
            elif grid_status == REDO_REQUESTED:
                print "appl_Core: REDO requested from user"
                ##redo##
                command = self.memento_manager.PickFirstRedoElement()
                if command[0] == "added":
                    self.mainFrame.AddGridValue(command[1])

                if command[0] == "moved":
                    grid_list = self.mainFrame.GetGridValues()
                    if self.DEBUG:
                        print grid_list
                    del grid_list[command[1][0]]
                    grid_list.insert(command[1][0],command[1][2])
                    if self.DEBUG:
                        print grid_list
                    self.mainFrame.SetGridValues(grid_list)
                                    
                self.mainFrame.SetGridStatus(NOT_MODIFIED)
                if self.memento_manager.isRedoListEmpty():
                    self.mainFrame.SetRedo(False)

            elif grid_status == RESET:
                if self.DEBUG:
                    print "appl_Core: Trajectory Reset"
                self.memento_manager.AddToUndoCache(("reset",self.mainFrame.GetGridValues()))
                self.mainFrame.SetGridValues([])
                self.mainFrame.SetGridStatus(NOT_MODIFIED)
                if self.DEBUG:
                    self.memento_manager.PrintCaches()
