import network
import utime as time
import os

'''
import machine
rtc = machine.RTC()
rtc.datetime((2018,8,22,2,11,18,0,0))
'''

def mac_to_str(a):
    return ("%02x:%02x:%02x:%02x:%02x:%02x" % (((a[0])), ((a[1])), ((a[2])),
                                               ((a[3])), ((a[4])), (a[5])))

def get_whm():
    t = time.localtime(time.time())
    return (t[6],t[3],t[4])

f = None
macs = {}
def callback(mac_in):
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

def enable(ch=6):
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
    sta_if.promiscuous_enable(callback)

def disable():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.promiscuous_disable()
    global f
    if f is not None:
        f.close()
        f = None
    print("Promiscuous mode disabled")

def clear():
    disable()
    os.remove('log.txt')

