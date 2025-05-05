from flask import Flask 
from flask import render_template, request, redirect, Response, url_for, session , flash, jsonify
from flask_mysqldb import MySQL,MySQLdb
from datetime import datetime
from tkinter import *

app = Flask(__name__,template_folder='templates')
app.secret_key = "caircocoders-ednalan"


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'proyecto'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')   

@app.route('/admin')
def admin():
    return render_template('admin.html')  


 

#------------marcar la hora---------

@app.route('/marcar-horas', methods= ["POST"])
def marcar_horas():
    usuario_id = session.get('id')
    fecha_actual = datetime.now().date()
    hora_actual = datetime.now().time()

    cur = mysql.connection.cursor()
    if request.form.get('marcarEntrada'):
        cur.execute('SELECT id FROM Registro_Horas WHERE usuario_id = %s AND fecha = %s AND hora_entrada IS NOT NULL', (usuario_id, fecha_actual))
        entrada_existente = cur.fetchone()

        if entrada_existente:
            cur.close()
            return render_template('index.html', mensaje_error="Ya ha marcado el dia de hoy")

        cur.execute('INSERT INTO Registro_Horas (usuario_id, fecha, hora_entrada) VALUES (%s, %s, %s)', (usuario_id, fecha_actual, hora_actual))
        mysql.connection.commit()

    elif request.form.get('marcarSalida'):
        cur.execute('SELECT id FROM Registro_Horas WHERE usuario_id = %s AND fecha = %s AND hora_entrada IS NOT NULL AND hora_salida IS NULL', (usuario_id, fecha_actual))
        entrada_existente = cur.fetchone()
        if not entrada_existente:
            cur.close()
            return render_template('index.html', mensaje_error="No ha marado su entrada.")
        cur.execute('UPDATE Registro_Horas SET hora_salida = %s WHERE usuario_id = %s AND fecha = %s', (hora_actual, usuario_id, fecha_actual))
        mysql.connection.commit()

    cur.close()

    return render_template('index.html', mensaje3="Marcaje guardado")

#--------------- mensaje para usuario-----------------

def obtener_nombre(empleado_id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT nombre FROM empleado WHERE id = %s', (empleado_id,))
    nombre = cur.fetchone()
    cur.close()
    return nombre if nombre else None

#--------------- Acceso-----------------

@app.route('/acceso-login', methods= ["GET", "POST"])
def login():
    

    if request.method == 'POST' and 'txtUsuario' in request.form and 'txtContraseña':
        _usuario = request.form['txtUsuario']
        _contraseña = request.form['txtContraseña']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM empleado WHERE usuario = %s AND contraseña = %s', (_usuario, _contraseña,))
        account = cur.fetchone()
        
        if account:
            session['logueado'] = True
            session['id'] = account['id']
            session['id_rol'] = account['id_rol']
            usuario_id = account['id']

            if session['id_rol'] == 1:
                return render_template("admin.html")
            elif session ['id_rol']== 2:
                 nombre_usuario = obtener_nombre(usuario_id)
                 return render_template("usuario.html", nombre_usuario=nombre_usuario)

            
            
        else:
            return render_template('index.html', mensaje="Error correo o contraseña incorrecta")
        
 #-----------REGISTRO EMPLEADO-----------------
 
@app.route('/registro')
def registro():
    return render_template('registro.html')  

@app.route('/crear-registro', methods = ["GET", "POST"])
def crear_registro():
      
    

      nombre = request.form['txtNombre'].strip()
      f_nacimiento = request.form['txtFechaNacimiento'].strip()
      genero = request.form['txtGenero'].strip()
      direccion = request.form['txtDireccion'].strip()
      telefono = request.form['txtTelefono'].strip()
      correo = request.form['txtCorreo'].strip()
      f_contrato = request.form['txtFechaContrato'].strip()
      usuario = request.form['txtUsuario'].strip()
      contraseña = request.form['txtContraseña'].strip()

      cur = mysql.connection.cursor()
      cur.execute(" INSERT INTO empleado (nombre, fecha_nacimiento, genero, direccion, telefono, correo, fecha_contrato, usuario, contraseña, id_rol) VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s,'2')",
                  (nombre,f_nacimiento,genero,direccion,telefono,correo,f_contrato,usuario,contraseña))
      mysql.connection.commit()
    
      return render_template("admin.html",mensaje2="Usuario Registrado Exitosamente")




#---------eliminar-------------------------------

@app.route('/eliminar-empleado/<int:id>', methods=['POST'])
def eliminar_empleado(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM empleado WHERE id = %s', (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('listar'))



   #------------------editar tabla----------------

@app.route('/edit/<id>', methods=['POST', 'GET'])
def get_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM empleado WHERE id = %s %s', (id))
    mostrar = cur.fetchone()  
    cur.close()
    return render_template('actualizar.html', mostrar=mostrar)  





   #----------------actualizar tabla-------------------


@app.route('/update/<int:id>', methods= ['POST', 'GET'])
def update(id):
    if request.method == 'POST':
      nombre = request.form['txtNombre'].strip()
      f_nacimiento = request.form['txtFechaNacimiento'].strip()
      genero = request.form['txtGenero'].strip()
      direccion = request.form['txtDireccion'].strip()
      telefono = request.form['txtTelefono'].strip()
      correo = request.form['txtCorreo'].strip()
      f_contrato = request.form['txtFechaContrato'].strip()
      usuario = request.form['txtUsuario'].strip()
      contraseña = request.form['txtContraseña'].strip()

      id_data = request.form['id']
        

      cur = mysql.connection.cursor()
      cur.execute("""
         UPDATE empleado SET nombre=%s, fecha_nacimiento=%s, genero=%s, direccion=%s, telefono=%s, correo=%s, fecha_contrato=%s, usuario=%s, contraseña=%s
         WHERE id=%s
         """, (nombre,f_nacimiento,genero,direccion,telefono,correo,f_contrato,usuario,contraseña, id_data))

      
      flash('mostrar actualizado Successfully')
      mysql.connection.commit()
      return redirect(url_for('listar'))
    
    #--------lista-------

@app.route('/listar')
def listar ():
    
    return render_template('lista.html')


#-----------------buscar--------------------------

@app.route("/ajaxlivesearch", methods=["POST", "GET"])
def ajaxlivesearch():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    employee = None  

    if request.method == 'POST':
        search_word = request.form.get('search_text')  

        if not search_word:
            cur.execute("SELECT * FROM empleado")
            employee = cur.fetchall()
        else:
            query = """
                SELECT * FROM empleado 
                WHERE nombre LIKE %s OR fecha_nacimiento LIKE %s OR genero LIKE %s 
                OR direccion LIKE %s OR telefono LIKE %s OR correo LIKE %s 
                OR fecha_contrato LIKE %s OR usuario LIKE %s OR contraseña LIKE %s 
                ORDER BY id DESC LIMIT 20
            """
            search_pattern = f'%{search_word}%'
            cur.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern, 
                                search_pattern, search_pattern, search_pattern, search_pattern, 
                                search_pattern))
            employee = cur.fetchall()

    numrows = len(employee) if employee else 0 #funciona para que siempre te muestre los datos de la base 

    return jsonify({'htmlresponse': render_template('busqueda.html', employee=employee, numrows=numrows)})

#-----------registro de marcaje___

@app.route('/Marcaje', methods=["GET", "POST"])
def Marcaje():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM vista_registro_marcaje")
    registros = cur.fetchall()
    cur.close()

    return render_template("Marcaje.html", registros=registros)

#-------saludo 
@app.route('/saludo/<int:id>')
def saludo_personalizado(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT nombre FROM empleado WHERE id = %s", (id,))
    nombre = cur.fetchone()['nombre']
    print(f"Nombre obtenido de la base de datos: {nombre}") 
    cur.close()
    return render_template("saludo.html", nombre=nombre)

#-------Eliminar Horas de Empleado
@app.route('/Marcaje/<int:id>', methods=['POST'])
def eliminar_empleadohoras(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM registro_horas WHERE id = %s', (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('lista'))

#-----JARVISAI
@app.route('/llamar_python')
def llamar_python():
    import speech_recognition as sr
    import subprocess as sub
    from PIL import Image, ImageTk
    import pyttsx3, pywhatkit, wikipedia, datetime, keyboard, os
    from pygame import mixer
    import threading as tr

    main_window = Tk()
    main_window.title("Jarvis AI")

    main_window.geometry("800x450")
    main_window.resizable(0,0)
    main_window.configure(bg='#F2F2F2')

    comandos = """ 
                Comandos que puedes usar:
            
                - Reproduce...(canción)
                - Busca...(algo)
                - Abre...(página web o app)
                - Alarma...(hora en 24h)
                - Archivo...(nombre)
                - Termina
    """

    label_title = Label(main_window, text="Jarvis AI", bg="#D7DDE8", fg="#000000", font=('Arial', 30, 'bold'))
    label_title.pack(pady=10)

    canvas_comandos = Canvas(bg="#d7d2cc", height=150, width=200)
    canvas_comandos.place(x=0, y=0)
    canvas_comandos.create_text(80, 80, text=comandos, fill="black", font='Arial 10')

    text_info = Text(main_window, bg="#616161", fg="white", font='Arial 10')
    text_info.place(x=0, y=150, height=300, width=203)

    jarvis_photo = ImageTk.PhotoImage(Image.open("bot.png"))
    window_photo = Label(main_window, image= jarvis_photo )
    window_photo.pack(pady=10)
    window_photo.pack_configure(anchor='e', padx=248)

    def mexican_voice():
        change_voice(2)
    def spanish_voice():
        change_voice(0)
    def english_voice():
        change_voice(1)
    def change_voice(id):
        engine.setProperty('voice', voices[id].id)
        engine.setProperty('rate', 145)
        talk("Hola soy Jarvis!")

    name = "jarvis"
    listener = sr.Recognizer()
    engine = pyttsx3.init()

    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[2].id)
    engine.setProperty('rate', 145)

    sites={
                    'google':'google.com',
                    'youtube':'youtube.com',
                    'facebook':'facebook.com'
                    
    }

    files = {
        'tercer':'Tercer Examen Parcial - Educacion Ciudadana.docx',
        'cedula':'cualquier archivo.docx',
        'foto':'cualquierfoto.jpg'

    }

    programs = {
        'db' : r"C:\Program Files\DB Browser for SQLite\DB Browser for SQLite.exe"
    }


    def talk(text):
        engine.say(text)
        engine.runAndWait()

    def read_and_talk():
        text = text_info.get("1.0", "end")
        talk(text)
    def write_text(text_wiki):
        text_info.insert(INSERT, text_wiki)
        
    def listen():
        try:
            with sr.Microphone() as source:
                talk("Te Escucho")
                pc = listener.listen(source)
                rec = listener.recognize_google(pc, language="es")
                rec = rec.lower()
                if name in rec:
                    rec = rec.replace(name, '')
        except:
            pass
        return rec

    def clock(rec):
        num = rec.replace('alarma', '')
        num = num.strip()
        talk("Alarma activada a las " + num + " horas")
        if num[0] != '0' and len(num) < 5:
            num = '0' + num
        print(num)
        while True:
            if datetime.datetime.now().strftime('%H:%M' ) == num:
                print("DESPIERTA!!!")
                mixer.init()
                mixer.music.load("alarm-clock.mp3")
                mixer.music.play()
            else:
                continue
            if keyboard.read_key() == "s":
                mixer.music.stop()
                break

    def run_jarvis():
        while True:
            rec = listen()
            if 'reproduce' in rec:
                music = rec.replace('reproduce', '')
                print("Reproduciendo " + music)
                talk("Reproduciendo " + music)
                pywhatkit.playonyt(music)    
            elif 'busca' in rec:
                search = rec.replace('busca','')
                wikipedia.set_lang('es')
                wiki = wikipedia.summary(search, 1)
                talk(wiki)
                write_text(search + ": " + wiki)
                break               
            elif 'alarma' in rec:
                t = tr.Thread(target=clock, args=(rec,))
                t.start()                            
            elif 'abre' in rec:
                for site in sites:
                    if site in rec:
                        sub.call(f'start chrome.exe {sites[site]}', shell=True)
                        talk(f'Abriendo {site}')
                for app in programs:
                    if app in rec:
                        talk(f'Abriendo {app}')
                        sub.Popen(programs[app])                    
            elif 'archivo' in rec:
                for file in files:
                    if file in rec:
                        sub.Popen([files[file]], shell=True)
                        talk(f'Abriendo {file}')
                        
            elif 'escribe' in rec:
                try:
                    with open("nota.txt", 'a') as f:
                        write(f)
                    
                except FileNotFoundError as e:
                    file = open("nota.txt",  'w')
                    write(file)
                
            elif 'termina' in rec:
                talk('Adios!')
                break      
    def write(f):
        talk("¿Que quieres que escriba?")
        rec_write = listen()
        f.write(rec_write + os.linesep)
        f.close()
        talk("Listo, puedes revisarlo")
        sub.Popen("nota.txt", shell=True)
        

    button_voice_mx = Button(main_window, text="Voz México", fg="white", bg="#45a247", font=("Arial", 12, "bold"), command= mexican_voice)                    
    button_voice_mx.place(x=625, y=80, width=100, height=30)

    button_voice_es = Button(main_window, text="Voz España", fg="white", bg="#f12711", font=("Arial", 12, "bold"), command= spanish_voice)                    
    button_voice_es.place(x=625, y=115, width=100, height=30)

    button_voice_us = Button(main_window, text="Voz USA", fg="white", bg="#4286f4", font=("Arial", 12, "bold"), command= english_voice)                    
    button_voice_us.place(x=625, y=150, width=100, height=30)

    button_listen = Button(main_window, text="Escuchar", fg="white", bg="#1565c0", font=("Arial", 15, "bold"), width=10, height=1, command= run_jarvis)                    
    button_listen.place(x=625, y=150, width=100, height=30)

    button_listen.pack(pady=10)

    button_speak= Button(main_window, text="Hablar", fg="white", bg="#616161", font=("Arial", 12, "bold"), command= read_and_talk)                    
    button_speak.place(x=625, y=190, width=100, height=30)

    main_window.mainloop()
    return render_template('admin.html')

#--------------Iniciar la aplicación
if __name__ == '__main__':
    app.secret_key = "llave"
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)