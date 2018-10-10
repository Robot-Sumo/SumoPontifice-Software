""" En este codigo se recibe la variable nm desde el cliente mediante metodos POST GET"""

#rama 2
from flask import Flask, render_template, Response, request, jsonify
import time
import numpy as np
import os


#Variables globales
rpm = 0
ip_ESP8266 = "0.0.0.0"
ip_client1 = "0.0.0.0"
system_state = "ESP" # Sistema empieza en estado FREERUN


app = Flask(__name__)

T_Inicio = time.time()
T_Inicio2 = time.time()
T_Final = time.time()
T_Final2 = time.time()
Dif = T_Final - T_Inicio
jsonClient = {}

clientConnected = 0
@app.route("/")
def index():
    global system_state
    return render_template('index.html')

@app.route('/ESP8266', methods = ['POST', 'GET'])
def login():
    global ip_ESP8266, step1, step2, system_state, phi_start, phi_end, theta_start, theta_end, phi_0, theta_0, theta_resol, phi_resol
    global img , data1, data2, color_infra, color_ultra
    if request.method == 'POST':
        param1 = request.form['param1']
        param2 = request.form['param2']
        Infra_data = int(param1) # Convertir string a entero
        Ultra_data = int (param2)
        print("Infra = {}, Ultra = {}, ip = {}".format(Infra_data, Ultra_data, ip_ESP8266))
        return "OK"

    else:
        ESPstate = request.args.get('ESPstate')
        param1 = request.args.get('param1')
        param2 = request.args.get('param2')
        param3 = request.args.get('param3')
        param4 = request.args.get('param4')
        if (system_state == "ESP"): # Esperando que se conecta la ESP
            if (ESPstate == "OK"):  # ESP8266 conectada
                ip_ESP8266 = request.remote_addr
                print("ESP8266 Connected, ip  = {}".format(ip_ESP8266))
                system_state = "FREERUN"
                return "OK"

            # si la ESP esta en FREERUN



@app.route('/Client/postjson',methods = ['POST'])
def clientPost():
        global clientConnected, jsonClient
        clientConnected = 1
        
        content = request.get_json()
        jsonClient = content

        pwm = content['PWM']
        freq = content['Frequency']
        activeButton = content['ActiveButton']
        Dif = T_Inicio-T_Final
        print("freq= {}, pwm = {}, activeButton = {}".format(freq, pwm, activeButton))
        print("Time = {} ms".format(Dif*1000))
        return "OK"

@app.route('/ESP8266/postjson', methods = ['POST'])
def postJsonHandler():
    global T_Inicio2, clientConnected, jsonClient
    T_Final2 = T_Inicio2
    T_Inicio2 = time.time()
    content = request.get_json()
    if clientConnected:
        jsonESP = jsonify(jsonClient)
    else:
        jsonESP = jsonify(ActiveButton=-1)
    Dif = T_Inicio2-T_Final2

    print("Time = {} ms".format(Dif*1000))
    return jsonESP

if __name__ == '__main__':
    app.run(host='192.168.1.100', port=8001, debug=True, threaded=True)

