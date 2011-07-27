import wx
import math
import thread

##### COLOR DEFINITIONS #####
GREEN = (75, 155, 62)
RED = (191, 17, 27)
BACKGROUND = (0, 113, 181)
CONSTRUCTION_COLOR = (121, 56, 0)
BLACK = (0,0,0)
WHITE = (255, 255, 255)

START_GREEN = (0, 165, 80)
STOP_RED = (255, 0, 0)

MODIFIED = 1
MODIFYING = 2
NOT_MODIFIED = 0

DRAGGING = 1
IDLE = 0

def ScaledToActual(SCALE,n):
   return n/SCALE

def ActualToScaled(SCALE,n):
   return n*SCALE

## class Point(wx.EvtHandler):
##    def __init__(self,coordinates):
##       wx.EvtHandler.__init__(self)
##       self.point = coordinates
##       self.Bind(wx.EVT_MOTION, self.OnMouseMove)

##    def OnMouseMove(self,evt):
##       print "il mouse e' passato sopra di me!"

class Table(wx.Panel):
    width = 3000
    height = 2100
    mousepos = (0,0)
    oldpoint = (-1,-1)
    #status_mutex = thread.allocate_lock()

    def __init__(self,parent,statusbar,mainframe,id):
        wx.Panel.__init__(self, parent, id,(0,0), size=(ActualToScaled(0.2,self.width),ActualToScaled(0.2,self.height)))
        self.statusbar = statusbar
        self.mainframe = mainframe
        self.SCALE = 0.2
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseClick)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseRelease)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)
#        self.Bind(wx.EVT_LEFT_UP,self.OnMouseRelease)
        self.status_mutex = thread.allocate_lock()
        self.status = IDLE
        self.points = []
        self.GetPositionPoints = []
        self.Centre()
        self.Show(True)

##     def GetMutex(self):
##         return self.status_mutex

    def ResetOldPoint(self):
        self.oldpoint = (-1,-1)
        self.GetPositionPoints = []

    def AddGetPositionPoint(self,point):
       self.GetPositionPoints.append(point)

    def track(self,pt1,pt2,color):
        self.table.BeginDrawing()
        self.table.SetPen(wx.Pen(color,2))
        self.table.DrawCirclePoint(pt1,2)
        self.table.DrawCirclePoint(pt2,2)
        self.table.DrawLinePoint(pt1,pt2)
        self.table.EndDrawing()

    def getScale(self):
        return self.SCALE

    def setScale(self,newScale):
        self.SCALE=newScale

    def GetStatus(self):
        self.status_mutex.acquire()
        status = self.status
        self.status_mutex.release()
        return status

    def OnMouseClick(self,evt):
       (x,y) = evt.GetPositionTuple()
       x = ScaledToActual(self.SCALE,x)
       y = (2100 - ScaledToActual(self.SCALE,y))
       if (x < 3000 and x > 0 and y < 2100 and y > 0):
          i = 0
          for point in self.points:
             distance = math.sqrt(pow(x-point[0],2)+pow(y-point[1],2))
             if distance <=50:
                self.status = DRAGGING
                self.point_selected = i
                self.point_prior_to_drag = self.points[i]
                return
             else:
                i += 1
                
          if self.status == IDLE:
             if (self.oldpoint != (-1,-1)):
                self.track(self.oldpoint,(ActualToScaled(self.SCALE,x),ActualToScaled(self.SCALE,2100)-ActualToScaled(self.SCALE,y)),BLACK)
             self.oldpoint = (ActualToScaled(self.SCALE,x),ActualToScaled(self.SCALE,2100)-ActualToScaled(self.SCALE,y))
             self.mainframe.AddGridValue((x,y))
             self.Refresh()

    def OnMouseRelease(self,evt):
       if self.status == DRAGGING:
          (x,y) = evt.GetPositionTuple()
          x = ScaledToActual(self.SCALE,x)
          y = (2100 - ScaledToActual(self.SCALE,y))

          self.status = IDLE
#          print "number",self.point_selected
#          print "prior",self.point_prior_to_drag
#          print "after",(x,y)
          self.mainframe.SetPointMoved(self.point_selected,(x,y),self.status,self.point_prior_to_drag)
          self.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))       

    def OnMouseMove(self,evt):
       (x,y) = evt.GetPositionTuple()
       x = ScaledToActual(self.SCALE,x)
       y = (2100 - ScaledToActual(self.SCALE,y))
       if (x <= 3000 and x >= 0 and y <= 2100 and y >= 0):
          if self.status == IDLE:
             self.statusbar.SetStatusText(str((x,y)),0)
             for point in self.points:
                distance = math.sqrt(pow(x-point[0],2)+pow(y-point[1],2))
                if distance <= 25:
                   self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
                   break
                else:
                   self.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))

          elif self.status == DRAGGING:
             self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
             self.mainframe.SetPointMoved(self.point_selected,(x,y),self.status,(0,0))
             self.Refresh()

    def OnPaint(self,evt):
        self.table = wx.ClientDC(self)
        self.table.BeginDrawing()

        ## BACKGROUND ##
        self.table.SetPen(wx.Pen(BACKGROUND,0))
        self.table.SetBrush(wx.Brush(BACKGROUND))
        self.table.DrawRectangle(0,0,ActualToScaled(self.SCALE,self.width),ActualToScaled(self.SCALE,self.height))

        ##RED STARTING AREA ##
        self.table.SetPen(wx.Pen(RED,0))
        self.table.SetBrush(wx.Brush(RED))
        self.table.DrawRectangle(0,ActualToScaled(self.SCALE,self.height-500),ActualToScaled(self.SCALE,500),ActualToScaled(self.SCALE,500))

        ## GREEN STARTING AREA ##
        self.table.SetPen(wx.Pen(GREEN,0))
        self.table.SetBrush(wx.Brush(GREEN))
        self.table.DrawRectangle(ActualToScaled(self.SCALE,self.width-500),ActualToScaled(self.SCALE,self.height-500),ActualToScaled(self.SCALE,500),ActualToScaled(self.SCALE,500))
        
        ## CONSTRUCTION AREA 3 ##
        self.table.SetPen(wx.Pen(CONSTRUCTION_COLOR,0))
        self.table.SetBrush(wx.Brush(CONSTRUCTION_COLOR))
        self.table.DrawCircle(ActualToScaled(self.SCALE,self.width/2),ActualToScaled(self.SCALE,self.height/2),ActualToScaled(self.SCALE,150))

        ## CONSTRUCTION AREA 1 DELIMITERS ##
        CON_WID = ActualToScaled(self.SCALE,22.0)
        CON_HEI = ActualToScaled(self.SCALE,100)
        
        self.table.SetPen(wx.Pen(WHITE,0))
        self.table.SetBrush(wx.Brush(WHITE))
        self.table.DrawRectangle(ActualToScaled(self.SCALE,578.0),0,CON_WID,CON_HEI) ##why does not work properly?
        self.table.DrawRectangle(ActualToScaled(self.SCALE,2400.0),0,CON_WID,CON_HEI)

        ## CONSTRUCTION AREA 2 & 1 ##
        CON_WID = ActualToScaled(self.SCALE,600)
        CON_HEI = ActualToScaled(self.SCALE,100)
        
        self.table.SetPen(wx.Pen(CONSTRUCTION_COLOR,0))
        self.table.SetBrush(wx.Brush(CONSTRUCTION_COLOR))
        self.table.DrawRectangle(ActualToScaled(self.SCALE,600),0,CON_WID,CON_HEI)
        self.table.SetPen(wx.Pen(BLACK,0))
        self.table.DrawRectangle(ActualToScaled(self.SCALE,1200),0,CON_WID,CON_HEI)
        self.table.SetPen(wx.Pen(CONSTRUCTION_COLOR,0))
        self.table.DrawRectangle(ActualToScaled(self.SCALE,1800),0,CON_WID,CON_HEI)

        ## LINTELS RAILS ##
        LIN_Y = ActualToScaled(self.SCALE,self.height-250)
        LIN_WID = ActualToScaled(self.SCALE,15)
        LIN_HEI  =ActualToScaled(self.SCALE,250)
        self.table.SetPen(wx.Pen(BLACK,0))
        self.table.SetBrush(wx.Brush(BLACK))
        self.table.DrawRectangle(ActualToScaled(self.SCALE,892.5),LIN_Y,LIN_WID,LIN_HEI)
        self.table.DrawRectangle(ActualToScaled(self.SCALE,1292.5),LIN_Y,LIN_WID,LIN_HEI)
        self.table.DrawRectangle(ActualToScaled(self.SCALE,1692.5),LIN_Y,LIN_WID,LIN_HEI)
        self.table.DrawRectangle(ActualToScaled(self.SCALE,2092.5),LIN_Y,LIN_WID,LIN_HEI)

        ## CONSTRUCTION AREA 2 RAILS ##
        CON_Y = ActualToScaled(self.SCALE,100)
        CON_WID = ActualToScaled(self.SCALE,15)
        CON_HEI = ActualToScaled(self.SCALE,250)
        
        self.table.DrawRectangle(ActualToScaled(self.SCALE,1297.5),CON_Y,CON_WID,CON_HEI)
        self.table.DrawRectangle(ActualToScaled(self.SCALE,1427.5),CON_Y,CON_WID,CON_HEI)
        self.table.DrawRectangle(ActualToScaled(self.SCALE,1557.5),CON_Y,CON_WID,CON_HEI)
        self.table.DrawRectangle(ActualToScaled(self.SCALE,1687.5),CON_Y,CON_WID,CON_HEI)

        ## CONSTRUCTION AREA 1 RAILS ##
        self.table.DrawRectangle(ActualToScaled(self.SCALE,1897.5),CON_Y,CON_WID,CON_HEI)
        self.table.DrawRectangle(ActualToScaled(self.SCALE,2027.5),CON_Y,CON_WID,CON_HEI)
        self.table.DrawRectangle(ActualToScaled(self.SCALE,2157.5),CON_Y,CON_WID,CON_HEI)
        self.table.DrawRectangle(ActualToScaled(self.SCALE,2287.5),CON_Y,CON_WID,CON_HEI)

        self.table.DrawRectangle(ActualToScaled(self.SCALE,1087.5),CON_Y,CON_WID,CON_HEI)
        self.table.DrawRectangle(ActualToScaled(self.SCALE,957.5),CON_Y,CON_WID,CON_HEI)
        self.table.DrawRectangle(ActualToScaled(self.SCALE,827.5),CON_Y,CON_WID,CON_HEI)
        self.table.DrawRectangle(ActualToScaled(self.SCALE,697.5),CON_Y,CON_WID,CON_HEI)

        ## POINTS ##
        pt_list = self.mainframe.GetGridValues()
        self.points = []
        if pt_list == []:
           self.oldpoint = (-1,-1)
           return
        self.oldpoint = (ActualToScaled(self.SCALE,float(pt_list[0][0])),ActualToScaled(self.SCALE,2100)-ActualToScaled(self.SCALE,float(pt_list[0][1])))
        i = 1
        for point in pt_list:
            self.track(self.oldpoint,(ActualToScaled(self.SCALE,float(point[0])),ActualToScaled(self.SCALE,2100)-ActualToScaled(self.SCALE,float(point[1]))),BLACK)
            self.points.append((float(point[0]),float(point[1])))
            #print self.points
            self.table.DrawTextPoint(str(i),(ActualToScaled(self.SCALE,float(point[0])),ActualToScaled(self.SCALE,2100)-ActualToScaled(self.SCALE,float(point[1]))))
            self.oldpoint = (ActualToScaled(self.SCALE,float(point[0])),ActualToScaled(self.SCALE,2100)-ActualToScaled(self.SCALE,float(point[1])))
            i += 1

        ## ACTUAL ROBOT TRAJECTORY POINTS ##
        if self.GetPositionPoints == []:
           return
        self.oldpoint = (ActualToScaled(self.SCALE,float(self.GetPositionPoints[0][0])),ActualToScaled(self.SCALE,2100)-ActualToScaled(self.SCALE,float(self.GetPositionPoints[0][1])))
        for point in self.GetPositionPoints:
           self.track(self.oldpoint,(ActualToScaled(self.SCALE,float(point[0])),ActualToScaled(self.SCALE,2100)-ActualToScaled(self.SCALE,float(point[1]))),WHITE)
           self.oldpoint = (ActualToScaled(self.SCALE,float(point[0])),ActualToScaled(self.SCALE,2100)-ActualToScaled(self.SCALE,float(point[1])))

            
        self.table.EndDrawing()

    def OnDrag(self,evt):
       self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

    def OnEnter(self,evt):
       self.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))
