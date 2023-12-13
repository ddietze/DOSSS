"""
.. module: opsim.core.opsim_property_dialog
   :platform: Windows
.. moduleauthor:: Daniel Dietze <daniel.dietze@berkeley.edu>

This dialog provides a standardized method for the user to enter multiple property values for an object.

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

class DOSSS_PropertyDialog(wx.Dialog):
    """A simple property dialog.
     
    :param list options: A list of string - value pairs that give name and value of a parameter.
    """
    def __init__(self, options = [], parent = None):
        wx.Dialog.__init__(self, parent, -1, 'Properties')

        self.myOptions = deepcopy(options)
        
        # main sizer element
        mainSizer = wx.BoxSizer(wx.VERTICAL)        
        self.input = []

        # default - inputs
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        if(len(options) > 1):
            posSizer = wx.BoxSizer(wx.HORIZONTAL)        
            posSizer.Add(wx.StaticText(self, -1, "Position:"), 1, wx.ALIGN_LEFT | wx.ALL, 2)
            self.input.append(wx.TextCtrl(self, -1, str(options[0][1]), size=(88, -1), style=wx.TE_RIGHT))
            posSizer.Add(self.input[0], 0, wx.ALL, 2)
            self.input.append(wx.TextCtrl(self, -1, str(options[1][1]), size=(88, -1), style=wx.TE_RIGHT))
            posSizer.Add(self.input[1], 0, wx.ALL, 2)
            inputSizer.Add(posSizer, 1, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.ALL, 0)
            
            rotSizer = wx.BoxSizer(wx.HORIZONTAL)        
            rotSizer.Add(wx.StaticText(self, -1, "Rotation (deg):"), 1, wx.ALIGN_LEFT | wx.ALL, 2)
            self.input.append(wx.TextCtrl(self, -1, str(options[2][1]), size=(180, -1), style=wx.TE_RIGHT))
            rotSizer.Add(self.input[2], 0, wx.ALL, 2)
            inputSizer.Add(rotSizer, 1, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.ALL, 0)
            
            flipSizer = wx.BoxSizer(wx.HORIZONTAL)        
            flipSizer.Add(wx.StaticText(self, -1, "Mirror:"), 1, wx.ALIGN_LEFT | wx.ALL, 2)
            self.input.append(wx.CheckBox(self, -1, "horizontal", size=(88, -1), style=wx.TE_RIGHT))
            self.input[3].SetValue(int(options[3][1]))
            flipSizer.Add(self.input[3], 0, wx.ALL, 2)        
            self.input.append(wx.CheckBox(self, -1, "vertical", size=(88, -1), style=wx.TE_RIGHT))
            self.input[4].SetValue(int(options[4][1]))
            flipSizer.Add(self.input[4], 0, wx.ALL, 2)
            inputSizer.Add(flipSizer, 1, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.ALL, 0)
            
            # line
            inputSizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 5)
            
            # additional 'options'-inputs
            if len(options) > 5:
                for i in range(5, len(options)):
                    op = options[i]
                    label = wx.StaticText(self, -1, op[0] + ":")
                    sizer = wx.BoxSizer(wx.HORIZONTAL)
                    sizer.Add(label, 1, wx.ALIGN_LEFT | wx.ALL, 2)
                    if(len(op) > 1):
                        self.input.append(wx.TextCtrl(self, -1, str(op[1]), size=(180, -1), style=wx.TE_RIGHT))
                        sizer.Add(self.input[i], 0, wx.ALL, 2)                
                    inputSizer.Add(sizer, 1, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.ALL, 0)
        else:
            inputSizer.Add(wx.StaticText(self, -1, "This Object Has No Properties!"))
        mainSizer.Add(inputSizer, 1, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.ALL, 5)
        
        # buttons
        OkButton = wx.Button(self, wx.ID_OK, "Apply")
        CancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(OkButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonSizer.Add(CancelButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        mainSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER|wx.ALL, 5)        
        
        self.SetSizer(mainSizer)
        self.Layout()
        self.Fit()
        
    def getOptions(self):
        """Returns a list of option values.
        """
        options = []
        for i in range(len(self.input)):
            op = self.input[i]            
            if len(self.myOptions[i]) > 2 and self.myOptions[i][2] == "str":
                options.append(op.GetValue())
            else:
                options.append(float(op.GetValue()))                
        
            # do boundary checks
            if len(self.myOptions[i]) > 2 and self.myOptions[i][2] != "str":
                if(options[i] < self.myOptions[i][2]):
                    options[i] = self.myOptions[i][2]
                if len(self.myOptions[i]) > 3:
                    if(options[i] > self.myOptions[i][3]):
                        options[i] = self.myOptions[i][3]
        return options    