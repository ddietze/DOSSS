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
from core.opsim_lightray import *    # this applies for light sources only

class DOSSS_PointLight(DOSSSObject):
    def __init__(self, xpos = 0, ypos = 0, divangle = 30, norays = 5):
        DOSSSObject.__init__(self, xpos, ypos)
        self.color = "Blue"
        self.fullDivAngle = divangle        
        self.noRays = norays
        if self.fullDivAngle > 360:
            self.fullDivAngle = 360
        if self.fullDivAngle < 1:
            self.fullDivAngle = 1
        if self.noRays < 3:
            self.noRays = 3
        self.lightsource = 1 
        self.name = "Point Light"
      
    def GetDisplayPoints(self):
        # this schould return a list of wx.Point objects which contain the coordinates
        # of the points to display
        # they are then mirrored, rotated and translated according to the object properties
        # and finally projected onto the screen
        p = []
        # center spot
        p.append([0, 0])
        # for each ray create a segment of a circle
        dalpha = (float(self.fullDivAngle) / float(self.noRays - 1)) * pi / 180.0
        alpha0 = (-float(self.fullDivAngle) / 2.0) * pi / 180.0
        for i in range(int(self.noRays)):
            a = alpha0 + float(i) * dalpha
            x = sin(a) * 20
            y = -cos(a) * 20
            p.append([x, y])            
        return p
    
    def Intersection(self, line):
        # a light source does not interact with rays
        return [None, 0, []]
    
    # property dialog
    def ShowPropertyDialog(self):
        options = []
        options.append(["Position X", self.position[0]])
        options.append(["Position Y", self.position[1]])
        options.append(["Rotate", self.alpha])
        options.append(["FlipH", self.flip_h])
        options.append(["FlipV", self.flip_v])
        # object specific properties
        options.append(["Full Div. Angle", self.fullDivAngle, 1, 360])
        options.append(["# of Rays", self.noRays, 3])
        
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
            self.fullDivAngle = options[5]     
            self.noRays = options[6]
           
        dlg.Destroy()
        
    # this function applies only for light sources
    # returns a list of DOSSS_LightRay - objects
    # for an object to be a light source, the 'lightsource' flag has to be set
    def GetLight(self):      
        rays = []
        av = DOSSSVector(0, 0)   
        av = self.project(av, 0, 1)     
        
        dalpha = float(self.fullDivAngle) / (self.noRays - 1)
        alpha0 = -1.0 * float(self.fullDivAngle) / 2.0
        
        for i in range(int(self.noRays)):
            a = alpha0 + float(i) * dalpha
            print(a)
            a = a * pi / 180.0
            x = sin(a)
            y = -cos(a)
            uv = DOSSSVector(x, y)
            uv = self.project(uv, 1, 1)

            rays.append(DOSSS_LightRay(av.x(), av.y(), uv.x(), uv.y()))
            
        return rays