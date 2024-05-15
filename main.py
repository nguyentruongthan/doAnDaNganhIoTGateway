import uart 
import time
import MQTTClient
import schedule
import sys
import constants

class Task:
  def __init__(self, delay, period, func, args = None):
    self.delay = delay
    self.func = func
    self.period = period
    self.run_me = 0
    self.args = args

class Tasks:
  def __init__(self):
    self.tasks = list()

  def add_task(self, task):
    self.tasks.append(task)

  def remove_task(self, task):
    self.tasks.remove(task)

  def update(self):
    for task in self.tasks:
      if(task.delay >= 0):
        task.delay -= 1
        if(task.delay <= 0):
          task.delay = task.period
          task.run_me = 1

  def dispatch(self):
    for task in self.tasks:
      if(task.run_me):
        #reset flag run_me
        task.run_me = 0
        #active function of task
        if(task.args != None):
          task.func(task.args)
        else:
          task.func()
        
        if(task.period == 0):
          self.remove_task(task)
        else:
          task.delay = task.period

tasks = Tasks()
read_uart_task = Task(delay = 50, period = 1, func = uart.readSerial)
connect_uart_task = Task(delay = 50, period = 5, func = uart.getPort)

if __name__ == "__main__":
  if(len(sys.argv) != 3):
    print("Please enter feed name and port")
    exit()
  constants.FEED_NAME = sys.argv[1]
  constants.COMPORT = sys.argv[2]
  
  tasks.add_task(connect_uart_task)
  tasks.add_task(read_uart_task)
  
  time.sleep(1) #time unit is 100ms
  #init device
  MQTTClient.mqttClientHelper.publish(f"nguyentruongthan/feeds/{constants.FEED_NAME}", "4")
  time.sleep(1)
  #init scheduler
  MQTTClient.mqttClientHelper.publish(f"nguyentruongthan/feeds/{constants.FEED_NAME}", "7")
  time.sleep(1)
  #init isAuto
  MQTTClient.mqttClientHelper.publish(f"nguyentruongthan/feeds/{constants.FEED_NAME}", "13")
  time.sleep(1)
  while 1:
    tasks.update()
    tasks.dispatch()
    schedule.run_pending()
    time.sleep(0.01) #time unit is 10ms