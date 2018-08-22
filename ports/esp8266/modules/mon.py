import network
import utime as time
import os
from micropython import const, schedule
import machine
rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

#rtc.datetime((2018,8,22,2,11,18,0,0))

f = None

def disable():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.promiscuous_disable()
    global f
    ret = False
    if f is not None:
        f.close()
        f = None
        ret = True
    print("Promiscuous mode disabled")
    return ret


MIN_15 = const(15*60) #guard to allow downloading files from internal flash
MIN_30 = const(30*60) #guard to allow downloading files from internal flash
TIMER_PERIOD=MIN_30
boot_time = time.time()

def sleep(seconds):
    if ((time.time() - boot_time) > MIN_15 or machine.reset_cause() == machine.DEEPSLEEP_RESET):
        if disable() is True: #only sleep if previously enabled
            rtc.alarm(rtc.ALARM0, seconds * 1000)
            print('put the device to sleep')
            machine.deepsleep()

def mac_to_str(a):
    return ("%02x:%02x:%02x:%02x:%02x:%02x" % (((a[0])), ((a[1])), ((a[2])),
                                               ((a[3])), ((a[4])), (a[5])))

def get_whm():
    t = time.localtime(time.time())
    return (t[6],t[3],t[4])

macs = {}

def monitor(mac_in):
    mac = mac_to_str(mac_in)
    if mac not in macs:
        if not mac_in[0] & 0x2:
            print('global')
            macs[mac] = None
        else:
            print('local')
        whm = get_whm()
        s ="{}-{}\n".format(whm,mac)
        print(s)
        f.write(s)
        sleep(MIN_15)

def sleep_schedule(whm):
    wkd,hour,_ = whm
    if (hour >= 6 and hour <=20) and (wkd == 5 or wkd == 6 or hour > 16):
        return False
    return True #sleep sleep sleep


def timer_schedule(self=None):
    whm = get_whm()
    print('{}-timer'.format(whm))
    if sleep_schedule(whm):
        sleep(MIN_30)

def enable(ch=6, schedule=True):
    print("Promiscuous mode enable")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.promiscuous_disable()
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if.active(True)
    print("Channel {}".format(sta_if.set_channel(ch)))
    global f
    f = open('log.txt', 'w+')
    f.write("{}-started\n".format(get_whm()))
    sta_if.promiscuous_enable(monitor)
    if schedule:
        #tim = machine.Timer(-1)
        #tim.init(period=TIMER_PERIOD * 1000, mode=machine.Timer.PERIODIC, callback=timer_schedule)
        #timer causes crashes with monitor callbacks, things probably need to be in critical section, implement while True for now
        while True:
            timer_schedule()
            time.sleep(TIMER_PERIOD)


def clear():
    disable()
    os.remove('log.txt')

