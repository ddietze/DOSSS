"""
.. module: opsim.opsim_mainframe
   :platform: Windows
.. moduleauthor:: Daniel Dietze <daniel.dietze@berkeley.edu>

Main window of DOSSS.

..
   This program is free software: you can redistribute it and/or modify 
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.

   Copyright 2008 Daniel Dietze <daniel.dietze@berkeley.edu>.   
"""
import wx
import os
from copy import deepcopy
from core.opsim_objects import *
from core.opsim_lightray import *
import pickle       # save and load files

# that is the main frame class
class MainFrame(wx.Frame):
    """The main frame class derived from wx.Frame. This handles all user input.
    """
    # init the frame and define all objects and menu items
    def __init__(self, title, *args):
        wx.Frame.__init__(self, None, -1, title, *args)
        
        # set global variables for canvas
        self.origin_x = 0   	# current coordinates of the upper left corner in object space
        self.origin_y = 0
        self.zoom = 1       	# float value giving the current zoom level
        self.drawGrid = 1   	# show grid?        
        self.snapToGrid = 1 	# snap objects to grid?
        self.gridStepSize = 10
        
        self.sceneFileName = "" # variables used for saving files
        self.canClose = 1
        
        self.maxNumberOfIterations = 20 # maximum number of ray segments created during rendering
        
        # for scrolling
        self.mouse_pos = (0,0)
        self.old_origin = (0,0)
        
        # object list
        self.objects = []
        self.active_object = -1
        
        # light rays
        self.rays = []
        self.display_rays = 0

        # create canvas for drawing
        self.SetBackgroundColour("White")
        self.InitBuffer()        
        
        # create menu bar
        self.createMenu()
               
        # create status bar and set status text
        self.createStatusBar() 
        
        # canvas events
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
        # mouse events
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)

        # keyboard events
        self.Bind(wx.EVT_CHAR, self.onChar)
    
    def createStatusBar(self):
        self.statusbar = self.CreateStatusBar()        
        self.statusbar.SetFieldsCount(3)
        self.statusbar.SetStatusWidths([-3, -2, -1])
        self.statusbar.SetStatusText("Welcome to DOSSS!", 0)  
        self.statusbar.SetStatusText("Origin: (0, 0)", 1)
    
    def setHint(self, text):
        self.statusbar.PushStatusText(text, 0)   

    def clearHint(self):
        self.statusbar.PopStatusText(0)  
    
    # mouse events
    def OnMotion(self, event):
        pos = tuple(event.GetPosition())
        # V1.1 new: rescale the mouse coordinates to scene coordinates
        nposx = pos[0] / self.zoom + self.origin_x
        nposy = pos[1] / self.zoom + self.origin_y		
        #self.statusbar.SetStatusText("Pos: %s" % str(pos), 2)
        self.statusbar.SetStatusText("Pos: (%s, %s)" % (str(nposx), str(nposy)), 2)
        self.statusbar.SetStatusText("Origin: (%s, %s)" % (str(self.origin_x), str(self.origin_y)), 1)
        # right mouse button moves the scene
        if event.Dragging():
            dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)     
            if event.RightIsDown(): # move scene                               
                self.origin_x = self.old_origin[0] - (pos[0] - self.mouse_pos[0]) / self.zoom
                self.origin_y = self.old_origin[1] - (pos[1] - self.mouse_pos[1]) / self.zoom                
            elif event.LeftIsDown() and self.active_object != -1: # move object                                  
                nx = self.old_origin[0] + (pos[0] - self.mouse_pos[0]) / self.zoom
                ny = self.old_origin[1] + (pos[1] - self.mouse_pos[1]) / self.zoom
                if (self.snapToGrid): # snap nx and ny to nearest grid point                   
                    step = self.gridStepSize                  
                    nx = round((nx) / step) * step
                    ny = round((ny) / step) * step
                    
                self.objects[self.active_object].set_position(nx, ny)
                self.display_rays = 0
                self.canClose = 0
                
            self.DrawScene(dc)
        
        event.Skip()            
    
    def OnRightDown(self, event):                                
        self.setHint("Scroll Mode")
        self.mouse_pos = tuple(event.GetPosition())
        self.old_origin = (self.origin_x, self.origin_y)
        try:
            self.CaptureMouse()
        except Exception as e:
            print("Error onRightDown when capturing mouse:", e)
        
    def OnRightUp(self, event):
        if self.HasCapture():                       
            self.ReleaseMouse()
            self.clearHint()        
        
    def OnLeftDown(self, event):
        # select objects with mouse click
        pos = tuple(event.GetPosition())
        onr = self.getObjectUnderMouse(pos)
            
        if(onr != -1):
            if(self.active_object != -1):
                self.objects[self.active_object].active = 0
            self.active_object = onr
            self.objects[onr].active = 1
            self.InitBuffer()
            # prepare for moving the object
            self.CaptureMouse()
            self.mouse_pos = pos            
            self.old_origin = self.objects[self.active_object].get_position()
            self.setHint("Move Object...")            
        elif(self.active_object != -1):
            self.objects[self.active_object].active = 0
            self.active_object = -1
            self.InitBuffer()
        
        event.Skip()
    
    def OnLeftUp(self, event):
        if self.HasCapture():                       
            self.ReleaseMouse()
            self.clearHint()
        event.Skip()
    
    def OnLeftDClick(self, event):
        pos = tuple(event.GetPosition())
        onr = self.getObjectUnderMouse(pos)
        if(onr != -1):
            self.objects[onr].ShowPropertyDialog()
            self.display_rays = 0
            self.canClose = 0
            self.InitBuffer()
        event.Skip()
    
    def getObjectUnderMouse(self, mousepos):
        # get click position in lab space        
        cposx = mousepos[0] #self.origin_x + mousepos[0] / self.zoom
        cposy = mousepos[1] #self.origin_y + mousepos[1] / self.zoom        
        
        # now check if we are inside a bounding box        
        onr = -1        
        for i in range(len(self.objects)):            
            bb = self.objects[i].get_bbox()            
            if(cposx >= bb[0] and cposx <= bb[2] and cposy >= bb[1] and cposy <= bb[3]):
                onr = i
                #break
            
        return onr
    
    # menu functions
    def createMenu(self):
        menuFile = wx.Menu()
        #menuFile.Append(1, "&About...")
        menuFile.Append(13, "New")
        menuFile.Append(14, "Open..")
        menuFile.Append(15, "Save.. (STRG + s)")
        menuFile.Append(16, "Save as..")
        menuFile.AppendSeparator()
        menuFile.Append(17, "Export..")
        menuFile.AppendSeparator()
        menuFile.Append(1, "E&xit")
    
        # display menu
        menuZoom = wx.Menu()
        menuZoom.Append(2, "100%")
        menuZoom.AppendSeparator()
        menuZoom.Append(3, "25%")        
        menuZoom.Append(4, "50%")        
        menuZoom.Append(5, "200%")        
        menuZoom.Append(6, "400%")       
        menuZoom.Append(20, "800%")       
        menuZoom.AppendSeparator()
        menuZoom.AppendCheckItem(7, "Show Grid")        
        if (self.drawGrid):
            menuZoom.Check(7, 1)    # set show grid to default
        menuZoom.AppendCheckItem(8, "Snap To Grid")        
        if (self.snapToGrid):
            menuZoom.Check(8, 1)    # set snap to grid to default
        menuZoom.Append(21, "Set Grid Size..")
        menuZoom.AppendSeparator()
        menuZoom.Append(19, "Center Scene")        
        menuZoom.AppendSeparator()
        menuZoom.Append(18, "Redraw Screen")        

        # create the object menu
        # object id's start with 1000
        menuObject = wx.Menu()
        menuNewObject = wx.Menu()
        i = 1000
        for ob in objectList():
            menuNewObject.Append(i, ob)
            self.Bind(wx.EVT_MENU, self.OnNewObject, id = i)
            i = i + 1
        menuObject.Append(9, "New...", menuNewObject)
        menuObject.Append(11, "Clone (STRG + c)")
        menuObject.Append(10, "Delete (DEL)")
        menuObject.AppendSeparator()
        menuObject.Append(22, "Move forward (IMG UP)")
        menuObject.Append(23, "Move backward (IMG DOWN)")
        
        # rendering menu
        menuRender = wx.Menu()
        menuRender.Append(12, "Render (F5)")
        
        # put the menus together
        menuBar = wx.MenuBar()
        menuBar.Append(menuFile, "&File")
        menuBar.Append(menuZoom, "&Display")     
        menuBar.Append(menuObject, "&Object") 
        menuBar.Append(menuRender, "&Render")  
        self.SetMenuBar(menuBar)
        
        # event bindings for menu       
        self.Bind(wx.EVT_MENU, self.OnQuit, id = 1)
        self.Bind(wx.EVT_MENU, self.OnZoom100, id = 2)
        self.Bind(wx.EVT_MENU, self.OnZoom25, id = 3)
        self.Bind(wx.EVT_MENU, self.OnZoom50, id = 4)
        self.Bind(wx.EVT_MENU, self.OnZoom200, id = 5)
        self.Bind(wx.EVT_MENU, self.OnZoom400, id = 6)
        self.Bind(wx.EVT_MENU, self.OnZoom800, id = 20)
        self.Bind(wx.EVT_MENU, self.OnSetGridSize, id = 21)
        self.Bind(wx.EVT_MENU, self.OnShowGrid, id = 7)
        self.Bind(wx.EVT_MENU, self.OnSnapToGrid, id = 8)
        self.Bind(wx.EVT_MENU, self.OnObjectDelete, id = 10)        
        self.Bind(wx.EVT_MENU, self.OnObjectClone, id = 11)
        self.Bind(wx.EVT_MENU, self.OnObjectUp, id = 22)
        self.Bind(wx.EVT_MENU, self.OnObjectDown, id = 23)
        self.Bind(wx.EVT_MENU, self.OnRender, id = 12)
        self.Bind(wx.EVT_MENU, self.OnFileNew, id = 13)
        self.Bind(wx.EVT_MENU, self.OnFileOpen, id = 14)
        self.Bind(wx.EVT_MENU, self.OnFileSave, id = 15)
        self.Bind(wx.EVT_MENU, self.OnFileSaveAs, id = 16)
        self.Bind(wx.EVT_MENU, self.OnFileExport, id = 17)
        self.Bind(wx.EVT_MENU, self.OnRedraw, id = 18)
        self.Bind(wx.EVT_MENU, self.OnCenter, id = 19)
    
    def onChar(self, event):
        key = event.GetKeyCode()
        if(key == wx.WXK_F5):
            self.OnRender(event)
        if(key == wx.WXK_DELETE):
            self.OnObjectDelete(event)
        if(key == 3 and event.GetModifiers() == wx.MOD_CONTROL):
            self.OnObjectClone(event)
        if(key == 19 and event.GetModifiers() == wx.MOD_CONTROL):
            self.OnFileSave(event)
        if(key == wx.WXK_PAGEUP):
            self.OnObjectUp(event)
        if(key == wx.WXK_PAGEDOWN):
            self.OnObjectDown(event)
        if(key == wx.WXK_LEFT):
            self.OnObjectMoveLeft()
        if(key == wx.WXK_RIGHT):
            self.OnObjectMoveRight()
        if(key == wx.WXK_UP):
            self.OnObjectMoveUp()
        if(key == wx.WXK_DOWN):
            self.OnObjectMoveDown()
        event.Skip()

    def OnRedraw(self, event):
        self.InitBuffer()
        
    def OnCenter(self, event):
        self.origin_x = 0
        self.origin_y = 0
        self.InitBuffer()
    
    def OnFileExport(self, event):
        # refresh bitmap
        self.InitBuffer()
        # get "export to" - filename
        dialog = wx.FileDialog(self, "Choose a filename", os.getcwd(), "", "SVG Files (*.svg)|*.svg|PNG Files (*.png)|*.png")
        if dialog.ShowModal() == wx.ID_OK:
            # get name
            filename = dialog.GetPath()                            
            
            if(filename[-3:] == "png"):	# save as bitmap
                # create image object
                img = wx.ImageFromBitmap(self.buffer)
                # save to file
                img.SaveFile(filename, wx.BITMAP_TYPE_PNG)
            else:						# save as vector graphic
                fp = open(filename, "w")
                # write header
                fp.write("<?xml version=\"1.0\"?>\n")
                #fp.write("<svg height=\"%d\" width=\"%d\">\n" % (self.height,self.width))
                #fp.write("<svg height=\"1000mm\" width=\"1000mm\">\n")
                fp.write("<svg>\n")
                fp.write("<g>\n")
                # write all objects
                for o in self.objects:
                    fp.write(o.svgstr())
                # write all rays
                for r in self.rays:
                    fp.write(r.svgstr())
                # write footer
                fp.write("</g></svg>")
                fp.close()
        dialog.Destroy()         
    
    def OnFileSaveAs(self, event):
        # display choose file dialog and override self.sceneFileName
        dialog = wx.FileDialog(self, "Choose a filename", os.getcwd(), "", "DOSSS Files (*.dos)|*.dos")
        if dialog.ShowModal() == wx.ID_OK:
            self.sceneFileName = dialog.GetPath()
            self.OnFileSave()            
        dialog.Destroy()  
   
    def OnFileSave(self, event = None):
        if self.sceneFileName == "":
            dialog = wx.FileDialog(self, "Choose a filename for saving", os.getcwd(), "", "DOSSS Files (*.dos)|*.dos")
            if dialog.ShowModal() == wx.ID_OK:
                self.sceneFileName = dialog.GetPath()
            dialog.Destroy()
        if self.sceneFileName != "":
            # now save the objects list
            fp = open(self.sceneFileName, 'wb')
            pickle.dump(self.objects, fp)
            fp.close()
            self.canClose = 1
    
    def OnFileOpen(self, event):
        if not self.canClose:
            retval = wx.MessageBox("Save file before opening another scene?", "Open...", style = wx.YES_NO | wx.CANCEL)
            if retval == wx.CANCEL:
                return
            elif retval == wx.YES:
                self.OnFileSave()
        dialog = wx.FileDialog(self, "Choose a filename for opening", os.getcwd(), "", "DOSSS Files (*.dos)|*.dos")
        if dialog.ShowModal() == wx.ID_OK:
            self.sceneFileName = dialog.GetPath()
            self.rays = []
            self.objects = []
            self.zoom = 1
            self.origin_x = 0
            self.origin_y = 0
            self.canClose = 1          
            self.display_rays = 0
            self.active_object = -1
            # open dump file
            fp = open(self.sceneFileName, 'rb')
            self.objects = pickle.load(fp)
            fp.close            
            self.InitBuffer()
        dialog.Destroy()
        
    def OnFileNew(self, event):
        if not self.canClose:
            retval = wx.MessageBox("Save file before creating new scene?", "New...", style = wx.YES_NO | wx.CANCEL)
            if retval != wx.CANCEL:
                if retval == wx.YES:
                    self.OnFileSave()
                self.rays = []
                self.objects = []
                self.zoom = 1
                self.origin_x = 0
                self.origin_y = 0
                self.canClose = 1          
                self.sceneFileName = ""
                self.display_rays = 0
                self.active_object = -1     
                self.InitBuffer() 
        else:
            self.rays = []
            self.objects = []
            self.zoom = 1
            self.origin_x = 0
            self.origin_y = 0
            self.canClose = 1
            self.sceneFileName = ""
            self.display_rays = 0
            self.active_object = -1
            self.InitBuffer()
        
    def OnQuit(self, event):
        if not self.canClose:
            retval = wx.MessageBox("Save file before quit?", "Quit...", style = wx.YES_NO | wx.CANCEL)            
            if retval == wx.CANCEL:
                return
            elif retval == wx.YES:
                self.OnFileSave()
                self.Close()
            elif retval == wx.NO:
                self.Close()
        else:
            self.Close()
    
    def setZoom(self, zoom):
        # get lab coordinates of center
        ox = self.origin_x
        oy = self.origin_y
        size = self.GetClientSize()
        cx = ox + (size[0] / 2) / self.zoom
        cy = oy + (size[1] / 2) / self.zoom
        
        # set new zoom
        self.zoom = zoom
        
        # calculate new origin from center coordinates
        self.origin_x = cx - (size[0] / 2) / self.zoom
        self.origin_y = cy - (size[1] / 2) / self.zoom        
        
        # redraw
        self.InitBuffer()

    def OnSetGridSize(self, event):
        value = wx.GetNumberFromUser("New grid size in mm (1..100):", "", "Set grid size", self.gridStepSize, min=1, max=100)
        if(value >= 1):
            self.gridStepSize = value
            self.InitBuffer()

    def OnZoom100(self, event):
        self.setZoom(1)        

    def OnZoom25(self, event):
        self.setZoom(0.25)

    def OnZoom50(self, event):
        self.setZoom(0.5)

    def OnZoom200(self, event):
        self.setZoom(2)

    def OnZoom400(self, event):
        self.setZoom(4)
    
    def OnZoom800(self, event):
        self.setZoom(8)

    def OnShowGrid(self, event):
        self.drawGrid = not self.drawGrid
        self.InitBuffer()

    def OnSnapToGrid(self, event):
        self.snapToGrid = not self.snapToGrid
    
    def OnNewObject(self, event):
        #event.Skip()
        try:
            # get object-type
            itemId = list(objectList())[event.GetId() - 1000]
            print("Create", itemId)
            
            # get lab coordinates of center
            ox = self.origin_x
            oy = self.origin_y
            size = self.GetClientSize()
            cx = ox + (size[0] / 2) / self.zoom
            cy = oy + (size[1] / 2) / self.zoom
            
            # add new object
            obj = getNewObject(itemId, cx, cy)
            self.objects.append(obj)
            
            # redraw the scene
            self.display_rays = 0
            self.canClose = 0
            self.InitBuffer()
        except Exception as e:
            print("Error creating new object:", e)
            raise
            pass
            
    def OnObjectDelete(self, event):        
        # if an object is active
        if(self.active_object != -1):
            # slice the object out of the objects list
            self.objects = self.objects[0:self.active_object] + self.objects[self.active_object + 1:]
            self.active_object = -1
            
            # redraw scene
            self.display_rays = 0
            self.canClose = 0
            self.InitBuffer()            

    def OnObjectMoveLeft(self):
            # if an object is active
        if(self.active_object != -1):
            dx = -1
            if(self.snapToGrid == 1):
                dx = -self.gridStepSize
            self.objects[self.active_object].position[0] += dx
            
            self.display_rays = 0
            self.canClose = 0
            self.InitBuffer()

    def OnObjectMoveRight(self):
            # if an object is active
        if(self.active_object != -1):
            dx = 1
            if(self.snapToGrid == 1):
                dx = self.gridStepSize
            self.objects[self.active_object].position[0] += dx
            
            self.display_rays = 0
            self.canClose = 0
            self.InitBuffer()

    def OnObjectMoveUp(self):
            # if an object is active
        if(self.active_object != -1):
            dy = -1
            if(self.snapToGrid == 1):
                dy = -self.gridStepSize
            self.objects[self.active_object].position[1] += dy
            
            self.display_rays = 0
            self.canClose = 0
            self.InitBuffer()
    
    def OnObjectMoveDown(self):
            # if an object is active
        if(self.active_object != -1):
            dy = 1
            if(self.snapToGrid == 1):
                dy = self.gridStepSize
            self.objects[self.active_object].position[1] += dy
            
            self.display_rays = 0
            self.canClose = 0
            self.InitBuffer()

    def OnObjectUp(self, event):
        # if an object is active
        if(self.active_object != -1 and self.active_object < len(self.objects) - 1 ):
            # swap
            dummy = self.objects[self.active_object]
            self.objects[self.active_object] = self.objects[self.active_object + 1]
            self.objects[self.active_object + 1] = dummy
            self.active_object = self.active_object + 1

            # redraw
            self.canClose = 0
            self.InitBuffer()

    def OnObjectDown(self, event):
        # if an object is active
        if(self.active_object != -1 and self.active_object > 0 ):
            # swap
            dummy = self.objects[self.active_object]
            self.objects[self.active_object] = self.objects[self.active_object - 1]
            self.objects[self.active_object - 1] = dummy
            self.active_object = self.active_object - 1

            # redraw
            self.canClose = 0
            self.InitBuffer()

    def OnObjectClone(self, event):        
        if(self.active_object != -1):
            obj = deepcopy(self.objects[self.active_object])
            obj.active = 0
            ox, oy = obj.get_position()            
            obj.set_position(ox + 10, oy + 10)
            self.objects.append(obj)
            
            self.display_rays = 0
            self.canClose = 0
            self.InitBuffer()  
        
    # canvas functions
    def OnSize(self, event):
        self.reInitBuffer = True
    
    def OnIdle(self, event):
        if self.reInitBuffer:
            self.InitBuffer()
            self.Refresh(False)
    
    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self, self.buffer)        
    
    def InitBuffer(self):
        size = self.GetClientSize()
        self.buffer = wx.Bitmap(size.width, size.height)                
        self.reInitBuffer = False
        # create buffered dc
        dc = wx.BufferedDC(None, self.buffer)
        
        # here comes the drawing
        self.DrawScene(dc)     
        self.Refresh()

    def DrawScene(self, dc):            
        # clear the scene
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear() 
        # draw objects and grid and so on...
        if(self.drawGrid and self.zoom >= 1):
            self.DrawGrid(dc)
        self.DrawObjects(dc)  
        if(self.display_rays):
            self.DrawRays(dc)
        
    def DrawGrid(self, dc):
        dc.SetPen(wx.Pen("Blue", 1))
        dw, dh = dc.GetSize()        
        ox = int(floor((-self.origin_x % self.gridStepSize) * self.zoom))
        oy = int(floor((-self.origin_y % self.gridStepSize) * self.zoom))
        orgx = int(floor(-self.origin_x * self.zoom))
        orgy = int(floor(-self.origin_y * self.zoom))
        step = int(floor(self.gridStepSize * self.zoom))
        # draw coordinate system
        dc.DrawLine(orgx, orgy, orgx + 2 * step, orgy)
        dc.DrawLine(orgx + 2 * step, orgy, int(round(orgx + 1.5 * step)), int(round(orgy + 0.5 * step)))
        dc.DrawLine(orgx + 2 * step, orgy, int(round(orgx + 1.5 * step)), int(round(orgy - 0.5 * step)))
        dc.DrawLine(int(round(orgx + 2.5 * step)), int(round(orgy - 0.5 * step)), int(round(orgx + 3 * step + 1)), int(round(orgy + 0.5 * step + 1)))
        dc.DrawLine(int(round(orgx + 2.5 * step)), int(round(orgy + 0.5 * step)), int(round(orgx + 3 * step + 1)), int(round(orgy - 0.5 * step + 1)))

        dc.DrawLine(orgx, orgy, orgx, orgy + 2 * step)
        dc.DrawLine(orgx, orgy + 2 * step, int(round(orgx + 0.5 * step)), int(round(orgy + 1.5 * step)))
        dc.DrawLine(orgx, orgy + 2 * step, int(round(orgx - 0.5 * step)), int(round(orgy + 1.5 * step)))
        dc.DrawLine(int(round(orgx - 0.25 * step)), int(round(orgy + 3 * step)), orgx + 1, int(round(orgy + 3.5 * step + 1)))
        dc.DrawLine(int(round(orgx + 0.25 * step)), orgy + 3 * step, int(round(orgx - 0.25 * step + 1)), orgy + 4 * step + 1)
        dc.DrawCircle(orgx, orgy, int(round(0.5 * step)))
        # draw grid points
        for x in range(ox, dw, step):
            for y in range(oy, dh, step):
                dc.DrawPoint(x, y)
    
    def DrawObjects(self, dc):
        for obj in self.objects:
            obj.Draw(dc, self.zoom, self.origin_x, self.origin_y)
            
    def DrawRays(self, dc):
        for r in self.rays:
            r.Draw(dc, self.zoom, self.origin_x, self.origin_y)
            
    # rendering functions
    def OnRender(self, event = None):
        if(event != None):
            event.Skip()
        # check for light source and get list of initial rays
        self.rays = []
        for op in self.objects:
            if op.lightsource:
                print("found lightsource...")
                self.rays = self.rays + op.GetLight()

        if len(self.rays) == 0:
            wx.MessageBox("No light source provided! There has to be at least one!", "Rendering...", wx.OK)
            return
        else:
            print("start with", len(self.rays), "light rays")
        
        count = 0
        # start rendering
        thingsToDo = 1                       
        while(thingsToDo and count < self.maxNumberOfIterations):
            count = count + 1
            print("Round:", count)
            print("Process", len(self.rays), "rays...")
            thingsToDo = 0                        
            newRays = []
            d0 = 0         
            # for each ray propagate through the scene
            for r in self.rays:
                objId = -1                
                if not r.processed:
                    l = r.getCurLine()                           
                    r.processed = 1                    
                    if(l != None):                        
                        # now calculate intersection with each object and take the closest intersection point
                        for i in range(len(self.objects)):                        
                            p, d, nr = self.objects[i].Intersection(l)                   
                            # the minimal distance has to be larger than 0 due to numerical errors!     
                            if p != None and d > 1e-7 and l.isLambdaPositiveForPoint(p):                                      
                                if(objId == -1 or d0 > d):
                                    objId = i
                                    r.p1 = deepcopy(p)
                                    nr0 = deepcopy(nr)
                                    d0 = d
                                    
                        if(objId != -1):    # i found an intersection
                            thingsToDo = 1                            
                            # add new rays to newRays                    
                            for nr in nr0:
                                print("add:", nr)
                                newRays.append(fromLine(nr))
            self.rays = self.rays + newRays

        self.display_rays = 1
        self.InitBuffer()