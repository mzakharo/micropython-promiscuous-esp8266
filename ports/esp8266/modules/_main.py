import gc
import urtc
from machine import I2C, Pin, RTC
i2c = I2C(scl=Pin(5), sda=Pin(4))
rtc = urtc.PCF8523(i2c)

'''
if rtc.lost_power():
    print("WARNING: neeed to reset RTC")
if rtc.battery_low():
    print("WARNING: RTC battery low")
'''
rtc0 = RTC()
rtc0.datetime(tuple(rtc.datetime()))
del rtc, rtc0, i2c, I2C, Pin, RTC, urtc
gc.collect()
del gc

import mon
mon.enable(schedule=True)
