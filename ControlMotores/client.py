import requests
import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.widgets import Slider, Button, RadioButtons
import json
port_server = "8001"
ip = "192.168.1.100"

activeButton = 0
freq = 60
pwm = 0
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.25)
t = np.arange(0.0, 1.0, 0.000001)
a0 = 0
f0 = 100
delta_f = 5.0
s = np.sin(2*np.pi*f0*t)
l, = plt.plot(t, s, lw=2, color='red')
plt.axis([0, 0.01, -2, 2])

axcolor = 'lightgoldenrodyellow'
axfreq = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=axcolor)
axrpm= plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)

sfreq = Slider(axfreq, 'Freq', 60, 2000.0, valinit=f0, valstep=delta_f)
srpm = Slider(axrpm, 'LED Duty Cycle %', 0, 100, valinit=a0, valstep=1)

def ESP8266_send(): # el servo que controla phi (plano xy)
    global pwm, freq, activeButton
    url_server= "http://"+ ip +":"+ port_server+ "/Client/postjson"
    
    try:
        T_Inicio = time.time()
        payload =  {'ActiveButton': activeButton, "Frequency":freq, "PWM":pwm }
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(url_server, data = json.dumps(payload), headers = headers)
        response = req.content.decode('ascii')
        
        T_Final = time.time()
        Dif = T_Final - T_Inicio
        print("tiempo de envio= {0:0.2f} ms".format(Dif*1000))
        if response != "OK":
            print("Bad response ")
    except:
        print("Error Sending Data")
    

    return



def update(val):
    global pwm, freq
    pwm = int(srpm.val)
    ESP8266_send()
    freq = int(sfreq.val)
    l.set_ydata(np.sin(2*np.pi*freq*t))
    fig.canvas.draw_idle()
sfreq.on_changed(update)
srpm.on_changed(update)

resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')


def reset(event):
    global pwm, freq, activeButton
    pwm = a0
    freq = f0
    activeButton = 0
    ESP8266_send()
    sfreq.reset()
    srpm.reset()
button.on_clicked(reset)

rax = plt.axes([0.025, 0.5, 0.15, 0.15], facecolor=axcolor)
radio = RadioButtons(rax, ('BUZZER', 'LED'), active=0)


def colorfunc(label):
    global activeButton
    if label == "BUZZER":
        activeButton = 0
    else:
        activeButton = 1
    ESP8266_send()
radio.on_clicked(colorfunc)

plt.show()