"""
.. module: opsim.opsim_objects
   :platform: Windows
.. moduleauthor:: Daniel Dietze <daniel.dietze@berkeley.edu>

Manages object import into DOSSS. All objects that were placed in the *objects* folder are automatically imported.

.. important:: Each object class has to be placed in its own module and the module file needs to have the same name as the class.

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
import glob
import os
import sys

_dict_of_objects = {}     #: a dictionary mapping object names to modules

def load_from_file(filepath):
    """Dynamically load a python module and return an instance of the class with the same name as the file.
    
    :param str filepath: Name and path of the module to load.
    :returns: Instance of class with same name as module.
    """
    if not os.path.isfile(filepath):
        raise ValueError("Module does not exist!")
    
    mod_name, file_ext = os.path.splitext(os.path.split(filepath)[-1])

    py_mod = None
    if sys.version_info[:2] >= (3, 3):
        from importlib.machinery import SourceFileLoader
        py_mod = SourceFileLoader(mod_name, filepath).load_module()
    else:
        import imp
        if file_ext.lower() == '.pyc':
            py_mod = imp.load_compiled(mod_name, filepath)
        elif file_ext.lower() == '.py':
            py_mod = imp.load_source(mod_name, filepath)

    class_inst = getattr(py_mod, mod_name)()

    return class_inst

def parse_objects():
    """Create a dictionary mapping all existing objects to their modules. This function is called once at the beginning.
    """
    # load modules
    files = sorted(glob.glob("objects\\*.py"))
    
    for d in files:
        if os.path.split(d)[-1] != "__init__.py":
            try:
                cl = load_from_file(d)
                _dict_of_objects[cl.get_name()] = d
            except:
                raise
    
def objectList():
    """Returns a list with object names that can be used to create the menu items, for example.
    """
    # generate dictionary if it does not exist
    if not _dict_of_objects:
        parse_objects()
    
    # return list of keys
    return _dict_of_objects.keys()

def getNewObject(identifier, posx, posy):
    """Create a new object.
    
    :param str identifier: Name of the object as it appears in objectList.
    :param float posx: x-position of object.
    :param float posy: y-position of object.
    :returns: Instance of the new object or None if object not found.
    """
    
    # this also creates the dictionary if it does not yet exist
    if identifier not in objectList():
        return None
    
    # get class instance
    cl = load_from_file(_dict_of_objects[identifier])
    
    # set position
    cl.set_position(posx, posy)
    
    return cl
    