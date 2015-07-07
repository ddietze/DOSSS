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

class DOSSS_ParallelLight(DOSSSObject):
    def __init__(self, xpos = 0, ypos = 0, width = 10, norays = 5):
        DOSSSObject.__init__(self, xpos, ypos)
        self.color = "Blue"
        self.width = width
        self.noRays = norays        
        if self.noRays < 1:
            self.noRays = 1
        self.lightsource = 1 
        self.name = "Parallel Light"
      
    def GetDisplayPoints(self):
        # this schould return a list of wx.Point objects which contain the coordinates
        # of the points to display
        # they are then mirrored, rotated and translated according to the object properties
        # and finally projected onto the screen
        p = []        
        p.append([-self.width, -self.width / 2])
        p.append([self.width, -self.width / 2])
        p.append([self.width, self.width / 2])
        p.append([-self.width, self.width / 2])                   
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
        options.append(["Width", self.width, 1])
        options.append(["# of Rays", self.noRays, 1])
        
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
            self.width = options[5]     
            self.noRays = options[6]
           
        dlg.Destroy()
        
    # this function applies only for light sources
    # returns a list of DOSSS_LightRay - objects
    # for an object to be a light source, the 'lightsource' flag has to be set
    def GetLight(self):      
        rays = []
        if self.noRays > 1:
            a0 = -self.width / 2
            da = self.width / (float(self.noRays) - 1.0)
            print a0, da
        else:
            a0 = 0
            da = 0
        for i in range(int(self.noRays)):                                    
            av = DOSSSVector(0, a0)
            uv = DOSSSVector(1, 0)
            a0 = -self.width / 2 + (i + 1) * da
            # project vectors in LabSpace
            uv = self.project(uv, 1, 1)
            av = self.project(av, 0, 1)                
            rays.append(DOSSS_LightRay(av.x(), av.y(), uv.x(), uv.y()))
            
        return rays