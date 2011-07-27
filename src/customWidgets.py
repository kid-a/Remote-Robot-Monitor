import wx

class Battery(wx.Panel):
    def __init__(self, parent, id, dim):
        wx.Panel.__init__(self, parent, id)

        self.parent = parent
        self.SetSize(dim)
        self.SetBackgroundColour('#000000')


        self.Bind(wx.EVT_PAINT, self.OnPaint)


    def OnPaint(self, event):

        dc = wx.PaintDC(self)

        dc.SetDeviceOrigin(0, 100)
        dc.SetAxisOrientation(True, True)

        pos = self.GetSize()
        x = pos[0]
        #rect = pos / 5

        for i in range(1, 21):
            #if i > rect:
            dc.SetBrush(wx.Brush('#075100'))
            dc.DrawRectangle((x/2)-20, i*4, 40, 5)
#            dc.DrawRectangle((x/2)+5, i*4, 30, 5)
#            else:
#                dc.SetBrush(wx.Brush('#36ff27'))
#                dc.DrawRectangle(10, i*4, 30, 5)
#                dc.DrawRectangle(41, i*4, 30, 5)


#class CPUWidget(wx.Frame):
#    def __init__(self, parent, id, title):
#        wx.Frame.__init__(self, parent, id, title, size=(190, 140))

#        panel = wx.Panel(self, -1)
#        centerPanel = wx.Panel(panel, -1)

#        self.cpu = CPU(centerPanel, -1)

#        hbox = wx.BoxSizer(wx.HORIZONTAL)

#        hbox.Add(centerPanel, 0,  wx.LEFT | wx.TOP, 20)

#        panel.SetSizer(hbox)

#        self.Centre()
#        self.Show(True)


#app = wx.App()
#CPUWidget(None, -1, 'Battery Status')
#app.MainLoop()

