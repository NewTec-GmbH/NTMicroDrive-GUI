#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
  (c) NewTec GmbH System-Entwicklung und Beratung 2018   -   www.newtec.de

 $Id: controller.py 2634 2019-04-27 16:54:51Z brunner $
 $URL: https://svn/MIC/HVC4223/trunk/Software/GUI_Marketing/system/Coding/controller.py $

'''

import sys
import webbrowser

from PyQt5 import QtCore, QtGui, QtWidgets 
from PyQt5.Qt import QDialog, QTimer
from serial.tools import list_ports

from ui.mainWindow import Ui_MainWindow
from ui.settingsWindow import Ui_AppSettings
from ui.numpad import Ui_Numpad

import comLib.linAdapter as rpc
import model

from enum import Enum


   
LicenseText = """This program is free software: you can redistribute it and/or modify<br>  
it under the terms of the GNU General Public License as published by<br>
the Free Software Foundation, either version 3 of the License, or<br>
(at your option) any later version.<br>
<br>
This program is distributed in the hope that it will be useful,<br>
but WITHOUT ANY WARRANTY; without even the implied warranty of<br>
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.<br>
See the GNU General Public License for more details.<br>
<br>
You should have received a copy of the GNU General Public License<br>
along with this program.  If not, see 
&lt;<a href = "https://www.gnu.org/licenses/">https://www.gnu.org/licenses/</a>&gt;.<br>
<br>
Dieses Programm ist Freie Software: Sie können es unter den Bedingungen<br>
der GNU General Public License, wie von der Free Software Foundation,<br>
Version 3 der Lizenz oder (nach Ihrer Wahl) jeder neueren<br>
veröffentlichten Version, weiter verteilen und/oder modifizieren.<br>
<br>
Dieses Programm wird in der Hoffnung bereitgestellt, dass es nützlich sein wird,<br>
jedoch OHNE JEDE GEWÄHR; sogar ohne die implizite Gewähr der MARKTFÄHIGKEIT
oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.<br>
Siehe die GNU General Public License für weitere Einzelheiten.<br>
<br>
Sie sollten eine Kopie der GNU General Public License zusammen mit diesem<br>
Programm erhalten haben. Wenn nicht, siehe 
&lt;<a href = "https://www.gnu.org/licenses/">https://www.gnu.org/licenses/</a>&gt;.<br>
<br>
Source Code can be found at:<br>
<a href = "https://github.com/NewTec-GmbH/NTMicroDrive-GUI">
https://github.com/NewTec-GmbH/NTMicroDrive-GUI</a><br>"""


   
class Status(object):
    ''' Possible Application status indicators.'''
        
    OVER_CURRENT = 0
    NO_OVER_CURRENT = 1
    
    OVER_TEMPERATURE = 2
    NO_OVER_TEMPERATURE = 3
    
    STALL_DETECTED = 4
    NO_STALL_DETECTED = 5
    
    ERROR = 6
    NO_ERROR = 7
    
    TARGET_ONLINE = 8
    TARGET_OFFLINE = 9
    
class DefinedValues(Enum):
    ''' Defines of "MagicNumbers" '''
    
    # Motor variables
    BVDD_FACTOR = 0.2       # 0,2 V per digit
    TJ_OFFSET = -60         # unit in °C
    RPM_FACTOR = 8        # 128 RPM/digit conversion
    
    # Plot y-axis range values
    BVDD_Y_MIN_RANGE = 0    # unit in V
    BVDD_Y_MAX_RANGE = 15   # unit in V
    
    TJ_Y_MIN_RANGE = 0      # unit in °C
    TJ_Y_MAX_RANGE = 150    # unit in °C
    
    RS_Y_MIN_RANGE = 0      # in rpm (1/min) 
    RS_Y_MAX_RANGE = 500   # in rpm (1/min)
    
    # Timebase adjustment
    TIMEBASE_FACTOR = 1000  # to convert kms to s
    
    PIC_SWAP_TIME = 5000    # time cycle for swaping image in ms
    
    # Weblink
    LEARN_MORE_WEB_ADDRESS = 'https://www.newtec.de/loesungen/plattformen/ntmicrodrive/'   # webpage for button LearnMore
    
    '''
    Access example of an Enum:
    ScaleValue.TJ_OFFSET            ->    Returns human readable string: ScaleValue.TJ_OFFSET
    ScaleValue.TJ_OFFSET.value      ->    returns value:    -60
    ScaleValue.TJ_OFFSET.name       ->    returns name:    TJ_OFFSET
    
    '''      

class Controller(QtWidgets.QMainWindow):
    '''
        Responsible for updating of UI/View.
        Control and updates of model with new data.
    '''
 

    def __init__(self, model):
        ''' initialization of class '''
        super().__init__()
        
        self.value = str()
        # Current Model we use
        self._model = model  
        
        # Application's UI main window
        self._ui = Ui_MainWindow()
        
        # Setup main window
        self._ui.setupUi(self)       
        
        #setup numpad
        self.qDialog = QDialog()
        self.numpadWindow = Ui_Numpad()
        self.numpadWindow.setupUi(self.qDialog)
        self.numpadWindow.numberToSet.setAlignment(QtCore.Qt.AlignRight)
        self.numpadWindow.numberToSet.setMaxLength(6)
        self.numpadWindow.numberToSet.setReadOnly(True)
        self.qLineValidator = QtGui.QIntValidator

        self.numpadButtons = [self.numpadWindow.button0, self.numpadWindow.button1, self.numpadWindow.button2, self.numpadWindow.button3,
                              self.numpadWindow.button4, self.numpadWindow.button5, self.numpadWindow.button6, self.numpadWindow.button7,
                              self.numpadWindow.button8, self.numpadWindow.button9
                             ]
        for idx, item in enumerate(self.numpadButtons):
            #print(type(item))
            #print(idx)
            item.setText(str(idx))
            item.clicked.connect(lambda: self._buttonpres())
        
        self.numpadWindow.buttonBackspace.clicked.connect(self._dellast)
        self.numpadWindow.buttonSub.clicked.connect(self._negateValue)


        # Set UI input objects to default state/value
        self._setUiInputsToDefault()        
                        
        # Connect UI elements/objects signals and slots
        self._connectSignalSlots()
        
        # Add menu bar items
        self._addMenubarItems()        
        
        # Setup Plots
        self._bvddPlot = self._ui.graphicsViewBVDD.plot([], [], pen=(0, 0, 255))
        self._ui.graphicsViewBVDD.setLabel('left', 'BVDD', units='V')
        self._ui.graphicsViewBVDD.setLabel('bottom', 'Time', units='s')
        self._ui.graphicsViewBVDD.showGrid(x=True, y=True)
        self._ui.graphicsViewBVDD.setYRange(DefinedValues.BVDD_Y_MIN_RANGE.value, DefinedValues.BVDD_Y_MAX_RANGE.value, 0, True)
                
        self._temperaturePlot = self._ui.graphicsViewTemperature.plot([], [], pen=(0, 255, 0))
        self._ui.graphicsViewTemperature.setLabel('left', 'Tj', units='°C')
        self._ui.graphicsViewTemperature.setLabel('bottom', 'Time', units='s')
        self._ui.graphicsViewTemperature.showGrid(x=True, y=True)
        self._ui.graphicsViewTemperature.setYRange(DefinedValues.TJ_Y_MIN_RANGE.value, DefinedValues.TJ_Y_MAX_RANGE.value, 0, True)
        
        self._rotorSpeedPlot = self._ui.graphicsViewRotorSpeed.plot([], [], pen=(255, 0, 0))
        self._ui.graphicsViewRotorSpeed.setLabel('left', 'Rotor Speed', units='PPS')
        self._ui.graphicsViewRotorSpeed.setLabel('bottom', 'Time', units='s')
        self._ui.graphicsViewRotorSpeed.showGrid(x=True, y=True)
        self._ui.graphicsViewRotorSpeed.setYRange(DefinedValues.RS_Y_MIN_RANGE.value, DefinedValues.RS_Y_MAX_RANGE.value, 0, True)
        
        self.__rawCurrentSpeed = 0
        self.__currentSpeed = 0
        
        self._picIndex = 0            # first image to be replaced

        self._picTimer= QTimer()
        self._picTimer.timeout.connect(self.updatePic)
        self._picTimer.start(DefinedValues.PIC_SWAP_TIME.value)
     
            
        
    def updatePic(self):
        ''' cyclical switch of banner pic '''
        self._picIndex +=1       # next image
        if(self._picIndex > 5):  # last image reached ?
            self._picIndex =0

        if (self._picIndex == 0):
            self._ui.ImageButton.setStyleSheet("border-image: url(:/Image/resources/NT_BannerSW31.png);") 
        elif (self._picIndex == 1):
            self._ui.ImageButton.setStyleSheet("border-image: url(:/Image/resources/NT_BannerSW32.png);") 
        elif (self._picIndex == 2):
            self._ui.ImageButton.setStyleSheet("border-image: url(:/Image/resources/NT_BannerSW33.png);") 
        elif (self._picIndex == 3):
            self._ui.ImageButton.setStyleSheet("border-image: url(:/Image/resources/NT_BannerSW34.png);") 
        elif (self._picIndex == 4):
            self._ui.ImageButton.setStyleSheet("border-image: url(:/Image/resources/NT_BannerSW35.png);") 
        elif (self._picIndex == 5):
            self._ui.ImageButton.setStyleSheet("border-image: url(:/Image/resources/NT_BannerSW36.png);")
        else:
            self._picIndex =0   #default never reached
         
                
    def updateCurrentPosition(self, position):
        ''' Set current position displayed in 'Current Status' LCD element. '''
        self._ui.currentPositionLCD.display(position) 
        
    def setStatusIndicator(self, statusIndicator):
        ''' Set status indicator elements. '''
        if Status.OVER_CURRENT == statusIndicator:
            self._ui.labelOverCurrentLED.setPixmap(QtGui.QPixmap(":/led/resources/red-led-on.png"))
        
        elif Status.NO_OVER_CURRENT == statusIndicator:
            self._ui.labelOverCurrentLED.setPixmap(QtGui.QPixmap(":/led/resources/red-led-off.png"))
        
        elif Status.OVER_TEMPERATURE == statusIndicator:
            self._ui.labelOverTemperatureLED.setPixmap(QtGui.QPixmap(":/led/resources/red-led-on.png"))
        
        elif Status.NO_OVER_TEMPERATURE == statusIndicator:
            self._ui.labelOverTemperatureLED.setPixmap(QtGui.QPixmap(":/led/resources/red-led-off.png"))
       
        elif Status.ERROR == statusIndicator:
            self._ui.labelErrorLED.setPixmap(QtGui.QPixmap(":/led/resources/red-led-on.png"))
        
        elif Status.NO_ERROR == statusIndicator:
            self._ui.labelErrorLED.setPixmap(QtGui.QPixmap(":/led/resources/red-led-off.png"))
            
        elif Status.TARGET_ONLINE == statusIndicator:
            self._ui.labelTargetOnlineLED.setPixmap(QtGui.QPixmap(":/led/resources/green-led-on.png"))
            
        elif Status.TARGET_OFFLINE == statusIndicator:
            self._ui.labelTargetOnlineLED.setPixmap(QtGui.QPixmap(":/led/resources/green-led-off.png"))
        else:
            #Nothing to do here
            pass
    
    def updateBvddPlot(self, plotData):
        ''' Updates BVDD plot with plotData. '''
        self._bvddPlot.setData(plotData.x,  plotData.y)
    
    def updateTemeperatuePlot(self,plotData):
        ''' Updates Temperature plot with plotData. '''
        self._temperaturePlot.setData(plotData.x,  plotData.y)
    
    def updateRotorSpeedPlot(self, plotData):
        ''' Updates Rotor Speed plot with plotData. '''
        self._rotorSpeedPlot.setData(plotData.x,  plotData.y)
        
    def updateCurrentSpeed(self, speed):
        ''' get current speed value '''
        self.__rawCurrentSpeed = speed

    def getCurrentSpeedRPM(self):
        ''' returns the current speed'''
        self.__currentSpeedRPM = (self.__rawCurrentSpeed * DefinedValues.RPM_FACTOR.value)
                
        return self.__currentSpeedRPM
    
    def buttonLearnMore(self):
        ''' open micronas webaddress '''
        webbrowser.open(DefinedValues.LEARN_MORE_WEB_ADDRESS.value)
        
        
    def showErrorDialog(self, errorMsg):
        ''' Shows a modal error message dialog. 
            errorMsg: Message (string) displayed in dialog.
        '''
        msg = QtWidgets.QErrorMessage()
        msg.setWindowTitle("ERROR MESSAGE")
        msg.setWindowModality(QtCore.Qt.ApplicationModal)
        msg.showMessage(errorMsg)        
        msg.exec_()
    
    def _addMenubarItems(self):
        ''' create sub items in menu bar and connect with actions '''
        action = QtWidgets.QAction("Connect", self)
        action.triggered.connect(self._onMenuBarItemSelectComPort)
        self._ui.menuSettings.addAction(action)        

        action = QtWidgets.QAction("License", self)
        action.triggered.connect(self._onLicense)
        self._ui.menuClose.addAction(action)
        
        action = QtWidgets.QAction("Exit", self)
        action.triggered.connect(self._closeApp)
        self._ui.menuClose.addAction(action)
        
    
    def _connectSignalSlots(self):
        ''' Connect UI's signals and slots connections. '''        
        
        # Connect push buttons 
        self._ui.pushButtonEnableMotorCtrl.clicked.connect(self._onPushButtonEnableMotorCtrl)
        self._ui.pushButtonResetInputs.clicked.connect(self._onPushButtonResetInputs)
        
        # Connect Direction radio buttons
        self._ui.radioButtonDirectionStop.clicked.connect(self._onRadioButtonDirection)
        self._ui.radioButtonDirectionClockWise.clicked.connect(self._onRadioButtonDirection)
        self._ui.radioButtonDirectionAntiClockwise.clicked.connect(self._onRadioButtonDirection)
        
        # Connect Control radio buttons
        self._ui.radioButtonPositionCtrl.clicked.connect(self._onRadioButtonControlSelection)
        self._ui.radioButtonSpeedCtrl.clicked.connect(self._onRadioButtonControlSelection)
        
        # Connect speed slider control
        self._ui.speedSlider.valueChanged.connect(self._updateSpeedGroupBox)
        
        # Connect speed spinBox
        self._ui.speedspinBox.editingFinished.connect(self._updateSpeedSpinBox)

        self._ui.speedChangeButton.clicked.connect(self._ChangeSpeed)
        
        # Connect position slider control
        self._ui.positionSlider.valueChanged.connect(self._updatePositionGroupBox)
        
        # Connect position spinBox
        self._ui.positionspinBox.editingFinished.connect(self._updatePositionSpinBox)

        self._ui.posChangeButton.clicked.connect(self._ChangePos)
        
        # Connect pushButton_learnMore
        self._ui.ImageButton.clicked.connect(self.buttonLearnMore)
        
        
    
    def _onPushButtonEnableMotorCtrl(self):
        ''' action for Button to Enable/Disable Motor control'''
        if self._ui.pushButtonEnableMotorCtrl.isChecked():
            self._ui.pushButtonEnableMotorCtrl.setText("Disable Motor Control")
            self._model.ctrlFrame.motorEnabled = True
            #we want only a change of speed and position if the motor is enabled
            if self._ui.radioButtonPositionCtrl.isChecked():
                self._ui.groupBoxAcceleration.setEnabled(True)
                self._ui.groupBoxPosition.setEnabled(True)
                self._ui.groupBoxSpeed.setEnabled(True)
                self._model.ctrlFrame.opMode = rpc.OpMode.POSITION_CTRL
            else:
                self._ui.groupBoxAcceleration.setEnabled(True)
                self._ui.groupBoxPosition.setEnabled(False)
                self._ui.groupBoxDirection.setEnabled(True)
                self._ui.groupBoxSpeed.setEnabled(True)
                self._model.ctrlFrame.opMode = rpc.OpMode.SPEED_CTRL       
            
        else:
            self._ui.pushButtonEnableMotorCtrl.setText("Enable Motor Control")
            self._model.ctrlFrame.motorEnabled = False
            #motor disable -> no changes on speed and position
            self._ui.groupBoxPosition.setEnabled(False)
            self._ui.groupBoxSpeed.setEnabled(False)
            self._ui.groupBoxDirection.setEnabled(False)
            self._ui.groupBoxAcceleration.setEnabled(False)
            if self._ui.radioButtonPositionCtrl.isChecked():
                self._model.ctrlFrame.opMode = rpc.OpMode.POSITION_CTRL
                #pass
            elif self._ui.radioButtonSpeedCtrl.isChecked():
                self._model.ctrlFrame.opMode = rpc.OpMode.SPEED_CTRL
                #pass
    
        
    def _onPushButtonResetInputs(self):
        ''' Reset inputs to default values '''
        self._setUiInputsToDefault()
    
    def _onRadioButtonControlSelection(self):
        ''' action to activate speed or position control'''
        
        if self._ui.pushButtonEnableMotorCtrl.isChecked():
            
            if self._ui.radioButtonPositionCtrl.isChecked() and self.getCurrentSpeedRPM() < 1:
                self._ui.groupBoxDirection.setEnabled(False)
                self._ui.groupBoxPosition.setEnabled(True)
                self._ui.groupBoxSpeed.setEnabled(True)
                self._model.ctrlFrame.opMode = rpc.OpMode.POSITION_CTRL
            
            elif self._ui.radioButtonSpeedCtrl.isChecked() and self.getCurrentSpeedRPM() < 1: 
                self._ui.groupBoxDirection.setEnabled(True)
                self._ui.groupBoxPosition.setEnabled(False)
                self._ui.groupBoxSpeed.setEnabled(True)
                self._model.ctrlFrame.opMode = rpc.OpMode.SPEED_CTRL
            
            elif self._ui.radioButtonPositionCtrl.isChecked() and self.getCurrentSpeedRPM() > 1:
                self._ui.radioButtonPositionCtrl.setChecked(False)
                self._ui.radioButtonSpeedCtrl.setChecked(True)
                
            elif self._ui.radioButtonSpeedCtrl.isChecked() and self.getCurrentSpeedRPM() > 1:
                self._ui.radioButtonSpeedCtrl.setChecked(False)
                self._ui.radioButtonPositionCtrl.setChecked(True)
                
                
        
    def _onRadioButtonDirection(self):
        ''' Update model with selected direction. '''
        if self._ui.radioButtonDirectionStop.isChecked():
            self._model.ctrlFrame.direction = rpc.Direction.STOP
            
        elif self._ui.radioButtonDirectionClockWise.isChecked():
            self._model.ctrlFrame.direction = rpc.Direction.CLOCKWISE
            
        elif self._ui.radioButtonDirectionAntiClockwise.isChecked():
            self._model.ctrlFrame.direction = rpc.Direction.ANTI_CLOCKWISE
        
        else:
            #Nothing to do here
            pass
            
    
    def _updateSpeedGroupBox(self):
        ''' Updates Speed Group Box elements. '''
        speed = self._ui.speedSlider.value()
        #self._ui.speedLCD.display(speed)
        self._model.ctrlFrame.speed = int(speed / DefinedValues.RPM_FACTOR.value)
        # Sync between slider and Spinbox
        self._syncSpeedSpinBoxAndSpeedSlider(speed)
    
    def _updateSpeedSpinBox(self):
        ''' update speed in speed display'''
        speed = self._ui.speedspinBox.value()
        #self._ui.speedLCD.display(speed)
        self._model.ctrlFrame.speed = int (speed / DefinedValues.RPM_FACTOR.value)
        # Sync between slider and Spinbox
        self._syncSpeedSpinBoxAndSpeedSlider(speed)

    def _syncSpeedSpinBoxAndSpeedSlider(self, speed):
        ''' Update and Sync of the GUI-Values '''
        self._ui.speedSlider.setValue(speed)
        self._ui.speedspinBox.setValue(speed)                             
            
    def _updatePositionGroupBox(self):
        ''' Updates Position Group Box elements. '''
        position = self._ui.positionSlider.value()
        #self._ui.positionLCD.display(position)        
        self._model.ctrlFrame.newPosition = position
        # Sync between slider and Spinbox
        self._syncPositionSpinBoxAndPositionSlider(position)
    
    def _updatePositionSpinBox(self):
        '''update position in position display'''
        position = self._ui.positionspinBox.value()
        #self._ui.positionLCD.display(position)
        self._model.ctrlFrame.newPosition = position
        # Sync between slider and Spinbox
        self._syncPositionSpinBoxAndPositionSlider(position) 
        
    def _syncPositionSpinBoxAndPositionSlider(self, position):
        ''' Update and Sync of the GUI-Values '''
        self._ui.positionSlider.setValue(position)
        self._ui.positionspinBox.setValue(position)
        
    def _setUiInputsToDefault(self):
        ''' Set UI elements to default values. '''
        self._ui.pushButtonEnableMotorCtrl.setChecked(model.DefaultValues.MOTOR_ENABLED)
        self._onPushButtonEnableMotorCtrl()
       
        self._ui.speedSlider.setValue(model.DefaultValues.SPEED)
        self._ui.positionSlider.setValue(model.DefaultValues.INIT_CURRENT_POS)  
           
        #self._ui.radioButtonAcceleration1.setChecked(model.DefaultValues.ACCELERATION)
        self._ui.radioButtonDirectionStop.setChecked(model.DefaultValues.DIRECTION)        
        self._onRadioButtonControlSelection()    
    
    
    def _onLicense(self):
        ''' open message box and show license information
        '''
        # create message box
        msg = QtWidgets.QMessageBox()
        # icon information (I)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        # text format RichText to interprete links in html style 
        msg.setTextFormat(QtCore.Qt.RichText)
        # Text string with license text
        msg.setText(LicenseText)
        # title of window
        msg.setWindowTitle("License Information")
        # show message box
        msg.exec_()
        
        
    def _onMenuBarItemSelectComPort(self):       
        ''' Selection of COM port.
            Starts model on valid port selection.
        ''' 
        
        #Stop model
        self._model.stop()
        
        #We are no more connected
        self.setStatusIndicator(Status.TARGET_OFFLINE)
        
        #Create dialog for COM port selection
        qDialog = QDialog()
        settingWindow = Ui_AppSettings()
        settingWindow.setupUi(qDialog)
        
        #Get COM ports with connected devices
        ports = sorted([port.device for port in list_ports.comports()])
        
        #Populate comboBox with found COM ports
        settingWindow.comboBoxComPorts.clear()
        settingWindow.comboBoxComPorts.addItems(ports)        
        
        #Show dialog
        qDialog.exec_()        
        
        #Evaluate user selection        
        if QDialog.Accepted == qDialog.result():
            # User has accepted by pressing OK button
            
            #Get selected COM-Port
            selectedIdx = settingWindow.comboBoxComPorts.currentIndex()
            comPort = ports[selectedIdx]
            
            self._model.start(comPort)    
        else:
            # User has rejected by pressing CANCEL button
            pass              
    
    
    def _buttonpres(self):
        ''' action asoziated with Button 1 on the numpad
        '''
        #print(type(self.sender()))
        buttonpressed = self.sender()
        #print(type(buttonpressed))
        #print(self.sender().text())
        self.value = self.numpadWindow.numberToSet.text()
        self.value = self.value + buttonpressed.text()
        self.numpadWindow.numberToSet.setText(self.value)

    def _dellast(self):
        ''' usebackspace from qLineEdit to remove last number
        '''
        self.numpadWindow.numberToSet.backspace()

    def _negateValue(self):
        '''negate value for numpad window '''
        currentstring = self.numpadWindow.numberToSet.text()
        if currentstring:
            number = int(currentstring)
        else:
            number = 0
        
        number = number *(-1)
        self.numpadWindow.numberToSet.setText(str(number))

    def _ChangeSpeed(self):       
        ''' Change speed via Numpad.
        '''  
        self.numpadWindow.numberToSet.setValidator(self.qLineValidator(0,4992)) # needs to be the same range as set in UI of qt designer
        
        #Show dialog
        self.qDialog.exec_()        
        
        #Evaluate user selection        
        if QDialog.Accepted == self.qDialog.result():
            # User has accepted by pressing OK button
            
            #Get selected COM-Port
            if(self.numpadWindow.numberToSet.text()):
                speed = int(self.numpadWindow.numberToSet.text())
                self._syncSpeedSpinBoxAndSpeedSlider(speed)
                self.value = str()
                self.numpadWindow.numberToSet.setText(self.value)
            else:
                self._syncSpeedSpinBoxAndSpeedSlider(0)
                self.value = str()
                self.numpadWindow.numberToSet.setText(self.value)

        else:
            # User has rejected by pressing CANCEL button
            self.value = str()
            self.numpadWindow.numberToSet.setText(self.value)
            pass              
    
    def _ChangePos(self):       
        ''' Change Position via Numpad
        ''' 
        self.numpadWindow.numberToSet.setValidator(self.qLineValidator(-16000,16000)) # needs to be the same range as set in UI of qt designer
        
        #Show dialog
        self.qDialog.exec_()        
        
        #Evaluate user selection        
        if QDialog.Accepted == self.qDialog.result():
            # User has accepted by pressing OK button
            
            #Get selected COM-Port
            if(self.numpadWindow.numberToSet.text()):
                pos = int(self.numpadWindow.numberToSet.text()) #need to protect against no return value
                self._syncPositionSpinBoxAndPositionSlider(pos)
                self.value = str()
                self.numpadWindow.numberToSet.setText(self.value)
            else:
                self._syncPositionSpinBoxAndPositionSlider(0)
                self.value = str()
                self.numpadWindow.numberToSet.setText(self.value)


        else:
            # User has rejected by pressing CANCEL button
            self.value = str()
            self.numpadWindow.numberToSet.setText(self.value)
            pass              



        
    def _closeApp(self):
        ''' Close and exit application. '''
        sys.exit()
