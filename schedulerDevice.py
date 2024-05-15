import schedule
import Device

schedulerDevices = dict()

def addSchedulerDevice(schedulerID, time, action, deviceID):
  hour = int(time) // 60
  minute = int(time) % 60 
  if hour < 10:
    hour = f'0{hour}'
  if minute < 10:
    minute = f'0{minute}'
  
  # print(f'{hour}:{minute}')
  if schedulerID in schedulerDevices.keys():
    # delete old scheduler
    schedule.cancel_job(schedulerDevices[schedulerID])
    schedulerDevices[schedulerID] = schedule.every().day.at(f'{hour}:{minute}').do(
      Device.controlDevice, deviceID=deviceID, value=action)
    print(f"Update scheduler {schedulerID} at {hour}:{minute} with action {action}")
  else:
    schedulerDevices[schedulerID] = schedule.every().day.at(f'{hour}:{minute}').do(
      Device.controlDevice, deviceID=deviceID, value=action)
    print(f"Add scheduler {schedulerID} at {hour}:{minute} with action {action}")

def deleteSchedulerDevice(schedulerID):
  schedule.cancel_job(schedulerDevices[f'{schedulerID}!!!'])
  schedule.cancel_job(schedulerDevices[f'{schedulerID}###'])
  print(f"Delete scheduler {schedulerID}")

def showSchedulerDevices():
  for scheduler in schedulerDevices:
    print(f"Scheduler: {scheduler}, {schedulerDevices[scheduler]}")
