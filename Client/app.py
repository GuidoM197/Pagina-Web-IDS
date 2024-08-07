from flask import Flask, render_template, redirect, url_for, flash, request, session
import requests

BACKEND_URL = 'http://127.0.0.1:8080'
PORT=5000
app = Flask(__name__)
app.secret_key = 'profetas123'

@app.route('/')
def index():
    computadoras = requests.get(f'{BACKEND_URL}/obtener-computadoras').json() # asi se llama a una funcion del back
    pcs_amd = [pc for pc in computadoras if 'AMD' in pc['procesador']]
    pcs_intel = [pc for pc in computadoras if 'Intel' in pc['procesador']]

    if not 'carrito' in session:
        session['carrito'] = {}
        session['carrito']['carrito_producto'] = {}
        session['carrito']['carrito_cantidad'] = {}

    return render_template('./main_page/index.html', pcs_amd=pcs_amd, pcs_intel=pcs_intel, carrito=session['carrito'])

@app.route('/ventas/<idpc>')
def ventas(idpc):
    datos_computadora = requests.get(f'{BACKEND_URL}/detalles-computadora/{idpc}').json()
    return render_template('./pagina-venta/ventas.html', computadora=datos_computadora, carrito=session['carrito'])

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    usuario = request.form.get('usuario')
    email = request.form.get('email')
    contrasenia = request.form.get('contrasenia')
    user = {
        'usuario' : usuario,
        'email' : email,
        'contrasenia' : contrasenia
    }
    resultado = requests.post(f'{BACKEND_URL}/registrar-usuario', json=user)

    if resultado.status_code == 201:
        return redirect(url_for('login'))
    else:
        return render_template('./registrarse/registrarse.html', carrito=session['carrito'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form.get('email')
    contrasenia = request.form.get('contrasenia')
    datos = {
        "email": email,
        "contrasenia": contrasenia
    }
    respuesta = requests.post(f'{BACKEND_URL}/login-user', json=datos)
    if respuesta.status_code == 200:
        respuesta = respuesta.json()
        id = respuesta['id']
        session['id'] = id
        return redirect(url_for('mi_perfil'))
    
    return render_template('./login/login.html', carrito=session['carrito'])

@app.route('/mi-perfil', methods=['GET', 'POST'])
def mi_perfil():
    try:
        id = session['id']
        if id == '-1' or not id:
            return redirect(url_for('login'))

        respuesta = requests.get(f'{BACKEND_URL}/datos-de-usuario/{id}')
        info_usuario = respuesta.json()

        return render_template('./mi-perfil/mi-perfil.html', info_usuario=info_usuario, carrito=session['carrito'])
    except:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('index'))

@app.route('/delete-account', methods=['GET', 'POST'])
def delete_account():
    user_id = session['id']
    if user_id:
        respuesta = requests.delete(f'{BACKEND_URL}/delete-user/{user_id}')
        if respuesta.status_code == 200:
            session.pop('id', None)
            flash('Cuenta eliminada con éxito.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error al eliminar la cuenta.', 'danger')
    return redirect(url_for('mi_perfil'))

@app.route('/actualizar-datos', methods=['GET', 'POST'])
def actualizar_datos():
    id = session['id']
    usuario = request.form.get('usuario')
    email = request.form.get('email')
    contrasenia = request.form.get('contrasenia')

    user = {
        'usuario' : usuario,
        'email' : email,
        'contrasenia' : contrasenia
    }
    requests.put(f'{BACKEND_URL}/subir-datos/{id}', json=user)

    return redirect(url_for('mi_perfil'))

@app.route('/agregar-al-carrito/<id>', methods=['GET', 'POST'])
def agregar_al_carrito(id):
    carrito = session['carrito']
    datos_computadora = requests.get(f'{BACKEND_URL}/detalles-computadora/{id}').json()

    if not carrito:
        carrito = {}

    carrito['carrito_cantidad'] = carrito.get('carrito_cantidad', {})
    carrito['carrito_cantidad'][id] = carrito['carrito_cantidad'].get(id, 0) + 1

    carrito['carrito_producto'] = carrito.get('carrito_producto', {})
    carrito['carrito_producto'][id] = carrito['carrito_producto'].get(id, {})
    carrito['carrito_producto'][id] = {
        'idpc': datos_computadora['idpc'],
        'nombre': datos_computadora['nombre'],
        'procesador': datos_computadora['procesador'],
        'gpu': datos_computadora['gpu'],
        'motherboard': datos_computadora['motherboard'],
        'ram': datos_computadora['ram'],
        'almacenamiento': datos_computadora['almacenamiento'],
        'imagen': datos_computadora['imagen'],
        'precio': datos_computadora['precio'],
        'fuente': datos_computadora['fuente']
    }

    session['carrito'] = carrito
    return redirect(url_for('ventas', idpc=id))

@app.route('/comprar', methods=['GET', 'POST'])
def comprar():
    datos = []
    datos.append(session['carrito']['carrito_producto'])
    datos.append(session['carrito']['carrito_cantidad'])
    datos.append(session['id'])
    requests.post(f'{BACKEND_URL}/subir-compra', json=datos)
    session.pop('carrito', None)
    return redirect(url_for('index'))

@app.route('/eliminar/<id>', methods=['GET', 'POST'])
def eliminar(id):
    carrito = session['carrito']
    
    if carrito['carrito_cantidad'][id] > 1:
        carrito['carrito_cantidad'][id] -= 1
        session['carrito'] = carrito

    else:
        carrito['carrito_cantidad'].pop(id, None)
        carrito['carrito_producto'].pop(id, None)
        session['carrito'] = carrito

    return redirect(request.referrer)

if __name__ == "__main__":
    app.run(debug=True, port=PORT)

    #Computadoras: (datos de la computadora que ya tenemos)
    #Usuarios: (id, mail, nombre, apellido)
    #Compras: (id_usuario, id_pc, precio, imagen, fecha)

    #PERSISTIR SESIONES EN UN TXT