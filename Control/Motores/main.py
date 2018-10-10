from flask import Flask, render_template, Response, request
import time
import os


#Variables globales
ip_ESP8266 = "0.0.0.0"
ip_client1 = "0.0.0.0"
system_state = "ESP" # Sistema empieza en estado FREERUN

app = Flask(__name__)
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
            else: # Entonces el estado de la ESP es Pointcloud o Freerun
                command = "RESET" # Resetear
                system_state = "ESP"
                return command
        elif( system_state == "FREERUN" ):
            if(ESPstate == "FREERUN"): # Freerun
                command  = "FREERUN"
                return command +"&"+str(step1)+ "&" + str(step2)
            elif (ESPstate == "POINTCLOUD"): # cambiar a estado FREERUN el sistema
                step1 = phi_0 - 97  # Reiniciar posicion de los motores
                step2 = theta_0- 57
                command  = "FREERUN"
                return command +"&"+str(step1)+ "&" + str(step2)
            elif (ESPstate == "OK"):
                command = "RESET"
                system_state = "ESP"
                return  command

        if (system_state == "POINTCLOUD"): #  si un cliente hizo la peticion de pointcloud
            if (ESPstate == "POINTCLOUD"):  #  si la ESP esta Pointcloud
                if (param1 != "FINISH" and param2 != "FINISH"): # si la nube de punto no ha terminado
                     N_med_infra = 16
                     Infra_data = int(param1)/N_med_infra*3.1/(2**12-1)  # Convertir string a entero
                     Echo_data = int(param2)
                     step11 = int(param3)*1.0  # paso actual del motor
                     step22 = int(param4)*1.0


                     infra_distance = med_infrarrojo(Infra_data)
                     ultra_distance = med_ultrasonido(Echo_data)
                     phi = transform_step(step11, 0)
                     theta = transform_step(step22, 1)

                     r1, theta1, phi1, x1, y1, z1, = transform_coord(ultra_distance, theta, phi, 0)
                     r2, theta2, phi2, x2, y2, z2, = transform_coord(infra_distance, theta, phi, 1)

                     data1 = np.append(data1, [[x1, y1, z1]], 0)
                     data2 = np.append(data2, [[x2, y2, z2]], 0)

                     _, img = camera.read()

                     cx1, cy1, w1, h1 = Pixel_Fun(ultra_distance, 0)
                     color = mean_color(img.copy(), cx1, cy1, w1, h1) # pasar copia de la imagen actual
                     (b, g, r, channel) = color
                     color_ultra = np.append(color_ultra, [[r / 255.0, g / 255.0, b / 255.0, 1]], 0)
                     cv2.rectangle(img, (cx1 - w1, cy1 - h1), (cx1 + w1, cy1 + h1), (255, 0, 0), 3)

                     cx2, cy2, w2, h2 = Pixel_Fun(infra_distance, 1)
                     color = mean_color(img.copy(), cx2, cy2, w2, h2)  # pasar copia de la imagen actual
                     (b, g, r, channel) = color
                     color_infra = np.append(color_infra, [[r / 255.0, g / 255.0, b / 255.0, 1]], 0)

                     cv2.rectangle(img, (cx2 - w2, cy2 - h2), (cx2 + w2, cy2 + h2), (255, 0, 0), 3)
                     font = cv2.FONT_HERSHEY_SIMPLEX
                     cv2.putText(img, "Distance Ultra = {0:0.2f} cm".format(ultra_distance), (50, 50), font, 0.8,
                                 (20, 200, 20), 3, cv2.LINE_AA)
                     cv2.putText(img, "Distance Infra = {0:0.2f} cm".format(infra_distance), (50, 80), font, 0.8,
                                 (20, 200, 20), 3, cv2.LINE_AA)
                     cv2.putText(img, "theta = {0:0.2f} degrees".format(np.degrees(theta)), (50, 110), font, 0.8,
                                 (20, 200, 20), 3, cv2.LINE_AA)
                     cv2.putText(img, "phi   = {0:0.2f} degrees".format(np.degrees(phi)), (50, 140), font, 0.8,
                                 (20, 200, 20), 3, cv2.LINE_AA)


                     print("Ultra_dis = {0:0.2f}, Infra_dis = {1:0.2f}, phi = {2:0.2f}, theta = {3:0.2f}".format(
                     r1, r2, np.degrees(phi), np.degrees(theta)))
                     return "OK"
                else: # PoinCloud terminada
                    # guardar data
                    pointcloud1 = data1
                    pointcloud2 = data2
                    os.mkdir("Data/"+file_name)
                    np.savetxt("Data/"+file_name+"/Ultra.out", pointcloud1, fmt='%1.8e')
                    np.savetxt("Data/"+file_name+"/Infra.out", pointcloud2, fmt='%1.8e')
                    np.savetxt("Data/"+file_name+"/ColorInfra.out", color_infra, fmt='%1.8e')
                    np.savetxt("Data/"+file_name+"/ColorUltra.out", color_ultra, fmt='%1.8e')
                    step1 = phi_0 - 97  # reiniciar posicion de motor
                    step2 = theta_0 - 57
                    command = "FREERUN"
                    system_state = "FREERUN"
                    img = np.zeros((h, w, 3), dtype='uint8')
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(img, "PointCloudLM Ready", (0, centery), font, 2, (50, 255, 50))
                    return command + "&" + str(step1) + "&" + str(step2)



            elif (ESPstate == "FREERUN"):
                command = "POINTCLOUD"
                return  command + "&" + str(phi_start) +"&"+str(phi_end)+"&"+str(theta_start) + "&"+str(theta_end)

            elif (ESPstate == "OK"):
                command = "RESET"
                system_state = "ESP"
                return command

            # si la ESP esta en FREERUN


@app.route('/HandTracking',methods = ['POST', 'GET'])
def HandTracking():
    global ip_ESP8266, ip_client1, step1, step2, band, system_state
    if request.method == 'POST':
        param1 = request.form['param1']
        param2 = request.form['param2']
        step1 = int(param1)
        step2  = int(param2)
        if (band == 0):
            print("Handtracking Started from ip  = {}".format(ip_client1))
            band = 1
        system_state = "FREERUN"
        return "OK"

    else:
        param1 = request.args.get('step1')
        param2 = request.args.get('step2')
        step1 = int(param1)
        step2  = int(param2)
        if (band == 0):
            ip_client1 = request.remote_addr
            print("Handtracking Started from ip  = {}".format(ip_client1))
            band = 1
        system_state = "FREERUN"
        print("Step1 = {}, Step2 = {}".format(step1, step2))
    return "OK"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)