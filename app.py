from distutils.util import execute
import serial
import time
import atexit
import threading
import sqlite3
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from apscheduler.schedulers.background import BackgroundScheduler
from turbo_flask import Turbo


def get_db_connection():
    '''conexion con la base de datos'''
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_dato(dato_id):
    '''Obtener el dato desde la base de datos'''
    conn = get_db_connection()
    dato = conn.execute('SELECT * FROM sensor_data WHERE id = ?',
                        (dato_id,)).fetchone()
    conn.close()
    if dato is None:
        abort(404)
    return dato


def read():
    '''Funcion que permite obtener datos de arduino'''
    # arduino = serial.Serial('/dev/ttyACM0', 9600)
    strArduino = arduino.readline().strip()
    # time.sleep(1)
    strArduino = arduino.readline().strip()
    print('Binario:', strArduino)
    # binary a string
    strArduino = strArduino.decode("utf-8")
    print('Cadena:', strArduino)
    datos = {
        'temperatura': None,
        'humedad': None,
        'intensidad_luz': None,
        'humedad_suelo': None,
        'limT': None,
        'limH': None,
        'limL': None,
        'limS': None,
    }

    # Verifica que se incluya el inicio de la lectura de arduino ('-')
    if '-' in strArduino:

        for dato in datos:
            ini = 0
            fin = None
            if dato == 'temperatura':
                ini = strArduino.index('-') + 1
                fin = strArduino.index(',')
                datos['temperatura'] = strArduino[ini:fin]
                strArduino = strArduino[fin + 1:len(strArduino)]
                # print('En temp:', strArduino)

            if dato == 'humedad':
                fin = strArduino.index(',')
                datos['humedad'] = strArduino[ini:fin]
                strArduino = strArduino[fin + 1:len(strArduino)]
                # print('En hum:', strArduino)

            if dato == 'intensidad_luz':
                fin = strArduino.index(',')
                datos['intensidad_luz'] = strArduino[ini:fin]
                strArduino = strArduino[fin + 1:len(strArduino)]

            if dato == 'humedad_suelo':
                fin = strArduino.index(',')
                datos['humedad_suelo'] = strArduino[ini:fin]
                strArduino = strArduino[fin + 1:len(strArduino)]

            # Limites
            if dato == 'limT':
                fin = strArduino.index(',')
                datos['limT'] = float(strArduino[ini:fin])
                strArduino = strArduino[fin + 1:len(strArduino)]

            if dato == 'limH':
                fin = strArduino.index(',')
                datos['limH'] = float(strArduino[ini:fin])
                strArduino = strArduino[fin + 1:len(strArduino)]

            if dato == 'limL':
                fin = strArduino.index(',')
                datos['limL'] = float(strArduino[ini:fin])
                strArduino = strArduino[fin + 1:len(strArduino)]

            if dato == 'limS':
                fin = strArduino.index(',')
                datos['limS'] = float(strArduino[ini:fin])
                strArduino = strArduino[fin + 1:len(strArduino)]

        # Conectar la base de datos para insertar valores
        connection = sqlite3.connect('database.db')
        cur = connection.cursor()
        cur.execute(
            "INSERT INTO sensor_data (temperatura, humedad, intensidad_luz, humedad_suelo) VALUES (?, ?, ?, ?)", (
                datos['temperatura'], datos['humedad'], datos['intensidad_luz'], datos['humedad_suelo'])
        )
        connection.commit()
        connection.close()

        conn = get_db_connection()
        limite = conn.execute('SELECT * FROM limite LIMIT 1').fetchone()
        conn.close()

        # print('datos:{} type:{}, limite:{} type:{}'.format(datos['limT'], type(datos['limT']), limite['temperatura'], type(limite['temperatura'])))
        # print(datos['limT'] != limite['temperatura'])

        if datos['limT'] != limite['temperatura']:
            cambiarLimT(datos['limT'])

        if datos['limH'] != limite['humedad']:
            cambiarLimH(datos['limH'])

        if datos['limL'] != limite['intensidad_luz']:
            cambiarLimL(datos['limL'])

        if datos['limS'] != limite['humedad_suelo']:
            cambiarLimS(datos['limS'])


def cambiarLimT(valor):
    connection = sqlite3.connect('database.db')
    cur = connection.cursor()
    cur.execute(
        'UPDATE limite SET temperatura = ? WHERE temperatura NOT NULL', (valor,)
    )
    connection.commit()
    connection.close()

def cambiarLimH(valor):
    connection = sqlite3.connect('database.db')
    cur = connection.cursor()
    cur.execute(
        'UPDATE limite SET humedad = ? WHERE temperatura NOT NULL', (valor,)
    )
    connection.commit()
    connection.close()

def cambiarLimL(valor):
    connection = sqlite3.connect('database.db')
    cur = connection.cursor()
    cur.execute(
        'UPDATE limite SET intensidad_luz = ? WHERE temperatura NOT NULL', (valor,)
    )
    connection.commit()
    connection.close()

def cambiarLimS(valor):
    connection = sqlite3.connect('database.db')
    cur = connection.cursor()
    cur.execute(
        'UPDATE limite SET humedad_suelo = ? WHERE temperatura NOT NULL', (valor,)
    )
    connection.commit()
    connection.close()

def write(sensor, valor):
    '''Funcion para escribir información en arduino'''
    # arduino = serial.Serial('/dev/ttyACM0', 9600)
    # time.sleep(2)
    print("\nValores a escribir: ", (valor + ',' + sensor).encode("utf-8"))
    arduino.write((valor + ',' + sensor).encode("utf-8"))
    # arduino.close()


# scheduler = BackgroundScheduler(daemon=True)
# scheduler.add_job(read, 'interval', seconds=3)
# scheduler.start()
# Apague el programador al salir de la aplicación
# atexit.register(lambda: scheduler.shutdown())
arduino = serial.Serial('/dev/ttyACM0', 9600)
atexit.register(lambda: arduino.close())


app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcdefghij123456789'
turbo = Turbo(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/humedad', methods=('GET', 'POST'))
def humedad():

    if request.method == 'POST':
        valor = request.form['valor']
        sensor = "H\n"

        if not valor:
            flash('Se require un valor')
        else:
            flash('Valor modificado')
            write(sensor, valor)

    conn = get_db_connection()
    datos = conn.execute('SELECT fecha,humedad FROM sensor_data ORDER BY id DESC LIMIT 500').fetchall()

    data = []
    cont = 0
    for dato in datos:
        data.append((dato['fecha'], dato['humedad']))
        cont += 1

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    return render_template('humedad.html', labels=labels, values=values)

@app.route('/temperatura', methods=('GET', 'POST'))
def temperatura():

    if request.method == 'POST':
        valor = request.form['valor']
        sensor = "T\n"

        if not valor:
            flash('Se require un valor')
        else:
            flash('Valor modificado')
            write(sensor, valor)

    conn = get_db_connection()
    datos = conn.execute('SELECT temperatura FROM sensor_data ORDER BY id DESC LIMIT 500').fetchall()

    data = []
    cont = 0
    for dato in datos:
        data.append((cont, dato['temperatura']))
        cont += 1

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    return render_template('temperatura.html', labels=labels, values=values)


@app.route('/intensidad_luz', methods=('GET', 'POST'))
def intensidad_luz():

    if request.method == 'POST':
        valor = request.form['valor']
        sensor = "L\n"

        if not valor:
            flash('Se require un valor')
        else:
            flash('Valor modificado')
            write(sensor, valor)

    conn = get_db_connection()
    datos = conn.execute('SELECT intensidad_luz FROM sensor_data ORDER BY id DESC LIMIT 500').fetchall()

    data = []
    cont = 0
    for dato in datos:
        data.append((cont, dato['intensidad_luz']))
        cont += 1

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    return render_template('intensidad_luz.html', labels=labels, values=values)


@app.route('/humedad_suelo', methods=('GET', 'POST'))
def humedad_suelo():

    if request.method == 'POST':
        valor = request.form['valor']
        sensor = "S\n"

        if not valor:
            flash('Se require un valor')
        else:
            flash('Valor modificado')
            write(sensor, valor)

    conn = get_db_connection()
    datos = conn.execute('SELECT humedad_suelo FROM sensor_data ORDER BY id DESC LIMIT 500').fetchall()

    data = []
    cont = 0
    for dato in datos:
        data.append((cont, dato['humedad_suelo']))
        cont += 1

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    return render_template('humedad_suelo.html', labels=labels, values=values)

@app.context_processor
def inject_load():
    conn = get_db_connection()
    datos = conn.execute('SELECT * FROM sensor_data ORDER BY id DESC LIMIT 1').fetchone()
    limites = conn.execute('SELECT * FROM limite LIMIT 1').fetchone()
    # print('\nT: {}, H: {}, L: {}, HS: {}'.format(datos['temperatura'], datos['humedad'], datos['intensidad_luz'], datos['humedad_suelo']))
    conn.close()
    return {'temperatura': datos['temperatura'], 'humedad': datos['humedad'], 'intensidad_luz': datos['intensidad_luz'], 'humedad_suelo': datos['humedad_suelo'],
            'limT': limites['temperatura'], 'limH': limites['humedad'], 'limL': limites['intensidad_luz'], 'limS': limites['humedad_suelo']}


@app.before_first_request
def before_first_request():
    threading.Thread(target=update_load).start()


def update_load():
    with app.app_context():
        while True:
            read()
            time.sleep(2)
            turbo.push(turbo.replace(render_template('loadavg.html'), 'load'))


@app.route('/<int:dato_id>')
def dato(dato_id):
    dato = get_dato(dato_id)
    return render_template('dato.html', dato=dato)


'''
export FLASK_APP=app
export FLASK_ENV=development
flask run

Abrir puerto
//Consultar: ls -l /dev | grep ACM
//conceder permisos puertos: sudo chmod 777 /dev/ttyACM0
'''
