#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
  (c) NewTec GmbH System-Entwicklung und Beratung 2018   -   www.newtec.de

 $Id: main.py 2634 2019-04-27 16:54:51Z brunner $
 $URL: https://svn/MIC/HVC4223/trunk/Software/GUI_Marketing/system/Coding/main.py $

'''

import sys
from PyQt5 import QtWidgets
from model import Model
from controller import Controller
from comLib.linAdapter import LINAdapter


WINDOW_TITLE = "NTMicroDrive Control Tool V 1.0.2"

   
    
if __name__ == "__main__":    
    # Create QT application
    app = QtWidgets.QApplication(sys.argv)
      
    # LIN Adapter
    linAdapter = LINAdapter()
    
    # Create Modell
    model = Model(linAdapter)
    
   
      
    # Create controller / main window
    controller = Controller(model)
          
    # Register Controller in model
    model.registerController(controller)
  
    # Set program version
    controller.setWindowTitle(WINDOW_TITLE)    
  
    # Disable window resizing
    #mainWindow.setFixedSize(mainWindow.size())
  
    # Show main window
    controller.show()
  
    # Start QT application
    sys.exit(app.exec_())
