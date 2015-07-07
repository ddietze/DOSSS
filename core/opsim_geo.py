"""
.. module: opsim.opsim_geo
   :platform: Windows
.. moduleauthor:: Daniel Dietze <daniel.dietze@berkeley.edu>

Definitions / declarations for geometrical objects and functions used in DOSSS.

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
from math import *
from numpy import *
from copy import deepcopy

class DOSSSVector:
    """A 2d vector class that supports basic arithmetic operations (+, -, `*`).

    :param float nx: x-component (optional).
    :param float ny: y-component (optional).
    """
    def __init__(self, nx = 0, ny = 0):
        self.data = array([nx,ny], dtype=float)        
        self.type = "vector"
    
    def x(self):
        """Returns x-component of vector. If absolute value is below 1e-10, it returns 0.
        """
        if abs(self.data[0]) < 1e-10:
            self.data[0] = 0
        return self.data[0]
    
    def y(self):
        """Returns y-component of vector. If absolute value is below 1e-10, it returns 0.
        """
        if abs(self.data[1]) < 1e-10:
            self.data[1] = 0
        return self.data[1]

    def setx(self, x):
        """Overwrite x-component of vector. 
        
        :param float x: New value for x-component.
        """        
        self.data[0] = x
        
    def sety(self, y):
        """Overwrite y-component of vector. 
        
        :param float y: New value for y-component.
        """
        self.data[1] = y
    
    def isNull(self):
        """Returns True if vector is identical to zero, False otherwise.
        """
        if(self.data[0] == 0 and self.data[1] == 0):
            return 1
        else:
            return 0

    def unit(self):        
        """Returns a unit vector with the same orientation.
        """
        nx = self.data[0] / self.length()
        ny = self.data[1] / self.length()
        return DOSSSVector(nx, ny)

    def __str__(self):
        return "(" + str(self.data[0]) + ", " + str(self.data[1]) + ")"
    
    def __add__(self, other):
        return DOSSSVector(self.data[0] + other.data[0], self.data[1] + other.data[1])

    def __sub__(self, other):
        return DOSSSVector(self.data[0] - other.data[0], self.data[1] - other.data[1])

    def __mul__(self, other):
        try:
            return DOSSSVector(self.data[0] * other, self.data[1] * other)
        except:
            return self.data[0] * other.data[0] + self.data[1] * other.data[1]

    def length(self):
        """Return length of vector.
        """
        return sqrt(self.data[0] * self.data[0] + self.data[1] * self.data[1])
    
    def __eq__(self, other):
        try:
            if(self.data[0] == other.data[0] and self.data[1] == other.data[1]):
                return 1
            else:
                return 0
        except:
            return 0
        
    def rotate(self, theta):
        """Rotate vector.
        
        :param float theta: Angle in degrees.
        :returns: Rotated vector.
        """
        alpha = theta * pi / 180.0
        return DOSSSVector(cos(alpha) * self.data[0] - sin(alpha) * self.data[1], sin(alpha) * self.data[0] + cos(alpha) * self.data[1])

class DOSSSLine:
    """Represents a line of the form P = a + lambda * u where u gives the direction of the line and a is the base of the line. Distances along the line are measured relative to this point. 

    :param DOSSSVector a: Base point of the line. If None, it defaults to (0,0).
    :param DOSSSVector u: Direction of the line. If None, it defaults to (1,0).
    """
    def __init__(self, a = None, u = None):
        if a is None:
            a = DOSSSVector(0, 0)
        if u is None:
            u = DOSSSVector(1, 0)
        self.a = deepcopy(a)
        self.u = u.unit()
        self.type = "line"
    
    def __str__(self):
        return str(self.a) + " + lambda * " + str(self.u)

    def get_point(self, l):
        """Return point for lambda value l.
        """
        return self.a + self.u * l

    # return true if p is part of this line
    def contains_point(self, p):
        """Returns True if point p is part of the line, False otherwise.
        """
        if (self.u.x() != 0.0):
            l = (p.x() - self.a.x()) / self.u.x()
        elif (self.u.y != 0.0):
            l = (p.y() - self.a.y()) / self.u.y()
        else:
            if(p == self.a):
                return True
            else:
                return False
        p2 = self.get_point(l)
        if (p == p2):
            return True
        else:
            return False

    # check whether p is in the positive halfspace or in the negative halfspace
    def isLambdaPositiveForPoint(self, p):
        """Return True if point p (DOSSSVector) is in the positive half space of the line, i.e. lambda is positive. Returns False otherwise.
        """
        cosphi = (p - self.a) * self.u
        if cosphi >= 0:
            return True
        else:
            return False

    # return intersection point of two lines, None if the lines are parallel or identical
    def intersect(self, l):
        """Returns the intersection of a line with the current line (DOSSSVector) or None if the lines are parallel or identical.
        """
        # check for parallelity
        if(l.u == self.u or self.u == DOSSSVector(0, 0) or l == DOSSSVector(0, 0)):
            return None
        # get lambda factor
        A = -(self.a.x() * l.u.y() - l.a.x() * l.u.y() - l.u.x() * self.a.y() + l.u.x() * l.a.y()) / (self.u.x() * l.u.y() - l.u.x() * self.u.y())
                
        return self.get_point(A)
    
    # return intersection when point lies between the given points of the line
    def bounded_intersection(self, l, p1, p2):
        """Return the intersection of a line l (DOSSSLine) with the current line (DOSSSVector) only if it lies between the points p1 (DOSSSVector) and p2 (DOSSSVector), otherwise returns None.
        """
        p = self.intersect(l)
        if(p == None):
            return None
        
        # check whether the point lies between the two points
        # this is the case, when the distance between p and p1 and the distance between p and p2
        # is smaller than the distance between p1 and p2 (p is part of the line!)
        l0 = (p1 - p2).length()
        if((p - p1).length() < l0 and (p - p2).length() < l0):
            if (l.isLambdaPositiveForPoint(p)):
                return p
       
        return None
    
    # returns a line orthogonal to this line which goes through the specified point
    def get_normal(self, p):
        """Returns a line orthogonal to this line through the specified point p (DOSSSVector).
        """
        return DOSSSLine(p, DOSSSVector(self.u.y(), -1.0 * self.u.x()))
    
    # mirror a line on another line - the new base point is the intersection of the two lines
    def mirror(self, l):
        """Mirror the current line on another line l. The new base point is the intersection of the two lines.
        """
        p = self.intersect(l)
        if p != None:
            theta = 2 * atan2(l.u.y(), l.u.x())
            u = DOSSSVector(cos(theta) * self.u.x() + sin(theta) * self.u.y(), sin(theta) * self.u.x() - cos(theta) * self.u.y())            
            return DOSSSLine(p, u)
        else:
            return DOSSSLine(self.a, self.u)
    
    # rotate the line by the angle alpha
    def rotate(self, alpha):        
        """Returns a copy of the current line rotated by an angle alpha (in degrees).
        """
        return DOSSSLine(self.a.rotate(alpha), self.u.rotate(alpha))

def getLineThroughPoints(p1, p2):
    """Create a DOSSSLine object defined by two points p1 (DOSSSVector) and p2 (DOSSSVector).
    """
    u = p2 - p1
    u = u * (1.0 / u.length())
    return DOSSSLine(p1, u)

# get refracted (ior != 0) or reflected (ior = 0) ray from incident vector u and surface normal n
# see "Needful Things" - paper
def Snell(u, n, ior = 0):
    """Apply Snell's law to a vector.
    
    :param DOSSSVector u: Incident vector.
    :param DOSSSVector n: Surface normal vector.
    :param float ior: Index of refraction of the refracting object (ior != 0). Set to zero to calculate reflected vector.
    :returns: Refracted (ior != 0) or reflected (ior == 0) vector.
    """
    # get unit vectors
    u1 = u.unit()
    n1 = n.unit()
    N = deepcopy(ior)
    nphi = u1 * n1
    
    # flip surface normal if ray is incident from the air side -> invert also ior
    if nphi < 0:
        n1 = n1 * (-1.0)
        nphi = u1 * n1        
        if(ior != 0):
            N = 1.0 / N            
    
    # get unit vector parallel to surface
    m1 = DOSSSVector(n1.y(), -n1.x())
    mphi = u1 * m1
    if mphi < 0:   
        m1 = DOSSSVector(-n1.y(), n1.x())
        mphi = u1 * m1
    
    nphip = 1.0 - N * N * (1.0 - nphi * nphi)
    if ior == 0 or nphip < 0:  # normal reflection or total internal reflection
        up = n1 * (-nphi) + m1 * mphi
    elif mphi == 0:  # going straight
        up = u1
    else:   # refraction
        up = n1 * sqrt(nphip) + m1 * mphi * N          
    
    return up.unit()

# get intersection with sphere (radius R, centered at x0)
def IntersectionWithSphere(line, x0, R):
    """Calculate the intersection between a line and a sphere.
    
    :param DOSSSLine line: The line.
    :param DOSSSVector x0: Center of the sphere.
    :param float R: Radius of the sphere.
    :returns: Intersection(s) (Sequence of DOSSSVectors of length [0, 1, 2]).
    """
    a = line.u.x()**2 + line.u.y()**2
    b = 2 * (line.a.x() - x0) * line.u.x() + 2 * line.a.y() * line.u.y()
    c = (line.a.x() - x0)**2 + line.a.y()**2 - R**2
    D = b**2 - 4 * a * c     
    p =[]
    
    if D == 0:
        l1 = -b / (2 * a)
        if l1 >= 0:
            p1 = line.get_point(l1)                     
            p.append(p1)
    elif(D > 0):
        l1 = (-b + sqrt(D))/(2 * a)
        if l1 >= 0:
            p1 = line.get_point(l1)
            p.append(p1)
        l2 = (-b - sqrt(D))/(2 * a)
        if l2 >= 0:
            p2 = line.get_point(l2)
            p.append(p2)
    return p

# get intersection with parabola (focal length f), (see notes on exact geometry)
def IntersectionWithParabola(line, f):   
    """Calculate the intersection between a line and a parabola.
    
    :param DOSSSLine line: The line.
    :param float f: Focal length of the parabola.
    :returns: Intersection(s) (Sequence of DOSSSVectors of length [0, 1, 2])
    """
    a = -line.u.x()**2 / (2 * f)
    b = -(line.a.x() - f) * line.u.x() / f - line.u.y()
    c = -(line.a.x() - f)**2 / (2 * f) + f / 2 - line.a.y()
    D = b**2 - 4 * a * c     
    p =[]       
    
    if a != 0:        
        if D == 0:
            l1 = -b / (2 * a)
            if l1 >= 0:
                p1 = line.get_point(l1)                     
                p.append(p1)
        elif(D > 0):
            l1 = (-b + sqrt(D))/(2 * a)            
            if l1 >= 0:
                p1 = line.get_point(l1)
                p.append(p1)
            l2 = (-b - sqrt(D))/(2 * a)            
            if l2 >= 0:
                p2 = line.get_point(l2)
                p.append(p2)
    else:
        l1 = -c / b               
        if l1 >= 0:
            p1 = line.get_point(l1)                     
            p.append(p1)
    return p
