#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
  (c) NewTec GmbH System-Entwicklung und Beratung 2018   -   www.newtec.de

 $Id: linAdapter.py 2630 2019-04-18 10:10:52Z nhaerle $
 $URL: https://svn/MIC/HVC4223/tags/Software/PythonLib/V1.0/Coding/linAdapter.py $

'''

import bitstring
import serial

import numpy as np

class HVC_Status(object):
    ''' Possible HVC status. '''
    HVC_STATUS_OPERATING = 0
    HVC_STATUS_ERROR = 1
    
    NO_OVERCURRENT = 0
    OVER_CURRENT = 1
    
    NO_OVER_TEMEPERATURE = 0
    OVER_TEMEPERATURE = 1
    
    NO_STALL_DETECTED = 0
    STALL_DETECTED = 1
    
    NO_LIN_ERROR = 0
    LIN_ERROR = 1
    

class Acceleration(object):
    ''' accelleration levels'''
    ONE = 1
    TWO = 2
    FOUR = 4


class Direction(object):
    ''' directions '''
    STOP = 0
    CLOCKWISE = 1
    ANTI_CLOCKWISE = 3


class MotorControllState(object):
    ''' states of motor controll'''
    TARGET_ONLINE = 0
    ERROR = 1
    OVER_CURRENT = 2
    OVER_TEMPERATURE = 3
    STALL_DETECTED = 4 


class OpMode():
    ''' control mode states  '''
    POSITION_CTRL = 0
    SPEED_CTRL = 1


class FrameID(object):
    ''' IDs of HVC frames. '''
    
    # HVC control frame
    CONTROL = 0x30
    
    # HVC status frame
    STATUS  = 0x31
    
    # HVC Diag Frame Send
    DIAGSEND = 0x3C
    
    # HVC Diag Frame Recive
    DIAGREC = 0x3D


class ElmHeader():
    ''' Elements of a HCV Frame's header. '''
    
    #TIMESTAMP   = 'Timestamp'
    PCSYNC      = 'PcSync'  #Status = 0x55, Control = 0xAA
    ID          = 'ID'
    DATALENGTH  = 'DataLength'


class ElmControl():
    ''' Elements of a HCV Controll Frame '''
    
    INIT_CURRENT_POS        = 'init_current_pos'
    NEW_POS                 = 'new_pos'
    SPEED                   = 'speed'
    OP_MODE                 = 'op_mode'
    ENABLE                  = 'enable'
    ENABLE_STALL_DETECTION  = 'enable_stall_detection'
    DIRECTION               = 'direction'


class ElmStatus():
    ''' Elements of a HCV Status Frame  '''
    
    CURRENT_POS         = 'current_pos'
    LIN_ERROR           = 'lin_error'
    STALL_DETECTED      = 'stall_detected'
    OVER_TEMPERATURE    = 'over_temperature'
    OVER_CURRENT        = 'over_current'
    HVC_STATUS          = 'hvc_status'
    BVDD                = 'bvdd'
    TJ                  = 'tj'
    CURRENT_SPEED       = 'current_speed'

class ElmDiag():
    ''' Elements of HVC Diag Frame '''
    
    NAD = 'nad'
    PCI = 'pci'
    SID = 'sid'
    D1 = 'd1'
    D2 = 'd2'
    D3 = 'd3'
    D4 = 'd4'
    D5 = 'd5'

# Header bitstring format of HCV frame 

#BBR cng for timestamp uint:32={}
_HVC_HEADER_FORMAT = \
    "\
        uint:8={},  \
        uint:8={},   \
        uint:8={}    \
    ".format(ElmHeader.PCSYNC, ElmHeader.ID, ElmHeader.DATALENGTH)


# Bitstring format of HCV Control Frame 
_HVC_CONTROL_FORMAT = \
    "\
        intle:16={}, \
        intle:16={}, \
        uintle:8={}, \
        pad:8,       \
        pad:3,       \
        uint:1={},   \
        uint:1={},   \
        uint:1={},   \
        uint:2={}    \
    ".format(ElmControl.INIT_CURRENT_POS, ElmControl.NEW_POS,
             ElmControl.SPEED, ElmControl.OP_MODE, ElmControl.ENABLE, 
             ElmControl.ENABLE_STALL_DETECTION, ElmControl.DIRECTION
            )

# Bitstring format of HCV Status Frame 
_HVC_STATUS_FORMAT = \
    "\
        intle:16={}, \
        pad:2,       \
        uint:1={},   \
        uint:1={},   \
        uint:1={},   \
        uint:1={},   \
        uint:2={},   \
        uint:8={},   \
        uint:8={},   \
        uint:8={}    \
    ".format(ElmStatus.CURRENT_POS, ElmStatus.LIN_ERROR, ElmStatus.STALL_DETECTED, 
             ElmStatus.OVER_TEMPERATURE, ElmStatus.OVER_CURRENT, ElmStatus.HVC_STATUS, 
             ElmStatus.BVDD, ElmStatus.TJ, ElmStatus.CURRENT_SPEED
            )

# Bitstring format of HCV Diag Frame 
_HVC_DIAGNOSTIC_FORMAT = \
    "\
        uint:8={},       \
        uint:8={},       \
        uint:8={},       \
        uint:8={},       \
        uint:8={},       \
        uint:8={},       \
        uint:8={},       \
        uint:8={}        \
    ".format(ElmDiag.NAD, ElmDiag.PCI, ElmDiag.SID, ElmDiag.D1, ElmDiag.D2, ElmDiag.D3, ElmDiag.D4, ElmDiag.D5)

class HVC_Header(dict):
    ''' HCV Header representation. '''
    
    def __init__(self, pcSync, _id, dataLen): #timeStamp
        super().__init__()
        
        self._format = _HVC_HEADER_FORMAT
        
        # ElmHeader data
        self[ElmHeader.PCSYNC] = pcSync #timeStamp
        self[ElmHeader.ID] = _id
        self[ElmHeader.DATALENGTH] = dataLen
        #self[ElmHeader.TIMESTAMP] = timeStamp
        
    def toBytearray(self):
        ''' Convert HCV frame to byte array'''
        self._frame = bytearray(bitstring.pack(self._format, **self).bytes)
        return self._frame
        

class HVC_Frame(dict):
    ''' Represents a generic HCV frame. Offers operations for conversion of frames.'''   
    
    def __init__(self, header, payloadFormat):
        ''' 
            - header: HCV_Header
            - payloadFormat: Bitstring format specification of payload data.
        '''
        super().__init__()
                
        self._header  = header
        self._format  = header._format + ','+  payloadFormat
        
        #Frame as bytearray
        self._frame   = None 
        
        self.update(header)
    
    
    def toBytearray(self):
        ''' Convert HCV frame to byte array'''
        self._frame = bytearray(bitstring.pack(self._format, **self).bytes)
        return self._frame
    
    def fromBytearray(self, frame=None):                     
        ''' Create HCV frame from a bytearray frame. '''
        if not frame:
            frame = self._frame
        
        fmt = self._format
        
        streamData = bitstring.BitStream(self._frame) 
        
        # List of format strings
        fmtStr = fmt.split(',')
        
        # Get all keywords from bitstring formatString 
        keys = [kw.split('=')[1].strip() for kw in fmtStr if len(kw.split('=')) > 1]
        
        # Create dictionary from keys and stream data
        frameDict = dict(zip(keys, streamData.unpack(fmt)))
        
        # Assign items to self
        self.update(frameDict)
        
        return frameDict

        
class HVC_ControlFrame(HVC_Frame):
    ''' Represents a HCV control frame. '''
        
    def __init__(self):
        self._header = HVC_Header(0xAA, FrameID.CONTROL, 7)      #, 0       
        super().__init__(self._header, _HVC_CONTROL_FORMAT)

        #Init Frame default values
        self[ElmControl.INIT_CURRENT_POS] = None
        self[ElmControl.NEW_POS] = None
        self[ElmControl.SPEED] = None
        self[ElmControl.OP_MODE] = None
        self[ElmControl.ENABLE] = None
        self[ElmControl.ENABLE_STALL_DETECTION] = None
        self[ElmControl.DIRECTION] = None
        
    @property
    def initPosition(self):
        return self[ElmControl.INIT_CURRENT_POS]
        
    @initPosition.setter
    def initPosition(self, pos):
        self[ElmControl.INIT_CURRENT_POS] = pos
    
    @property
    def newPosition(self):
        return self[ElmControl.NEW_POS]
    
    @newPosition.setter
    def newPosition(self, pos):
        self[ElmControl.NEW_POS] = pos
    
    @property
    def speed(self):
        return self[ElmControl.SPEED]
    
    @speed.setter
    def speed(self, speed):
        self[ElmControl.SPEED] = speed
    
    @property
    def opMode(self):
        return self[ElmControl.OP_MODE]
    
    @opMode.setter
    def opMode(self, opMode):
        self[ElmControl.OP_MODE] = opMode
    
    @property
    def motorEnabled(self):
        return self[ElmControl.ENABLE]
    
    @motorEnabled.setter
    def motorEnabled(self, isEnabled):
        self[ElmControl.ENABLE] = isEnabled
    
    @property
    def isStallDetection(self):
        return self[ElmControl.ENABLE_STALL_DETECTION]
    
    @isStallDetection.setter
    def isStallDetection(self, isEnabled):
        self[ElmControl.ENABLE_STALL_DETECTION] = isEnabled
    
    @property
    def direction(self):
        return self[ElmControl.DIRECTION]
    
    @direction.setter
    def direction(self, direction):
        self[ElmControl.DIRECTION] = direction

  
class HVC_StatusFrame(HVC_Frame):
    ''' Represents a HCV Status frame. '''
                
    def __init__(self, frame=None):
        self._header = HVC_Header(0x55, FrameID.STATUS,  6) #, 0
        super().__init__(self._header, _HVC_STATUS_FORMAT)
        
        self._frame = frame
        
        if self._frame:
            # Assign ctrlFrame data to self items
            self.fromBytearray()
       
    
    @property  
    def currentPos(self):
        return self[ElmStatus.CURRENT_POS]
    
    @property
    def currentSpeed(self):
        return self[ElmStatus.CURRENT_SPEED]
        
    @property
    def isOverCurrent(self):
        return self[ElmStatus.OVER_CURRENT]
        
    @property
    def hvcStatus(self):
        return self[ElmStatus.HVC_STATUS]    
    
    @property
    def bvdd(self):
        return self[ElmStatus.BVDD]
    
    @property
    def tj(self):
        return self[ElmStatus.TJ]
    
    @property
    def isStallDetected(self):
        return self[ElmStatus.STALL_DETECTED]
    
    @property
    def isOverTemperature(self):
        return self[ElmStatus.OVER_TEMPERATURE]
    
    @property
    def isLinError(self):
        return self[ElmStatus.LIN_ERROR]
    
   
class HVC_DiagSendFrame(HVC_Frame):
    ''' Represents a HCV Diag frame to send. '''
                
    def __init__(self):
        self._header = HVC_Header(0xAA, FrameID.DIAGSEND,  8) #, 0
        super().__init__(self._header, _HVC_DIAGNOSTIC_FORMAT)
        
        #Init Frame default values
        self[ElmDiag.NAD] = None
        self[ElmDiag.PCI] = None
        self[ElmDiag.SID] = None
        self[ElmDiag.D1] = None
        self[ElmDiag.D2] = None
        self[ElmDiag.D3] = None
        self[ElmDiag.D4] = None
        self[ElmDiag.D5] = None
            
    @property
    def nad(self):
        return self[ElmDiag.NAD]
        
    @nad.setter
    def nad(self, nad):
        self[ElmDiag.NAD] = nad
    
    @property
    def pci(self):
        return self[ElmDiag.PCI]
    
    @pci.setter
    def pci(self, pci):
        self[ElmDiag.PCI] = pci
    
    @property
    def sid(self):
        return self[ElmDiag.SID]
    
    @sid.setter
    def sid(self, sid):
        self[ElmDiag.SID] = sid
    
    @property
    def d1(self):
        return self[ElmDiag.D1]
    
    @d1.setter
    def d1(self, data):
        self[ElmDiag.D1] = data
    
    @property
    def d2(self):
        return self[ElmDiag.D2]
    
    @d2.setter
    def d2(self, data):
        self[ElmDiag.D2] = data
        
    @property
    def d3(self):
        return self[ElmDiag.D3]
    
    @d3.setter
    def d3(self, data):
        self[ElmDiag.D3] = data

    @property
    def d4(self):
        return self[ElmDiag.D4]
    
    @d4.setter
    def d4(self, data):
        self[ElmDiag.D4] = data
        
    @property
    def d5(self):
        return self[ElmDiag.D5]
    
    @d5.setter
    def d5(self, data):
        self[ElmDiag.D5] = data


class HVC_DiagRecFrame(HVC_Frame):
    ''' Represents a rcived HCV Diag frame. '''
                
    def __init__(self, frame=None):
        self._header = HVC_Header(0x55, FrameID.DIAGREC,  8) #, 0
        super().__init__(self._header, _HVC_DIAGNOSTIC_FORMAT)
        
        self._frame = frame
        
        if self._frame:
            # Assign ctrlFrame data to self items
            self.fromBytearray()
            
    @property
    def nad(self):
        return self[ElmDiag.NAD]
    
    @property
    def pci(self):
        return self[ElmDiag.PCI]
    
    @property
    def sid(self):
        return self[ElmDiag.SID]
    
    @property
    def d1(self):
        return self[ElmDiag.D1]
    
    @property
    def d2(self):
        return self[ElmDiag.D2]
        
    @property
    def d3(self):
        return self[ElmDiag.D3]
    
    @property
    def d4(self):
        return self[ElmDiag.D4]
    
    @property
    def d5(self):
        return self[ElmDiag.D5]
    



class Procedure(object):
    ''' Procedures that are remote callable an LIN-Adapater hardware. '''
    
    LIN_SEND_MSG = "LIN_Send({})"
    LIN_GET_STATUS = "LIN_GetStatus()"

class LINAdapterCOMError(Exception):
    pass

class LINAdapter(object):
    ''' 
        Offers operations for remote procedure call (RPC) on LIN-Adapter.
    '''
#edit here    
    def __init__(self ):
        self.linAdapterBoard = None
        self._isConnected = False
        
    def __del__(self):
        if self._isConnected:
            self.disconnect()
    
    def connect(self, comPort=None, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, timeoutval=1): #user='micro', password='python',
        ''' Connect with LIN adapter. '''
        
        self.linAdapterBoard = serial.Serial(comPort, baudrate, bytesize, parity, timeout=timeoutval) #user, password,
        
        if self.linAdapterBoard.is_open == True:
            self._isConnected = True
        else:
            print('Not connected')

    def disconnect(self):
        ''' Disconnect from LIN Adapter. '''
        self.linAdapterBoard.close()
        self._isConnected = False
        
    @property
    def isConnected(self):
        ''' returns it's connection state'''
        return self._isConnected

    def callLinSendMsg(self, hvcCtrlFrame):
        ''' Calls SendMsg procedure on LIN Adapter.
            - hcvFrame: HCV_ControlFrame with valid control data.
            Returns HCV_StatusFrame with current status data.
            If not connected returns None
        '''
        if self._isConnected:
            #Send Msg ID 0x30 to LinAdapter
            frame = hvcCtrlFrame.toBytearray()
            #Format of frame = bytearray(b'data')
            self.linAdapterBoard.write(frame)
            #Receive same Msg from LinAdapter
            framerec = self.linAdapterBoard.read(3 + hvcCtrlFrame['DataLength']) #Payload 7 + Sync, ID and len
            #received frame is in bytes format for compare we need to convert it to a bytearray()
            framerecbytearray = bytearray(framerec)
            
            tbol = np.array_equal(frame, framerecbytearray) #returns true if same, false if different
            if (False == tbol):
                print('no answer from Comport')
                return False

            return True
        else:
            return False
    
    def callGetStatus(self, hvcReadFrame):
        ''' Calls GetStatus procedure on LIN Adapter.
            Returns HCV_StatusFrame with current status data,
            if not connected returns None
        '''
        if self._isConnected:
            returntype = type(hvcReadFrame) 
            getFrame = hvcReadFrame._header.toBytearray()
            self.linAdapterBoard.write(getFrame) #ToDo modular design
            frame = self.linAdapterBoard.read(3 + hvcReadFrame['DataLength']) #Payload 6 + Sync, ID and len 
    
            return returntype(frame)
        else:
            return None
    
##hier editieren ende    
    

if __name__ == '__main__':
    import unittest
    
    class TestHVC_ControlFrame(unittest.TestCase):
        ''' Unit test of HCV_ControlFrame class. 
        '''
        
        def test_createFrame(self):
            ctrlFrame = HVC_ControlFrame()
            ctrlFrame.initPosition = 16000
            ctrlFrame.newPosition = 8000
            ctrlFrame.speed = 40
            ctrlFrame.opMode = OpMode.POSITION_CTRL
            ctrlFrame.motorEnabled = True
            ctrlFrame.isStallDetection = True
            ctrlFrame.direction = Direction.STOP
            
            #Created frame
            frame = ctrlFrame.toBytearray()
            
            #Expected frame
            expFrame = bytearray([0, 0, 0, 0, FrameID.CONTROL, 7, 128, 62, 64, 31, 40, 0, 12])
            
            #Check that created frame is as expected
            assert all([expected == actual for expected, actual in zip(expFrame, frame)])
            
        def test_unpackFrame(self):
            ctrlFrame = HVC_ControlFrame()
            ctrlFrame.initPosition = 16000
            ctrlFrame.newPosition = 8000
            ctrlFrame.speed = 40
            ctrlFrame.opMode = OpMode.POSITION_CTRL
            ctrlFrame.motorEnabled = True
            ctrlFrame.isStallDetection = True
            ctrlFrame.direction = Direction.STOP
            
            #Create bytearray frame 
            baFrame = ctrlFrame.toBytearray()
            
            #Get unpacked dict
            frameDict1 = ctrlFrame.fromBytearray()
            
            #Unpack dict from frame in bytearray format
            frameDict2 = ctrlFrame.fromBytearray(baFrame)

            #Check both are equal
            self.assertDictEqual(frameDict1, frameDict2)
            
    class Test_HVC_StatusFrame(unittest.TestCase):
        ''' Unit test of HCV_StatusFrame class.
        '''
        
        def test_createFrame(self):
            
            currentPos = 2345
            hvcStatus = HVC_Status.HVC_STATUS_ERROR
            isOverCurrent = HVC_Status.OVER_CURRENT
            isOverTemperature = HVC_Status.NO_OVER_TEMEPERATURE
            isStallDetected = HVC_Status.NO_STALL_DETECTED
            isLinError = HVC_Status.NO_LIN_ERROR
            bvdd = 12
            tj = 76
            currentSpeed = 142
            
            #Create binary frame
            timeStamp = 235
            frameLen = 6
            currentPosMSB = currentPos & 0xFF
            currentPosLSB =  currentPos >> 8
            
            #Create status byte
            statusByte = 0x00
            statusByte |= hvcStatus
            statusByte |= isOverCurrent << 2
            statusByte |= isOverTemperature << 3
            statusByte |= isStallDetected << 4
            statusByte |= isLinError << 5

            #Create byte frame
            expFrame = bytearray([timeStamp, FrameID.STATUS, frameLen, currentPosMSB, currentPosLSB, statusByte, bvdd, tj, currentSpeed])
            expFrame = expFrame.__repr__()
            expFrame = bytes(expFrame, 'utf-8')
            #print(expFrame, type(expFrame))
            #print([str(v) for v in expFrame ])
            
            #Create StatusFrame
            statusFrame = HVC_StatusFrame(expFrame)
            #print(statusFrame)
            
            #Check frame data is equal to binary frame data
            self.assertEqual(statusFrame.currentPos, currentPos, "")
            self.assertEqual(statusFrame.hvcStatus, hvcStatus, "")
            self.assertEqual(statusFrame.isOverCurrent, isOverCurrent, "")
            self.assertEqual(statusFrame.isOverTemperature, isOverTemperature, "")
            self.assertEqual(statusFrame.isStallDetected, isStallDetected, "")
            self.assertEqual(statusFrame.isLinError, isLinError, "")
            self.assertEqual(statusFrame.bvdd, bvdd, "")
            self.assertEqual(statusFrame.tj, tj, "")
            self.assertEqual(statusFrame.currentSpeed, currentSpeed, "")

            
        def test_createFrameFromByteArray(self):
            pass
        
        def test_FrameToByteArray(self):
            pass
        
        
    
    
    unittest.main()