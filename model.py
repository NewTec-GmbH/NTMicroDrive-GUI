#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
  (c) NewTec GmbH System-Entwicklung und Beratung 2018   -   www.newtec.de

 $Id: model.py 2634 2019-04-27 16:54:51Z brunner $
 $URL: https://svn/MIC/HVC4223/trunk/Software/GUI_Marketing/system/Coding/model.py $

'''

import collections
from datetime import datetime
from PyQt5 import QtCore
import comLib.linAdapter as rpc
import controller

   
    
class DefaultValues(object):
    #ACCELERATION = rpc.Acceleration.ONE
    INIT_CURRENT_POS = 0
    NEW_POS = 0
    SPEED = 0
    DIRECTION = rpc.Direction.STOP
    STALL_DETECTION = False
    MOTOR_ENABLED = False
    OP_MODE = rpc.OpMode.POSITION_CTRL


class PlotData(object):
    ''' Container for  X, Y plot data. '''
    
    def __init__(self, bufferSize):
        '''
            - bufferSize: Number of (x,y) data points we hold for
                          plot visualization
        '''
        self.x = collections.deque([0.0] * bufferSize, bufferSize)
        self.y = collections.deque([0.0] * bufferSize, bufferSize)
    
    def add(self, x, y):
        ''' Add datapoint to plot data. '''
        self.x.append(x)
        self.y.append(y)
        
    def clear(self):
        ''' Deletes all plot data. '''
        self.x.clear()
        self.y.clear()


class Model(object):
    '''
        Provides data further to LIN Adapater.
        Requests data from LIN Adapter.
        Data provision / requesting is done cyclic.
        Notifies/updates Controller with new LIN Adapter data.        
    '''      

    #Update intervall in milliseconds
    UPDATE_INTERVAL   = 200
    
    # Timewindows in ...
    TIME_WINDOW_WIDTH = 1000
    
    def __init__(self, linAdapter):
        ''' 
            - linAdapter: LIN Adapter object
        '''
        # Controller Object: Ifc for UI control
        self._ctrl = None
        
        # LIN Adapter Access
        self._linAdapter = linAdapter
        
        # Cyclic update _timer
        self._timer = QtCore.QTimer()
        
        # Register callback function for cyclic update
        self.setCyclicUpdateCallback(self.cyclicUpdate)
        
        # Initialize Control Frame
        self.ctrlFrame = rpc.HVC_ControlFrame()
        self.ctrlFrame.initPosition = DefaultValues.INIT_CURRENT_POS
        self.ctrlFrame.newPosition = DefaultValues.NEW_POS
        self.ctrlFrame.speed = DefaultValues.SPEED
        self.ctrlFrame.opMode = DefaultValues.OP_MODE
        self.ctrlFrame.motorEnabled = DefaultValues.MOTOR_ENABLED
        self.ctrlFrame.isStallDetection = DefaultValues.STALL_DETECTION
        self.ctrlFrame.direction = DefaultValues.DIRECTION        
        
        
        # Initialize Status Frame
        self.statusFrame = rpc.HVC_StatusFrame()
        
        # Update intervall for plots / serial commonication in milliseconds
        self._interval = Model.UPDATE_INTERVAL
        
        # Number of data points we display at once in a plot
        self._bufsize = Model.TIME_WINDOW_WIDTH
        
        # BVDD Plot Data
        self._plotDataBvdd = PlotData(self._bufsize)
        
        # Temperature Plot Data
        self._plotDataTemperature = PlotData(self._bufsize)
        
        # Rotor Speed Plot Data
        self._plotDataRotorSpeed = PlotData(self._bufsize)
        
        # Start time of data plots
        self._startTime = None
      
        
    def registerController(self, controllerObj):
        ''' Register UI Controller. '''
        self._ctrl = controllerObj
    
    
    def setCyclicUpdateCallback(self, funcRef):
        ''' Set cylic timer callback. '''
        self._timer.timeout.connect(funcRef)
    
    
    def clearData(self):
        ''' Clear plot data buffers. '''
        self._plotDataBvdd.clear()
        self._plotDataTemperature.clear()
        self._plotDataRotorSpeed.clear()
    
    
    def start(self, comPort):
        ''' Start communication with LIN Adapter.
            Status is requested cyclic and Controller is updated with new data.            
        '''        
        # Clear all plot data
        self.clearData()
        
        # Set start time
        self._startTime = datetime.now()
        
        try:
            # Open communication channel with LIN Adapter
            self._linAdapter.connect(comPort)

            if self._linAdapter.isConnected:
                # Start cyclic timer           
                self._timer.start(self._interval)
                
                #Update ui's target online status indicator
                self._ctrl.setStatusIndicator(controller.Status.TARGET_ONLINE)
            else:
                errorMsg = "Connected device on {} seems not to be a valid LIN-Adapter?!"
                self._ctrl.showErrorDialog(errorMsg.format(comPort))

        except:
            errorMsg = "Could not connect to LINAdapter({})"
            raise Exception(errorMsg.format(comPort))
    
    
    def stop(self):
        ''' Stop cyclic update of LIN Adapter. '''       
        self._timer.stop()        
        if self._linAdapter.isConnected:
            self._linAdapter.disconnect()
    
    
    def cyclicUpdate(self):       
        ''' Update LIN adapter with current control data.
            Requests current status of LIN Adapter.
            Update of UI with received status data.
        '''
        # Update LIN Adapter with current settings
        if (True == self._linAdapter.callLinSendMsg(self.ctrlFrame)):
        
            # Request current status data from LIN adapter
            status = self._linAdapter.callGetStatus(self.statusFrame)
        
            # Get elapsed time from start
            dt = (self._getElapsedTime() / controller.DefinedValues.TIMEBASE_FACTOR.value)
            #20190822 BBr fix for kms as time scale to seconds + fast update rate
            
            # Update BVDD Plot with new data       
            self._plotDataBvdd.add(dt, (status.bvdd * controller.DefinedValues.BVDD_FACTOR.value))
            self._ctrl.updateBvddPlot(self._plotDataBvdd)
            
            # Update Temperature Plot with new data
            self._plotDataTemperature.add(dt, (status.tj + controller.DefinedValues.TJ_OFFSET.value))
            #20180822 BBr added Temp offset - 60 °C
            self._ctrl.updateTemeperatuePlot(self._plotDataTemperature)
            
            # Update RotortSpeed Plot with new data
            self._plotDataRotorSpeed.add(dt, (status.currentSpeed * controller.DefinedValues.RPM_FACTOR.value))
            self._ctrl.updateRotorSpeedPlot(self._plotDataRotorSpeed)
            
            # Update current speed
            self._ctrl.updateCurrentSpeed(status.currentSpeed)
                    
            # Update current position
            self._ctrl.updateCurrentPosition(status.currentPos)
            
            # Update status indicator Error ##Lin Error
            statusIndication = controller.Status.ERROR if status.hvcStatus else controller.Status.NO_ERROR        
            #statusIndication = controller.Status.ERROR if status.isLinError else controller.Status.NO_ERROR
            self._ctrl.setStatusIndicator(statusIndication)
           
            # Update status indicator Over Current
            statusIndication = controller.Status.OVER_CURRENT if status.isOverCurrent else controller.Status.NO_OVER_CURRENT
            self._ctrl.setStatusIndicator(statusIndication)
            
            # Update status indicator Over Temperature
            statusIndication = controller.Status.OVER_TEMPERATURE if status.isOverTemperature else controller.Status.NO_OVER_TEMPERATURE
            self._ctrl.setStatusIndicator(statusIndication)
        else:
            self.stop()
            self._ctrl.setStatusIndicator(controller.Status.TARGET_OFFLINE)
            
        
    def _getElapsedTime(self):
        ''' Returns time difference from startTime and now in milliseconds. '''
        #Time difference from start        
        dt = datetime.now() - self._startTime 
        
        #Time difference in milliseconds
        dt_ms = int(dt.total_seconds() * controller.DefinedValues.TIMEBASE_FACTOR.value)        
        return dt_ms
