import serial
import time
arduino = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(3)
strArduino = arduino.readline().strip()
print('Binario:', strArduino)
# binary a string
strArduino = strArduino.decode("utf-8")
print('Cadena:', strArduino)
datos = {
    'temperatura': None,
    'humedad': None,
    'intensidad_luz': None,
    'humedad_suelo': None
}

for dato in datos:
    ini = 0
    fin = None
    if dato == 'temperatura':
        fin = strArduino.index(',')
        datos['temperatura'] = strArduino[ini:fin]
        strArduino = strArduino[fin + 1:len(strArduino)]
        print('En temp:', strArduino)

    if dato == 'humedad':
        fin = strArduino.index(',')
        datos['humedad'] = strArduino[ini:fin]
        strArduino = strArduino[fin + 1:len(strArduino)]
        print('En hum:', strArduino)

    if dato == 'intensidad_luz':
        fin = strArduino.index(',')
        datos['intensidad_luz'] = strArduino[ini:fin]
        strArduino = strArduino[fin + 1:len(strArduino)]

    if dato == 'humedad_suelo':
        datos['humedad_suelo'] = 0

print(datos)
arduino.close()
