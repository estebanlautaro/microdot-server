# Aplicacion del servidor
from boot import do_connect
from microdot import Microdot, send_file
import machine
import neopixel
import time

do_connect()
app = Microdot()

led1 = machine.Pin(32, machine.Pin.OUT)
led2 = machine.Pin(33, machine.Pin.OUT)
led3 = machine.Pin(25, machine.Pin.OUT)

np = neopixel.NeoPixel(machine.Pin(27), 8)

@app.route('/')
async def index(request):
    return send_file('index.html')

@app.route('/<dir>/<file>')
async def static_file(request, dir, file):
    return send_file(f"/{dir}/{file}")

@app.route('/led')
async def led_control(request):
    led_num = int(request.args.get('led'))
    state = request.args.get('state') == 'true'
    print(f"Controlando LED {led_num}, estado: {state}")
    led = [led1, led2, led3][led_num - 1]
    if state:
        led.on()
    else:
        led.off()
    return f'LED {led_num} {"encendido" if state else "apagado"}'

@app.route('/color')
async def color_control(request):
    r = int(request.args.get('r'))
    g = int(request.args.get('g'))
    b = int(request.args.get('b'))
    print(f"Estableciendo color de tira LED: R:{r}, G:{g}, B:{b}")
    np.fill((r, g, b))
    np.write()
    return f'Color establecido a R:{r}, G:{g}, B:{b}'

app.run(port=80)
