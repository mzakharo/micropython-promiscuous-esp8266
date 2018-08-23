import network
import utime as time
import os
from micropython import const, schedule
import machine
#rtc = machine.RTC()
#rtc.datetime((2018,8,22,2,11,18,0,0))

BOOT_WAIT = const(10)
MIN_15 = const(15*60)
MIN_30 = const(30*60)
#MIN_15 = const(10)
#MIN_30 = const(10)


TIMER_PERIOD=MIN_30
boot_time = time.time()

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


def sleep(seconds):
    #allow 15 min after manual reset to work with the device
    if ((time.time() - boot_time) > BOOT_WAIT or machine.reset_cause() == machine.DEEPSLEEP_RESET):
        if disable() is True: #only sleep if previously enabled
            os.umount('/')
            rtc = machine.RTC()
            rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
            rtc.alarm(rtc.ALARM0, seconds * 1000)
            print('put the device to sleep')
            machine.deepsleep()

def mac_to_str(a):
    return ("%02x:%02x:%02x:%02x:%02x:%02x" % (((a[0])), ((a[1])), ((a[2])),
                                               ((a[3])), ((a[4])), (a[5])))


day = {0 : 'mon',
        1 : 'tue',
        2 : 'wed',
        3 : 'thu',
        4 : 'fri',
        5 : 'sat',
        6 : 'sun',
        }

def get_whm():
    t = time.localtime(time.time())
    return (day[t[6]],t[3],t[4])

macs = {}

def monitor(mac_in):
    mac = mac_to_str(mac_in)
    if mac not in macs:
        if not mac_in[0] & 0x2:
            suffix = 'G'
            macs[mac] = None
        else:
            suffix = 'L'
        whm = get_whm()
        s ="{}-{}-{}\n".format(whm,mac, suffix)
        print(s, end="")
        f.write(s)
        sleep(MIN_15)

def sleep_schedule(whm):
    wkd,hour,_ = whm
    if (hour >= 6 and hour <=20) and (wkd in ['sat', 'sun'] or hour >= 16):
        return False
    return True #sleep sleep sleep


def timer_schedule(self=None):
    whm = get_whm()
    print('{}-timer'.format(whm))
    if sleep_schedule(whm):
        sleep(MIN_30)

def enable(ch=6, schedule=True):
    if machine.reset_cause() != machine.DEEPSLEEP_RESET:
        print('waiting 5 sec for user reset')
        time.sleep(5)
    else:
        time.sleep(1)
    #elif schedule:
    #    timer_schedule()
    print("Promiscuous mode enable")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.promiscuous_disable()
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if.active(True)
    global f
    print("Channel {}".format(sta_if.set_channel(ch)))
    f = open('log.txt', 'a')
    f.write("{}-started\n".format(get_whm()))
    sta_if.promiscuous_enable(monitor)
    if schedule:
        #tim = machine.Timer(-1)
        #tim.init(period=TIMER_PERIOD * 1000, mode=machine.Timer.PERIODIC, callback=timer_schedule)
        #timer causes crashes with monitor callbacks, things probably need to be in critical section, implement while True for now
        try:
            while True:
                timer_schedule()
                time.sleep(TIMER_PERIOD)
        except:
            raise
        finally:
            disable()


def clear():
    disable()
    os.remove('log.txt')

