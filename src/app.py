#!/usr/bin/env python
# -*- coding: utf-8 -*-
# generated by wxGlade 0.6.3 on Thu Feb 12 13:23:43 2009

import wx
import sys
from MainFrame import MainFrame
from applicationCore import applicationCore
import threading

def scanArguments(argv):
   for argument in argv:
      if argument == "--debug" or argument == "--DEBUG":
         global DEBUG
         DEBUG = True
      elif argument == "--help":
         print "Usage: %s [--debug] [--help]" % argv[0]
         sys.exit(1)

if __name__ == "__main__":
    DEBUG = False
    scanArguments(sys.argv)
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    
    mementoCondition = threading.Condition() #condition variable for the memento design pattern
    socketCondition = threading.Condition() #condition variable for the socket
    fileCondition = threading.Condition() #condition variable for file handling
    
    MainFrame = MainFrame(None, -1, mementoCondition, socketCondition,fileCondition, "")
    Core = applicationCore(MainFrame, mementoCondition, socketCondition,fileCondition, DEBUG)
    Core.start()
    app.SetTopWindow(MainFrame)
    MainFrame.Show()
    app.MainLoop()
