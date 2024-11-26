from microdot import Microdot, Response
import machine
import onewire
import ds18x20
import json
from time import sleep
import _thread

datapin = machine.Pin(19)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(datapin))

buzzer = machine.Pin(14, machine.Pin.OUT)

setpoint_temp = 15
current_temp = None
roms = None

app = Microdot()

@app.route('/temperature')
def get_temperature(request):
    global current_temp
    temp = current_temp if current_temp is not None else "No disponible"
    return Response(json.dumps({"temperature": temp}), headers={'Content-Type': 'application/json'})

@app.route('/setpoint', methods=['POST'])
def set_setpoint(request):
    global setpoint_temp
    try:
        setpoint_temp = int(request.args.get('setpoint', 0))
        print(f"Setpoint actualizado: {setpoint_temp}°C")
        return Response('', status_code=200)
    except ValueError:
        return Response(json.dumps({"error": "Setpoint inválido"}), status_code=400, headers={'Content-Type': 'application/json'})

@app.route('/buzzer')
def get_buzzer(request):
    return Response(json.dumps({"buzzer_state": buzzer.value()}), headers={'Content-Type': 'application/json'})

@app.route('/')
def index(request):
    with open('index.html', 'r') as f:
        html_content = f.read()
    return Response(html_content, headers={'Content-Type': 'text/html'})

def temperature_monitor():
    global current_temp, setpoint_temp, roms
    roms = ds_sensor.scan()
    if not roms:
        print("Sensor DS18X20 no detectado")
    
    while True:
        if roms:
            try:
                ds_sensor.convert_temp()
                sleep(1)
                temp_readings = []

                for _ in range(5):
                    temp_readings.append(ds_sensor.read_temp(roms[0]))
                    sleep(0.1)

                current_temp = sum(temp_readings) / len(temp_readings)
                print(f"Temperatura promedio: {current_temp:.2f}°C")
            except Exception as e:
                print(f"Error al leer el sensor: {e}")
                current_temp = None
        else:
            current_temp = None

        if current_temp is not None and current_temp > setpoint_temp:
            buzzer.value(1)
        else:
            buzzer.value(0)

        sleep(1)

_thread.start_new_thread(temperature_monitor, ())

app.run(host='0.0.0.0', port=80)
