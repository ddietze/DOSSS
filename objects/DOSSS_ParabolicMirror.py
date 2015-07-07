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

class DOSSS_ParabolicMirror(DOSSSObject):
    def __init__(self, xpos = 0, ypos = 0, aperture = 50, focallength = 100):
        DOSSSObject.__init__(self, xpos, ypos)
        self.aperture = aperture    # diameter
        self.focallength = focallength  # focallength
        self.name = "Parabolic Mirror"
        
    def y(self, x):
        # flip the y value as our coordinate system counts y positive in downwards direction
        return -((x - self.focallength)**2 / (2 * self.focallength) - self.focallength/2)

    # create object shape for displaying
    def GetDisplayPoints(self):                
        p = []
        p.append([-self.aperture/2, self.y(-self.aperture/2)])
        p.append([-self.aperture/2, self.y(self.aperture/2) + 10])
        p.append([self.aperture/2, self.y(self.aperture/2) + 10])
        
        a = self.aperture / 2
        for i in range(10):            
            p.append([a, self.y(a)])            
            a = a - self.aperture / 10.0
        
        return p

    # intersection functions
    def Intersection(self, line):  
        # transform ray into object coordinate system
        l = self.ProjectIntoObjectCosy(line)        
       
        # now test for intersection
        # this is done by checking every segment of the object for intersection
        # if a point is found, it is stored together with the distance to the rays origin
        # and a list of emerging rays (transmitted or reflected)
        # at the end, the point with the shortest distance is picked and returned
        tl = DOSSSVector(-self.aperture/2, self.y(-self.aperture/2))
        bl = DOSSSVector(-self.aperture/2, self.y(self.aperture/2) + 10)
        br = DOSSSVector(self.aperture/2, self.y(self.aperture/2) + 10)
        tr = DOSSSVector(self.aperture/2, self.y(self.aperture/2))
        
        # return values
        p0 = None
        d0 = d = -1
        er = []
        
        # first the absorbing sides of the mirror
        # left side
        lb = getLineThroughPoints(tl, bl)
        p = lb.bounded_intersection(l, tl, bl)
        if(p != None):                      
            d = (l.a - p).length()           
            if(d > 1e-7 and (d0 == -1 or d < d0)): 
                d0 = d
                p0 = p                           
                er = [] #DOSSSLine(p0, Snell(l.u, DOSSSVector(0, -1), self.refractiveIndex))]

        # lower side
        lb = getLineThroughPoints(br, bl)
        p = lb.bounded_intersection(l, br, bl)
        if(p != None):                
            d = (l.a - p).length()           
            if(d > 1e-7 and (d0 == -1 or d < d0)): 
                d0 = d
                p0 = p                              
                er = [] #DOSSSLine(p0, Snell(l.u, DOSSSVector(0, 1), self.refractiveIndex))]
    
        # right side
        lb = getLineThroughPoints(br, tr)
        p = lb.bounded_intersection(l, br, tr)
        if(p != None):                     
            d = (l.a - p).length()            
            if(d > 1e-7 and (d0 == -1 or d < d0)):      
                d0 = d
                p0 = p                
                er = [] #DOSSSLine(p0, Snell(l.u, DOSSSVector(-1, 0), self.refractiveIndex))]
        
        # mirror 
        ps = IntersectionWithParabola(l, self.focallength)
        for p in ps:
            print "found intersection", p
            if(p != None and abs(p.x()) <= self.aperture / 2):             
                d = (l.a - p).length()
                if(d > 1e-7 and (d0 == -1 or d < d0)):                
                    d0 = d
                    p0 = p                                    
                    er = [DOSSSLine(p0, Snell(l.u, DOSSSVector((self.focallength - p0.x())/self.focallength, -1), 0))]
                    
        # now that we have the intersection point, we have to transform it back
        if(p0 != None):
            p0 = self.ProjectIntoObjectCosy(p0, 1)
            # do the same for all emerging beams
            for i in range(len(er)):
                er[i] = self.ProjectIntoObjectCosy(er[i], 1)                
        
        # return values are: [intersection point, distance of travel, [emerging rays]]
        return [p0, d0, er]

    # property dialog
    def ShowPropertyDialog(self):
        # create options list
        options = []
        options.append(["Position X", self.position[0]])
        options.append(["Position Y", self.position[1]])
        options.append(["Rotate", self.alpha])
        options.append(["FlipH", self.flip_h])
        options.append(["FlipV", self.flip_v])
        # object specific properties
        options.append(["Aperture", self.aperture, 1])
        options.append(["Focallength", self.focallength, 1])
        
        # open dialog
        dlg = DOSSS_PropertyDialog(options)
        if (dlg.ShowModal() == wx.ID_OK):
            # read out new values
            options = dlg.getOptions()
            self.position[0] = options[0]
            self.position[1] = options[1]
            self.alpha = options[2]
            self.flip_h = options[3]
            self.flip_v = options[4]
            # object specific properties
            self.aperture = options[5]
            self.focallength = options[6]            
            
        # destroy dialog object
        dlg.Destroy()        