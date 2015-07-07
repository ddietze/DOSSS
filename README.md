Daniel's Optics Simulation Software Suite (DOSSS)
=================================================

Despite its big name, DOSSS is a *simple 2D simulation tool* that quickly allows you to create optical arrangements and visualize light propagation through optical components and complex assemblies using raytracing. The propagation of the light rays is thereby governed purely by geometric optics and Snell's law at *each* interface of an optical component. As a consequence, the thickness of the optical components matters, i.e., there will be a difference in the optical properties of a thick and a thin lens despite them having the same focal length.

Support for wavelength-dependent optical properties is currently built in indirectly and can be controlled by setting the index of refraction for each optical component. I have planned to extend this concept by allowing light sources with multiple wavelengths and wavelength-dependent refractive indices instead of constants.

Currently implemented optical components / objects:
* plano-concave lens
* plano-convex lens
* hemispheric lens
* right-angle prism
* parabolic mirror
* planar mirror
* beam splitter
* beam stop
* label
* marker for grouping elements
* parallel light source (e.g. a laser)
* point light source (e.g. a lamp)

In addition, you can easily implement your own objects into DOSSS, as is explained in the documentation.

Usage
=====

There is no installation routine / setup file yet. In order to use DOSSS, simply download and unpack the zip archive and execute the main file *opsim.py* using python. I have tested/developed this program using Python 2.7, mainly due to the availability of wxPython at that time. However, it should also run under Python 3 (maybe with some fixes to the print-syntax).  

Prerequisites: 
* wxPython
* Numpy

Documentation
=============

Documentation of the program and the source code can be found on my GitHub Pages: <http://ddietze.github.io/DOSSS>.
   
Licence
=======

This program is free software: you can redistribute and/or modify 
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
