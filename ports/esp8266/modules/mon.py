import time
import os
import network
import machine

DEBUG=False

BOOT_WAIT = (10)

if DEBUG:
    MIN_5 = (10)
    MIN_15 = (10)
    MIN_30 = (10)
else:
    MIN_5 = (5*60)
    MIN_15 = (15*60)
    MIN_30 = (30*60)

MON_PERIOD=MIN_5
boot_time = time.time()

ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
del ap_if
sta_if = network.WLAN(network.STA_IF)
sta_if.promiscuous_disable()
sta_if.active(True)

f = None

def disable():
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
    if ((time.time() - boot_time) > BOOT_WAIT or machine.reset_cause() == machine.DEEPSLEEP_RESET):
        if disable() is True: #only sleep if previously enabled
            os.umount('/')
            rtc = machine.RTC()
            rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
            rtc.alarm(rtc.ALARM0, seconds * 1000)
            print('sleep')
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

def get_time():
    t = time.localtime(time.time())
    return (day[t[6]],t[3],t[4], t[1], t[2])

macs = {}

def monitor(mac_in):
    mac = mac_to_str(mac_in)
    if mac not in macs:
        if not mac_in[0] & 0x2:
            suffix = 'G'
            macs[mac] = None
        else:
            suffix = 'L'
        t = get_time()
        s ="{}-{}-{}\n".format(t,mac,suffix)
        print(s, end="")
        f.write(s)
        sleep(MIN_15)

def sleep_schedule(t):
    wkd,hour,_,_,_ = t 
    if (hour >= 6 and hour <=19) and (wkd in ['sat', 'sun'] or hour >= 16):
        return False
    return True #sleep sleep sleep


def check_schedule(self=None):
    t = get_time()
    print('{}-sched'.format(t))
    if sleep_schedule(t):
        sleep(MIN_30)

def enable(ch=6, schedule=True):
    if machine.reset_cause() != machine.DEEPSLEEP_RESET:
        print('waiting 5 sec for user reset')
        time.sleep(5)
    else:
        time.sleep(1) #to allow for manual double reset to avoid DEEPSLEEP hang
    global f
    print("Promiscuous mode on channel {}".format(sta_if.set_channel(ch)))
    f = open('log.txt', 'a')
    f.write("{}-started\n".format(get_time()))
    if schedule:
        check_schedule()
    sta_if.promiscuous_enable(monitor)
    if schedule:
        try:
            time.sleep(MON_PERIOD)
            sleep(MIN_15)
        except:
            raise
        finally:
            disable()


def clear():
    disable()
    os.remove('log.txt')

