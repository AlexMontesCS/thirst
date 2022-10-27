from ClassyScraper import *
import threading 
import json


def update_total():
  total = get_total()
  f = open("total.json", "w")
  f.write(json.dumps(total))
  f.close()

def setInterval(func,time):
  e = threading.Event()
  while not e.wait(time):
      func()

print("Started the clock!")
setInterval(update_total, 300)