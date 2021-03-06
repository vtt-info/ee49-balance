from machine import Pin, I2C, Timer
from board import *
from bno055 import BNO055 # IMU

from drv8833 import DRV8833 # your implementation
from motor import PIDMotor # your implementation
from encoder import Encoder # your implementation, don't forget clear_count
from balance import Balance

import gc # for garbage collection methods

# Setup motors
########## Check Pin Numbers! ##########
# Change pin numbers here to match yours or rewire your robot
leftEnc = Encoder(34, 39, 2)
leftM = DRV8833(19, 16)

rightEnc = Encoder(36, 4, 1)
rightM = DRV8833(17, 21)
########## Check Pin Numbers! ##########

pidL = PIDMotor(leftM, leftEnc)
pidR = PIDMotor(rightM, rightEnc)

# setup IMU
i2c = I2C(0, sda=23, scl=22, freq=13000)
imu = BNO055(i2c)

# status LED
led = Pin(LED, mode=Pin.OUT)

dt = 0.02
ticks = 0
sec = 0
old_sec = 0
loopReady = False

def tick(timer):
    # every tick
    global loopReady, ticks, dt, sec
    loopReady = True # next loop is ready to go
    ticks += 1

    # every second
    if ticks == int(1/dt):
        sec += 1
        ticks = 0

# start a timer for the main loop
timer = Timer(0)
timer.init(period=int(dt * 1000), mode=Timer.PERIODIC, callback=tick)

# turn off garbage collection for deterministic loop times
# requires gc.collect() to be called periodically, without it
# MemoryErrors will occur after some time
# the collect is done inside balancer.do_balance()
gc.disable()

balancer = Balance(pidL, pidR, imu, dt)
balancer.set_balance_pi(219, 45)

# use an infinite loop with flag so that the callback is short
# in case code inside takes too long
# instead of directly calling everything needed in the callback
while (True):
    if loopReady:
        loopReady = False
        led(sec % 2) # status LED, toggle every second

        if (sec != old_sec):
            old_sec = sec
            balancer.increment_count()

        balancer.do_balance()
