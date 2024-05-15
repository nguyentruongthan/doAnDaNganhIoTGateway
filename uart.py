import serial.tools.list_ports
from serial import SerialException
import handleData
import constants
message = ""
ser = None
def readSerial():
  global message
  global ser
  if(ser == None): return
  try:
    #	Get the number of bytes in the input buffer
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
      
      #read all data in serial and assign to mess
      message = message + ser.read(bytesToRead).decode("utf-8")
      #Format of data is "!<content>#" 
      while ("#" in message) and ("!" in message):
        start = message.find("!")
        end = message.find("#")
        # processData(mess[start:end + 1], ser)
        # print(f"From UART: {message[start:end + 1]}")
        handleData.processUartData(message[start:end + 1])
        if (end == len(message)):
            message = ""
        else:
            message = message[end+1:]

  except SerialException:
    print(f"Disconnect from {ser}")
    ser = None
    
def sendData(data):
  global ser
  if(ser is None): return
  ser.write(data.encode())
  print(f"To uart: {data}")


def getPort():
  global message
  global ser
  
  if(ser != None): return
  ports = serial.tools.list_ports.comports()
  for port in ports:
    strPort = str(port)
    if "USB-SERIAL" in strPort:
      splitPort = strPort.split(" ")
      if(constants.COMPORT == splitPort[0]):
        print(f"Detected new port {constants.COMPORT}")
        #TODO 
        ser = serial.Serial(port = constants.COMPORT, baudrate = 115200)
        print(ser)