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

class DOSSS_Box(DOSSSObject):
    def __init__(self, xpos = 0, ypos = 0, width = 10, height = 10):
        DOSSSObject.__init__(self, xpos, ypos)
        self.width = width
        self.height = height        
        self.name = "Box"
        self.CalculateBoundingBox()

    # these functions are thought for the displayed version only
    def getPoints(self, zoom = 1, ox = 0, oy = 0):
        # create
        self.points = []
        self.points.append(DOSSSVector(0, 0))
        self.points.append(DOSSSVector(self.width, 0))
        self.points.append(DOSSSVector(self.width, self.height))
        self.points.append(DOSSSVector(0, self.height))
        # rotate
        for i in range(4):
            self.points[i] = self.points[i].rotate(self.alpha)
        # translate
        t = DOSSSVector(self.position[0], self.position[1])
        for i in range(4):
            self.points[i] = self.points[i] + t             

        # make projection into labspace
        O = DOSSSVector(ox, oy)
        for i in range(4):
            self.points[i] = (self.points[i] - O) * zoom

    def CalculateBoundingBox(self):
        self.getPoints()
        minx = maxx = self.points[0].x()
        miny = maxy = self.points[0].y()
        for i in range(1,4):
            if(minx > self.points[i].x()):
                minx = self.points[i].x()
            if(miny > self.points[i].y()):
                miny = self.points[i].y()
            if(maxx < self.points[i].x()):
                maxx = self.points[i].x()
            if(maxy < self.points[i].y()):
                maxy = self.points[i].y()
        self.bbox = [minx, miny, maxx, maxy]

    def Draw(self, dc, zoom, x0, y0):
        self.getPoints(zoom, x0, y0)
        DOSSSObject.Draw(self, dc, zoom, x0, y0)
        if self.active:
            dc.SetPen(wx.Pen("Red", 2))
        else:
            dc.SetPen(wx.Pen("Blue", 2))
        for i in range(3):
            dc.DrawLine(self.points[i].x(), self.points[i].y(), self.points[i+1].x(), self.points[i+1].y())
        dc.DrawLine(self.points[-1].x(), self.points[-1].y(), self.points[0].x(), self.points[0].y())            
        
    # intersection functions
    def Intersection(self, l):
        line = deepcopy(l)
        # transform ray into object coordinate system
        # 1. translate        
        O = DOSSSVector(self.position[0], self.position[1])
        line.a = line.a - O
        # 2. rotate by -alpha
        line = line.rotate(-self.alpha)
        
        # now test for intersection
        tl = DOSSSVector(0, 0)
        bl = DOSSSVector(0, self.height)
        tr = DOSSSVector(self.width, 0)
        br = DOSSSVector(self.width, self.height)
        
        p0 = None
        d0 = d = -1
        er = []
        
        # side 1
        lb = getLineThroughPoints(tl, tr)
        p = lb.bounded_intersection(line, tl, tr)
        if(p != None):            
            d = (line.a - p).length()
            if(d0 == -1 or d < d0):
                d0 = d
                p0 = p
                er = [DOSSSLine(p0, DOSSSVector(line.u.x(), -line.u.y()))]
        
        # side 2
        lb = getLineThroughPoints(tr, br)
        p = lb.bounded_intersection(line, tr, br)
        if(p != None):            
            d = (line.a - p).length()
            if(d0 == -1 or d < d0):
                d0 = d
                p0 = p
                er = [DOSSSLine(p0, DOSSSVector(-line.u.x(), line.u.y()))]
        
        # side 3
        lb = getLineThroughPoints(br, bl)
        p = lb.bounded_intersection(line, br, bl)
        if(p != None):            
            d = (line.a - p).length()
            if(d0 == -1 or d < d0):
                d0 = d
                p0 = p
                er = [DOSSSLine(p0, DOSSSVector(line.u.x(), -line.u.y()))]
        
        # side 4
        lb = getLineThroughPoints(bl, tl)
        p = lb.bounded_intersection(line, bl, tl)
        if(p != None):            
            d = (line.a - p).length()
            if(d0 == -1 or d < d0):
                d0 = d
                p0 = p
                er = [DOSSSLine(p0, DOSSSVector(-line.u.x(), line.u.y()))]
        
        # now that we have the intersection point, we have to transform it back
        if(p0 != None):
            # 1. rotate
            p0 = p0.rotate(self.alpha)            
            # 2. translate            
            p0 = p0 + O
            # do the same for all emerging beams
            for i in range(len(er)):
                er[i] = er[i].rotate(self.alpha)
                er[i].a = er[i].a + O
        
        # return values are: [intersection point, distance of travel, [emerging rays]]
        return [p0, d0, er]

    # property dialog
    def ShowPropertyDialog(self):
        # create options list
        options = []
        options.append(["Position X", self.position[0]])
        options.append(["Position Y", self.position[1]])
        options.append(["Width", self.width])
        options.append(["Height", self.height])
        options.append(["Rotate", self.alpha])
        
        # open dialog
        dlg = DOSSS_PropertyDialog(options)
        if (dlg.ShowModal() == wx.ID_OK):
            # read out new values
            options = dlg.getOptions()
            self.position[0] = options[0]
            self.position[1] = options[1]
            self.width = options[2]
            self.height = options[3]
            self.alpha = options[4]
            
            # important! calculate new bounding box
            self.CalculateBoundingBox()
        
        # destroy dialog object
        dlg.Destroy()