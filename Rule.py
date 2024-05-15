import constants
import Device
isAuto = 0
class OutputRule:
  def __init__(self, outputRuleID, outputID, action):
    self.outputRuleID = outputRuleID
    self.outputID = outputID
    self.action = action
    self.sensorRules = dict()
class SensorRule:
  def __init__(self, sensorRuleID, sensorID, condition, threshold):
    self.sensorRuleID = sensorRuleID
    self.sensorID = sensorID
    self.condition = condition
    self.threshold = threshold

outputRules = dict()

def addRule(ruleJson):
  outputRule = ruleJson['outputRule']
  sensorRules = ruleJson['sensorRules']
  
  outputRules[outputRule['_id']] = OutputRule(
    outputRuleID = outputRule['_id'],
    outputID = outputRule['outputID'],
    action = outputRule['action']
  )

  outputRule:OutputRule = outputRules[outputRule['_id']]
  for sensorRuleJson in sensorRules:
    sensorRule:SensorRule = SensorRule(
      sensorRuleID = sensorRuleJson['_id'],
      sensorID = sensorRuleJson['sensorID'],
      condition = sensorRuleJson['condition'],
      threshold = sensorRuleJson['threshold']
    )
    outputRule.sensorRules[sensorRuleJson['_id']] = sensorRule
    print(f"Add sensor rule type {Device.devices[sensorRule.sensorID].type}: {sensorRule.condition} {sensorRule.threshold} to output rule: {Device.devices[outputRule.outputID].pin}")
  

def checkSensorRule(sensorRule: SensorRule):
  device:Device.Device = Device.devices[sensorRule.sensorID]
  value = float(device.value)
  
  if(sensorRule.condition == "<"):
    if(value < float(sensorRule.threshold)):
      return True
  elif(sensorRule.condition == ">"):
    if(value >= float(sensorRule.threshold)):
      return True
  return False

def checkOutputRule(outputRule: OutputRule):
  sensorRules: SensorRule = outputRule.sensorRules
  for sensorRuleID in sensorRules:
    sensorRule: SensorRule = sensorRules[sensorRuleID]
    if checkSensorRule(sensorRule) == False:
      return False
  return True


def checkRule():
  if(isAuto == 0):
    return
  for outputRuleID in outputRules.keys():
    outputRule:OutputRule = outputRules[outputRuleID]
    action = outputRule.action
    if checkOutputRule(outputRule):
      Device.controlDevice(outputRule.outputID, '1' if action == "1" else '0')
    else:
      Device.controlDevice(outputRule.outputID, '0' if action == "1" else '1')


def deleteRule(outputRuleID):
  if outputRuleID in outputRules.keys():
    outputRuleDelete:OutputRule = outputRules.pop(outputRuleID)
    print(f'Delete rule: {Device.devices[outputRuleDelete.outputID].pin}')