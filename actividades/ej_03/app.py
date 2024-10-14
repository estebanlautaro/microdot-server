import network
import socket
import json
import machine
from time import sleep
import _thread

# Pin Setup
buzzer = machine.Pin(15, machine.Pin.OUT)  # Configura el buzzer en el pin GPIO15
temperature_sensor = machine.ADC(machine.Pin(32))  # Sensor de temperatura en GPIO32
temperature_sensor.atten(machine.ADC.ATTN_11DB)  # Para obtener un rango completo de voltaje

setpoint_temp = 0  # Variable global para almacenar la temperatura de setpoint

# Servidor Web
def web_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print('Listening on', addr)

    while True:
        cl, addr = s.accept()
        print('Client connected from', addr)
        request = cl.recv(1024)
        request = str(request)
        
        # Parsing HTTP request
        if "GET /temperature" in request:
            current_temp = (temperature_sensor.read() / 4095) * 100  # Simulación de temperatura
            response = json.dumps({"temperature": current_temp})
            cl.send('HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n' + response)

        elif "POST /setpoint" in request:
            setpoint_start = request.find('setpoint=') + len('setpoint=')
            setpoint_end = request.find(' ', setpoint_start)
            global setpoint_temp
            setpoint_temp = int(request[setpoint_start:setpoint_end])
            cl.send('HTTP/1.1 200 OK\r\n\r\n')
        
        elif "GET /buzzer" in request:
            response = json.dumps({"buzzer_state": buzzer.value()})
            cl.send('HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n' + response)

        elif "GET / " in request or "GET /index.html" in request:
            with open("index.html", "r") as f:
                html_content = f.read()
            cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + html_content)
        
        cl.close()

# Thread para monitorizar la temperatura y el buzzer
def temperature_monitor():
    global setpoint_temp
    while True:
        current_temp = (temperature_sensor.read() / 4095) * 100  # Simulación de temperatura
        if current_temp > setpoint_temp:
            buzzer.value(1)  # Encender buzzer si la temperatura excede el setpoint
        else:
            buzzer.value(0)  # Apagar buzzer si la temperatura está por debajo del setpoint
        sleep(1)

# Iniciar el servidor y el monitor en paralelo
_thread.start_new_thread(temperature_monitor, ())
web_server()
