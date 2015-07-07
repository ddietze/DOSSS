"""
.. module: opsim.opsim_lightray
   :platform: Windows
.. moduleauthor:: Daniel Dietze <daniel.dietze@berkeley.edu>

Definitions / declarations for light rays for use in DOSSS.

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
from core.opsim_geo import *

class DOSSS_LightRay:
    """A light ray class used for raytracing in DOSSS.
    All coordinates are given in laboratory system.
    
    :param float posx: x-coordinate of the base point.
    :param float posy: y-coordinate of the base point.
    :param float ux: x-component of the direction vector.
    :param float uy: y-component of the direction vector.
    """
    def __init__(self, posx = 0, posy = 0, ux = 1, uy = 0):
        self.p0 = DOSSSVector(posx, posy)   # these work in the lab system
        self.p1 = None
        self.processed = 0
        self.u = DOSSSVector(ux, uy)              
    
    def ContinueRay(self, dc, px, py, ux, uy):    # in client system       
        """Calculate the continuation of the light ray beyond the last intersecting object for proper display on screen.
        
        All coordinates are given in DC client system, i.e. range from 0 to size of screen in px.
        
        :param wx.DC dc: Paint DC.
        :param float px: x-coordinate of the base point.
        :param float py: y-coordinate of the base point.
        :param float ux: x-component of the direction vector.
        :param float uy: y-component of the direction vector.
        :returns: Lambda value of intersection with screen boundary (float).
        """
        # get size of client area
        size = dc.GetSize()   
        # create line object
        p = DOSSSVector(px, py)
        l = DOSSSLine(p, DOSSSVector(ux, uy))
        
        # get intersection with screen
        d0 = 1e10
        myp = None
        l1 = l.intersect(DOSSSLine(DOSSSVector(0, 0), DOSSSVector(1, 0)))        
        if(l1 != None and l.isLambdaPositiveForPoint(l1)):
            myp = l1
            d0 = (l1 - p).length()
        l2 = l.intersect(DOSSSLine(DOSSSVector(0, 0), DOSSSVector(0, 1)))
        if(l2 != None and ((l2 - p).length() < d0) and l.isLambdaPositiveForPoint(l2)):
            myp = l2
            d0 = (l2 - p).length()
        l3 = l.intersect(DOSSSLine(DOSSSVector(size[0], size[1]), DOSSSVector(1, 0)))
        if(l3 != None and ((l3 - p).length() < d0) and l.isLambdaPositiveForPoint(l3)):
            myp = l3
            d0 = (l3 - p).length()
        l4 = l.intersect(DOSSSLine(DOSSSVector(size[0], size[1]), DOSSSVector(0, 1)))
        if(l4 != None and ((l4 - p).length() < d0) and l.isLambdaPositiveForPoint(l4)):            
            myp = l4
            d0 = (l4 - p).length()
               
        return myp
    
    # draw light ray to screen    
    def Draw(self, dc, zoom, ox, oy):   # in client system
        """Draw the light ray to the DC client.
        
        :param wx.DC dc: Paint DC.
        :param float zoom: Zoom level, where 1 is no zoom.
        :param float ox: x-coordinate of origin of current view in laboratory frame.
        :param float oy: y-coordinate of origin of current view in laboratory frame.
        """
        # get size of client area
        ux, uy = dc.GetSize()   
        
        # set pen
        dc.SetPen(wx.Pen("Red", 1))
        
        # create list of points
        p = []
        p.append(wx.Point((self.p0.x() - ox) * zoom, (self.p0.y() - oy) * zoom))
        if(self.p1 != None):
            p.append(wx.Point((self.p1.x() - ox) * zoom, (self.p1.y() - oy) * zoom))
        else:            
            if not self.u.isNull():
                p1 = self.ContinueRay(dc, (self.p0.x() - ox) * zoom, (self.p0.y() - oy) * zoom, self.u.x(), self.u.y())                
                if p1 != None:
                    p.append(wx.Point(p1.x(), p1.y()))       
        dc.DrawLines(p)
    
    def svgstr(self):		# returns a string in SVG format for exporting to vector format
        """Returns a string in SVG format for exporting to vector format.
        """
        if(self.p1 == None):
            self.p1 = self.p0 + self.u * 500.0 	# make a 50cm long ray
        
        svg = "<g style=\"stroke-width:0.1mm; stroke:red;\">\n";
        svg += " <line x1=\"%f\" y1=\"%f\" x2=\"%f\" y2=\"%f\" />\n" % (self.p0.x(),self.p0.y(), self.p1.x(), self.p1.y())
        svg += "</g>\n"
        
        return svg

    # returns DOSSSLine object for current part of the beam
    def getCurLine(self):   # in lab system
        """Returns DOSSSLine object for current part of the beam.
        """
        if self.u.isNull():
            return None
        if self.p1 != None:
            return None
        return DOSSSLine(self.p0, self.u)
    
# convert a DOSSSLine object into a DOSSS_LightRay object
def fromLine(l):
    """Convert a DOSSSLine object into a DOSSS_LightRay object.
    """
    return DOSSS_LightRay(l.a.x(), l.a.y(), l.u.x(), l.u.y())