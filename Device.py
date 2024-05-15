import MQTTClient
import constants
import uart
class Device:
  def __init__(self, deviceID, pin, type, value):
    self.deviceID = deviceID
    self.pin = pin
    self.type = type
    self.value = value

#deviceID: Device
devices = dict()

def showDevices():
  for deviceID in devices:
    print(f"Device: {deviceID}, pin:{devices[deviceID].pin}, type:{devices[deviceID].type}, value:{devices[deviceID].value}")

def controlDevice(deviceID, value, isScheduler = True):
  #update value of device
  devices[deviceID].value = value
  # control device
  pin = devices[deviceID].pin
  # send data to uart
  print(f"Control device: {pin} with value: {value}")
  message = f"!{constants.HEADER_CONTROL_DEVICE}:{pin}:{value}#"
  uart.sendData(message)
  # send data to mqtt for update UI
  if isScheduler:
    MQTTClient.mqttClientHelper.publish(
      f'nguyentruongthan/feeds/{constants.FEED_NAME}', 
      f"{constants.HEADER_SENSOR_VALUE}:{deviceID}:{value}"
    )

def findDeviceByPinAndType(pin, type):
  for deviceID in devices:
    if devices[deviceID].pin == pin and devices[deviceID].type == type:
      return devices[deviceID]
  return None