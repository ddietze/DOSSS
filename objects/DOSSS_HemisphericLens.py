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

class DOSSS_HemisphericLens(DOSSSObject):
    def __init__(self, xpos = 0, ypos = 0, radius = 10, height = 15, ior = 1.5):
        DOSSSObject.__init__(self, xpos, ypos)       
        self.radius = radius
        self.height = height
        self.refractiveIndex = ior  # material ior        
        self.name = "Hemispheric Lens"
        
    # check for minimal thickness such that the lens has at least the given aperture
    def CheckParameters(self):        
        if self.height > 2 * self.radius:
            self.height = 2 * self.radius

    # create object shape for displaying
    def GetDisplayPoints(self):
        p = []
        for i in range(21):
            y = float(i-10)/10 * self.height/2 - (2 * self.radius - self.height)/2
            x = sqrt(self.radius**2 - y**2)
            p.append([x, y])        
        for i in range(21):
            y = float(10-i)/10 * self.height/2 - (2 * self.radius - self.height)/2
            x = -sqrt(self.radius**2 - y**2)
            p.append([x, y])
        p.append([0, -self.radius])
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
        x = sqrt(2 * self.height * self.radius - self.height**2)      
        y = self.height - self.radius
        bl = DOSSSVector(-x, y)
        br = DOSSSVector(+x, y)
        
        # return values
        p0 = None
        d0 = d = -1
        er = []
        
        # lower side
        if bl.x() != br.x():
            lb = getLineThroughPoints(bl, br)
            p = lb.bounded_intersection(l, bl, br)
            if(p != None):                      
                d = (l.a - p).length()           
                if(d > 1e-7 and (d0 == -1 or d < d0)): 
                    d0 = d
                    p0 = p                           
                    er = [DOSSSLine(p0, Snell(l.u, DOSSSVector(0, 1), self.refractiveIndex))]
 
        # spherical side
        ps = IntersectionWithSphere(l, 0, self.radius)
        for p in ps:
            if(p != None and p.y() < y):
                d = (l.a - p).length()
                if(d > 1e-7 and (d0 == -1 or d < d0)):                
                    d0 = d
                    p0 = p                
                    # the normal vector on the sphere is given by the vector through the intersection and the center of the sphere
                    er = [DOSSSLine(p0, Snell(l.u, DOSSSVector(p.x(), p.y()), self.refractiveIndex))]
                    
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
        options.append(["Radius", self.radius, 1])
        options.append(["Height", self.height, 1])
        options.append(["Refractive Index", self.refractiveIndex, 1])        
        
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
            self.radius = options[5]
            self.height = options[6]
            self.refractiveIndex = options[7]             
            self.CheckParameters()
        
        # destroy dialog object
        dlg.Destroy()
        