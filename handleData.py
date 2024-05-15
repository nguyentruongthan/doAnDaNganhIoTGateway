import constants
import MQTTClient
import uart
import Device
import json
import schedulerDevice
import Rule
def processUartData(data):
  #replace charactor ! and # at start and end of data
  data = data.replace("!", "")
  data = data.replace("#", "")

  #spilit data to array with spilt charactor is ":" 
  splitMessage = data.split(":")
  header = splitMessage[0]

  if(header == str(constants.HEADER_SENSOR_VALUE)):
    #receive sensor value
    type = splitMessage[1]
    pin = splitMessage[2]
    value = splitMessage[3]

    if(type == str(constants.TYPE_LIGHT_SENSOR)):
      print(f"Light: {value}")
    elif(type == str(constants.TYPE_SOIL_SENSOR)):
      print(f"HumiSolid: {value}")
    elif(type == str(constants.TYPE_HUMIAIR_SENSOR)):
      print(f"HumiAir: {value}")
    elif(type == str(constants.TYPE_TEMP_SENSOR)):
      print(f"Temp: {value}")
    # else:
    #   print(f"Type sensor value error")
    #   return
    
    # find deviceID by pin
    device:Device.Device = Device.findDeviceByPinAndType(pin, type)
    #update new value for device
    if(device == None):
      return
    
    device.value = value
    # check condition of rule
    if(type == str(constants.TYPE_TEMP_SENSOR)):
      Rule.checkRule()
        
    message = f"{constants.HEADER_SENSOR_VALUE}:{device.deviceID}:{value}"
    MQTTClient.mqttClientHelper.publish(f"nguyentruongthan/feeds/{constants.FEED_NAME}", message)
  

def processMQTTData(data):
  
  header = data[0]
  if(len(data) == 2):
    header = data[0:2]
  if(len(data) > 2):
    if(data[2] == ":"):
      header = data[0:2]
  
  if(header == str(constants.HEADER_CONTROL_DEVICE)):
    splitMessage = data.split(":")
    #<HEADER_CONTROL_DEVICE>:<deviceID>:<value>:<ack>
    
    deviceID = splitMessage[1]
    value = splitMessage[2]
    ack = splitMessage[3]
    Device.controlDevice(
      deviceID = deviceID,
      value = value,
      isScheduler = False
    )
    MQTTClient.mqttClientHelper.publish(
      f"nguyentruongthan/feeds/{constants.FEED_NAME}", 
      f"{constants.HEADER_ACK}:{ack}")
  elif(header == str(constants.HEADER_CREATE)):
    devices = json.loads(data[2:])
    if(data[2] == '['):
      #many devices
      for device in devices:  
        Device.devices[device['_id']] = Device.Device(
          deviceID = device['_id'],
          pin = device['pin'],
          type = device['type'],
          value = '0'
        )
        if(device['type'] == str(constants.TYPE_DIGITAL_OUTPUT)):
          # send mqtt message to get latest value of this device
          MQTTClient.mqttClientHelper.publish(
            f"nguyentruongthan/feeds/{constants.FEED_NAME}", 
            f"{constants.HEADER_GET_LATEST_VALUE}:{device['_id']}")
          # send mqtt message to get rule of this device
          MQTTClient.mqttClientHelper.publish(
            f"nguyentruongthan/feeds/{constants.FEED_NAME}", 
            f"{constants.HEADER_GET_RULE}:{device['_id']}")

    else:
      #one device
      device = devices
      if(device['type'] == str(constants.TYPE_DIGITAL_OUTPUT)):
        Device.devices[device['_id']] = Device.Device(
          deviceID = device['_id'],
          pin = device['pin'],
          type = device['type'],
          value = '0'
        )
    Device.showDevices()
  elif(header == str(constants.HEADER_DELETE)):
    deviceID = data[2:]
    print(f"Delete device: {deviceID}")
    Device.devices.pop(deviceID)
    Device.showDevices()
  elif(header == str(constants.HEADER_CREATE_SCHEDULER)):
    schedulers = json.loads(data[2:])
    for scheduler in schedulers:
      schedulerDevice.addSchedulerDevice(
        schedulerID = f"{scheduler['_id']}!!!",
        time = scheduler['start_time'],
        action = '1' if scheduler['action'] == "1" else '0',
        deviceID = scheduler['outputID']
      )
      schedulerDevice.addSchedulerDevice(
        schedulerID = f"{scheduler['_id']}###",
        time = scheduler['stop_time'],
        action = '0' if scheduler['action'] == "1" else '1',
        deviceID = scheduler['outputID']
      )
      
    # schedulerDevice.showSchedulerDevices()
  elif(header == str(constants.HEADER_DELETE_SCHEDULER)):
    schedulerID = data[2:]
    schedulerDevice.deleteSchedulerDevice(schedulerID)
  elif(header == str(constants.HEADER_LATEST_VALUE)):
    #message format: <HEADER_LATEST_VALUE>:<deviceID>:<value>
    splitMessage = data.split(":")
    deviceID = splitMessage[1]
    value = splitMessage[2]
    Device.controlDevice(
      deviceID = deviceID,
      value = value,
      isScheduler = False
    )
  elif(header == str(constants.HEADER_CREATE_RULE)):
    #message format: <HEADER_CREATE_RULE>:[json]
    rules = json.loads(data[3:])
    for rule in rules:
      # print(rule)
      Rule.addRule(rule)
  elif(header == str(constants.HEADER_CREATE_IS_AUTO)):
    isAutoRecv = data.split(":")[1]
    print('isAutoRecv: ', isAutoRecv)
    Rule.isAuto = int(isAutoRecv)
  elif(header == str(constants.HEADER_DELETE_RULE)):
    outputRuleID = data[3:]
    Rule.deleteRule(outputRuleID)