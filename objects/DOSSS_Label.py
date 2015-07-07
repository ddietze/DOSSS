"""
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

   Copyright 2015 Daniel Dietze <daniel.dietze@berkeley.edu>.   
""" 
import wx
from core.opsim_objectbase import *

class DOSSS_Label(DOSSSObject):
    def __init__(self, xpos = 0, ypos = 0, label = "Label"):  
        DOSSSObject.__init__(self, xpos, ypos)      
        self.color = "Grey"
        self.text = label                
        self.name = "Label"
    
    ##############################
    ## these functions have to be overwritten by any new object
    def Draw(self, dc, zoom, x0, y0):
        labelFont = wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL)
        dc.SetFont(labelFont)
        dc.SetTextForeground(self.color)
        self.width, self.height = dc.GetTextExtent(self.text)
        self.width = self.width / zoom
        self.height = self.height / zoom        
        
        # call base-function
        DOSSSObject.Draw(self, dc, zoom, x0, y0)    
        dc.DrawRotatedText(self.text, (self.position[0] + 2 - x0) * zoom, (self.position[1] + 2 - y0) * zoom, -self.alpha)
    
    def svgstr(self):
        svg = "<g style=\"stroke-width:0.1mm; stroke:blue; fill:white; fill-opacity:1.0;\">\n";
      
        svg += "<text x=\"%d\" y=\"%d\" font-size=\"10\" rotate=\"%d\">\n" % (self.position[0], self.position[1] + 10, -self.alpha);
        svg += "   %s\n" % (self.text)
        svg += "</text>\n"
       
        svg += "</g>\n"
        
        return svg
	
    def GetDisplayPoints(self):
        # this schould return a list of wx.Point objects which contain the coordinates
        # of the points to display
        # they are then mirrored, rotated and translated according to the object properties
        # and finally projected onto the screen
        p = []
        p.append([0, 0])
        p.append([self.width + 4, 0])
        p.append([self.width + 4, self.height + 4])
        p.append([0, self.height + 4])
        return p        
    
    def Intersection(self, line):
        # labels do not interfere
        return [None, 0, []]
    
    # property dialog
    def ShowPropertyDialog(self):
        options = []
        options.append(["Position X", self.position[0]])
        options.append(["Position Y", self.position[1]])
        options.append(["Rotate", self.alpha])
        options.append(["FlipH", self.flip_h])
        options.append(["FlipV", self.flip_v])
        options.append(["Text", self.text, "str"])
        dlg = DOSSS_PropertyDialog(options)
        if (dlg.ShowModal() == wx.ID_OK):
            options = dlg.getOptions() 
            self.position[0] = options[0]
            self.position[1] = options[1]
            self.alpha = options[2]
            self.flip_h = options[3]
            self.flip_v = options[4]
            self.text = options[5]           
            
        dlg.Destroy()        
    