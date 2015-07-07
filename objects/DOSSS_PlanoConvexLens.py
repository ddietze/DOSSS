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

class DOSSS_PlanoConvexLens(DOSSSObject):
    def __init__(self, xpos = 0, ypos = 0, aperture = 50, focallength = 100, ior = 1.5, thickness = 10):
        DOSSSObject.__init__(self, xpos, ypos)
        self.aperture = aperture    # diameter
        self.focallength = focallength  # focallength
        self.thickness = thickness  # maximal thickness
        self.refractiveIndex = ior  # material ior
        self.CheckThickness()
        self.name = "Plano-Convex Lens"
        
    # check for minimal thickness such that the lens has at least the given aperture
    def CheckThickness(self):        
        # take R as positive as I know, that we have a convex lens
        R = (self.refractiveIndex - 1) * self.focallength 
        if self.aperture > 2 * R:
            self.aperture = 2 * R
        dmin = R - sqrt(4 * R**2 - self.aperture**2) / 2.0
        if self.thickness < dmin:
            self.thickness = dmin

    # create object shape for displaying
    def GetDisplayPoints(self):
        R = (self.refractiveIndex - 1) * self.focallength 
        dmin = R - sqrt(4 * R * R - self.aperture * self.aperture) / 2.0
        
        p = []
        p.append([0, -self.aperture / 2])

        a = self.aperture / 2
        for i in range(11):
            d = R - sqrt(R**2 - a**2)
            p.append([self.thickness - d, -a])
            a = a - self.aperture / 10.0                    
        
        p.append([0, +self.aperture / 2])        
        
        return p

    # intersection functions
    def Intersection(self, line):  
        # transform ray into object coordinate system
        l = self.ProjectIntoObjectCosy(line) 
        
        # lens parameters
        R = (self.refractiveIndex - 1) * self.focallength   # radius of circular part
        dmin = R - sqrt(4 * R * R - self.aperture * self.aperture) / 2.0 # intersection of circular part with linear part 
        
        # now test for intersection
        # this is done by checking every segment of the object for intersection
        # if a point is found, it is stored together with the distance to the rays origin
        # and a list of emerging rays (transmitted or reflected)
        # at the end, the point with the shortest distance is picked and returned
        tl = DOSSSVector(0, -self.aperture/2)
        tr = DOSSSVector(self.thickness - dmin, -self.aperture/2)
        br = DOSSSVector(self.thickness - dmin, +self.aperture/2)
        bl = DOSSSVector(0, +self.aperture/2)
        
        # return values
        p0 = None
        d0 = d = -1
        er = []
        
        # upper side
        if tr.x() != tl.x():
            lb = getLineThroughPoints(tl, tr)
            p = lb.bounded_intersection(l, tl, tr)
            if(p != None):                      
                d = (l.a - p).length()           
                if(d > 1e-7 and (d0 == -1 or d < d0)): 
                    d0 = d
                    p0 = p                           
                    er = [DOSSSLine(p0, Snell(l.u, DOSSSVector(0, -1), self.refractiveIndex))]
 
        # lower side
        if br.x() != bl.x():
            lb = getLineThroughPoints(br, bl)
            p = lb.bounded_intersection(l, br, bl)
            if(p != None):                
                d = (l.a - p).length()           
                if(d > 1e-7 and (d0 == -1 or d < d0)): 
                    d0 = d
                    p0 = p                              
                    er = [DOSSSLine(p0, Snell(l.u, DOSSSVector(0, 1), self.refractiveIndex))]
        
        # right side
        lb = getLineThroughPoints(bl, tl)
        p = lb.bounded_intersection(l, bl, tl)
        if(p != None):                     
            d = (l.a - p).length()            
            if(d > 1e-7 and (d0 == -1 or d < d0)):      
                d0 = d
                p0 = p                
                er = [DOSSSLine(p0, Snell(l.u, DOSSSVector(-1, 0), self.refractiveIndex))]
        
        # spherical side
        ps = IntersectionWithSphere(l, self.thickness - R, R)
        for p in ps:
            if(p != None and p.x() >= self.thickness - R and abs(p.y()) <= self.aperture/2):
                d = (l.a - p).length()
                if(d > 1e-7 and (d0 == -1 or d < d0)):                
                    d0 = d
                    p0 = p                
                    # the normal vector on the sphere is given by the vector through the intersection and the center of the sphere
                    er = [DOSSSLine(p0, Snell(l.u, DOSSSVector(p.x() - self.thickness + R, p.y()), self.refractiveIndex))]
                    
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
        options.append(["Focal Length", self.focallength, 1])
        options.append(["Refractive Index", self.refractiveIndex, 1])
        options.append(["Thickness", self.thickness, 1])
        
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
            self.refractiveIndex = options[7] 
            self.thickness = options[8] 
            self.CheckThickness()
        
        # destroy dialog object
        dlg.Destroy()
