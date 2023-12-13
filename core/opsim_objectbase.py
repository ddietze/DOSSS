"""
.. module: opsim.opsim_objectbase
   :platform: Windows
.. moduleauthor:: Daniel Dietze <daniel.dietze@berkeley.edu>

This is the base class of all DOSSS objects.

In order to extend DOSSS by adding new objects, create a new class derived from :py:class:`DOSSSObject` and overwrite the following four interface functions:

    * :py:func:`~core.opsim_objectbase.DOSSSObject.GetDisplayPoints`: 
        Returns a list of points for drawing the object into the ClientDC.

    * :py:func:`~core.opsim_objectbase.DOSSSObject.Intersection`: 
        Returns some information about the intersection with a light ray: intersection point, distance of travel, emerging rays.

    * :py:func:`~core.opsim_objectbase.DOSSSObject.ShowPropertyDialog`:
        Show the property dialog box for the object.
        
    * :py:func:`~core.opsim_objectbase.DOSSSObject.GetLight`:
        Returns a list of light rays if the object is a light source.

In addition, you have to provide a unique name / identifier for the object in the :py:attr:`~core.opsim_objectbase.DOSSSObject.name` class attribute, which will then be used in the objects menu.
        
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
from copy import deepcopy
from core.opsim_geo import *
from core.opsim_property_dialog import *
from core.opsim_lightray import *

class DOSSSObject:
    """DOSSS object base class. All objects have to be derived from this class.

    :param float xpos: x-coordinate of object center in laboratory frame.
    :param float ypos: y-coordinate of object center in laboratory frame.
    """
    def __init__(self, xpos = 0, ypos = 0):
        self.position = [xpos, ypos]    # translation
        self.alpha = 0                  # rotation
        self.flip_h = 0                 # horizontal mirroring
        self.flip_v = 0                 # vertical mirroring
        
        self.bbox = [0, 0, 0, 0]
        self.active = 0
        self.color = "Black"    #: default color for drawing the object to the screen
        self.lightsource = 0    #: set this to one/True if you want to create a light source
    
        self.name = "Object"    #: overwrite this string for each new object and give it a unique identifier
    
    def get_name(self):
        """Returns the name / category of the object. This string is used to build the object menu items.
        """
        return self.name
    
    # general functions
    def set_position(self, x, y):             
        """Set new position (x, y) in laboratory frame.
        """
        self.position = [x, y]           
        
    def get_position(self):
        """Returns current position (x,y).
        """
        return self.position
    
    # ##########
    # display functions
    def CalculateBoundingBox(self, points):
        """Calculates the bounding box around a set of points.
        
        :param list points: List of object points like corners, etc.
        :returns: Bounding box [minx, miny, maxx, maxy] containing all points.
        """
        minx = maxx = points[0].x
        miny = maxy = points[0].y
        for p in points:
            if(minx > p.x):
                minx = p.x
            if(miny > p.y):
                miny = p.y
            if(maxx < p.x):
                maxx = p.x
            if(maxy < p.y):
                maxy = p.y
        self.bbox = [minx, miny, maxx, maxy]
        
    def get_bbox(self):
        """Returns the bounding box.
        """
        return self.bbox
    
    def ProjectDisplayPoints(self, points, ox, oy, zoom):
        """Apply rotation, mirror and translation operations to set of points and return coordinates in client system.
        
        :param list points: List of points.
        :param float ox: x-coordinate of origin of current view in laboratory frame.
        :param float oy: y-coordinate of origin of current view in laboratory frame.
        :param float zoom: Zoom level (1 is no zoom).
        :returns: List of points in client system.
        """
        newp = []
        for p in points:
            # 1. mirror
            if self.flip_h:
                p[0] = -p[0]
            if self.flip_v:
                p[1] = -p[1]
            # 2. rotate
            a = self.alpha * pi / 180.0
            x = cos(a) * p[0]  - sin(a) * p[1]
            y = sin(a) * p[0]  + cos(a) * p[1]
            p[0] = x
            p[1] = y
            # 3. translate
            p[0] = p[0] + self.position[0]
            p[1] = p[1] + self.position[1]
            # add screen origin and scale according to zoom level
            p[0] = (p[0] - ox) * zoom
            p[1] = (p[1] - oy) * zoom
            # append
            newp.append(wx.Point(int(p[0]), int(p[1])))
        
        return newp
        
    def Draw(self, dc, zoom, x0, y0):
        """Draw the object to the client DC.
        
        :param wx.DC dc: Paint DC.
        :param float zoom: Zoom level (1 is no zoom).
        :param float x0: x-coordinate of origin of current view in laboratory frame.
        :param float y0: y-coordinate of origin of current view in laboratory frame.
        """
        # points
        if self.active:
            dc.SetPen(wx.Pen("Red", 2))
        else:
            dc.SetPen(wx.Pen(self.color, 1))        
        dc.SetBrush(wx.Brush("White"))
        p = self.GetDisplayPoints()
        p = self.ProjectDisplayPoints(p, x0, y0, zoom)
        dc.DrawPolygon(p)
        # origin cross
        dc.SetPen(wx.Pen("Green", 1))
        ox = int(round((self.position[0] - x0) * zoom))
        oy = int(round((self.position[1] - y0) * zoom))
        of = 4 * zoom
        dc.DrawLine(ox-of, oy, ox+of, oy)
        dc.DrawLine(ox, oy-of, ox, oy+of)
        # get new bounding box
        self.CalculateBoundingBox(p) 
    
    def svgstr(self): 
        """Returns a string in SVG format for exporting to vector format.
        """
        svg = "<g style=\"stroke-width:0.3mm; stroke:black; fill:white; fill-opacity:1.0;\">\n";
      
        # get points
        p = self.GetDisplayPoints()
        p = self.ProjectDisplayPoints(p, 0, 0, 1)
        
        svg += " <polygon points=\""
        for point in p:
            svg += "%f,%f " % (point[0], point[1])
        svg += "\" />\n"
        svg += "</g>\n"
        
        return svg

    # ###########
    # intersection functions
    # project vector v back and forth
    def project(self, ve, isunit = False, back = False):
        """Apply transformations to a vector.
        
        :param DOSSSVector ve: Vector to be projected.
        :param bool isunit: If True, treat as direction vector, otherwise as coordinate vector (default).
        :param bool back: Direction of projection: True for screen-to-lab, False for lab-to-screen (default).
        :returns: Transformed version of the vector.
        """
        v = deepcopy(ve)
        O = DOSSSVector(self.position[0], self.position[1])
        if not back:                       
            # 1. translate        
            if not isunit:
                v = v - O
            
            # 2. rotate by -alpha
            v = v.rotate(-self.alpha)
            
            # 3. flip over
            if self.flip_h:
                v.setx(-v.x())                
            if self.flip_v:
                v.sety(-v.y())                
        else:   # or do the reverse transformation
            # 1. flip over
            if self.flip_h:
                v.setx(-v.x())                
            if self.flip_v:
                v.sety(-v.y())                
                
            # 2. rotate by alpha
            v = v.rotate(self.alpha)
            
            # 3. translate
            if not isunit:
                v = v + O
        return v
        
    def ProjectIntoObjectCosy(self, line, back = 0):
        """Project a line or vector into the object's coordinate system.
        This is done by applying the transformations from :py:func:`ProjectDisplayPoints` in reverse order and without the projection into the screen system. This is a convenience wrapper around :py:func:`project`.
        
        :param (DOSSSLine or DOSSSVector) line: Line or vector object to project.
        :param bool back: Forward (False, default) or backward (True) projection.
        :returns: Line or vector projected into object's coordinate system.
        """
        l = deepcopy(line)
        # decide whether its a line or a vector
        if l.type == "line":
            l.a = self.project(l.a, 0, back)
            l.u = self.project(l.u, 1, back)
        else:
            l = self.project(l, 0, back)
            
        return l

    ##############################
    ## these functions have to be overwritten by any new object
    
    def GetDisplayPoints(self):
        """Returns a list of *wx.Points* which contain the coordinates of the object's points/corners in the object's coordinate system for displaying on screen as polyline. These are subsequently mirrored, rotated and translated according to the object properties and finally projected onto the screen. These points are only for drawing the object and should be chosen such that the function of the object becomes evident.
        
        .. important:: This function needs to be overwritten by your object class.
        """
        return []
    
    def Intersection(self, line):
        """Test for intersection between a line and the current object. If there are several intersections, return the one closest to the light rays origin, i.e., with the smallest lambda value.
        
        .. important:: This function needs to be overwritten by your object class.
        
        :param DOSSSLine line: The light ray.
        :returns: - point of intersection, if any (DOSSSVector or None)
                  - distance from base to intersection (float)
                  - list of emerging rays, e.g., transmitted and/or reflected (list of DOSSSLine)
        """
        # transform ray into object coordinate system
        l = self.ProjectIntoObjectCosy(line)        
        # now test for intersection...
        # this is done by checking every segment of the object for intersection
        # if a point is found, it is stored together with the distance to the rays origin
        # and a list of emerging rays (transmitted or reflected)
        # at the end, the point with the shortest distance is picked and returned
        
        # l = self.ProjectIntoObjectCosy(line, 1)
        # return values are: [intersection point, distance of travel, [emerging rays]]
        return [None, 0, []]
    
    # property dialog
    def ShowPropertyDialog(self):
        """Show the property dialog box for the object, which allows the user to change the objects parameters.
        
        .. important:: This function needs to be overwritten by your object class.        
        """
        options = [["This object has no properties!"]]
        dlg = DOSSS_PropertyDialog(options)
        if (dlg.ShowModal() == wx.ID_OK):
            options = dlg.getOptions()            
        dlg.Destroy()
        
    def GetLight(self):
        """Returns a list of DOSSS_LightRay - objects emitted from the object. This function applies only for light sources and for an object to be a light source, the *lightsource* flag has to be set.
        
        .. important:: This function needs to be overwritten by your object class if it is a light source.
        """
        return []