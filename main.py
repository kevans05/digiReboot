import platform    # For getting the operating system name
import subprocess  # For executing a shell command
import sched
import time
import csv
from datetime import datetime
import collections
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
RELAIS_1_GPIO = 17
GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO Assign mode

s = sched.scheduler(time.time, time.sleep)

def ping(host):
    param = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', param, '1', host]
    return subprocess.call(command) == 0

def main(sc, ringbuffer):
    local_ping = ping("192.168.1.1")
    external_ping = ping("google.ca")

    ringbuffer.append(local_ping+external_ping)

    if (sum(ringbuffer) / len(ringbuffer)) <= 1.0:
        myCsvRow = {"datetime": datetime.now().isoformat(), "external_ping": external_ping, "local_ping": local_ping,
                    "reboot": True}
        GPIO.output(RELAIS_1_GPIO, GPIO.LOW) # out
        time.sleep(12)
        GPIO.output(RELAIS_1_GPIO, GPIO.HIGH)  # on
    else:
        myCsvRow = {"datetime":datetime.now().isoformat(),"external_ping":external_ping,"local_ping":local_ping,
                    "reboot":False}
    with open('event.csv', 'a') as f_object:
        dictwriter_object = csv.DictWriter(f_object, fieldnames=list(myCsvRow))
        dictwriter_object.writerow(myCsvRow)
        f_object.close()
    s.enter(150, 1, main, (sc,ringbuffer))


ringbuffer = collections.deque(maxlen=10)
s.enter(150, 1, main, (s,ringbuffer))
s.run()
