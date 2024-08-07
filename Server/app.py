from flask import Flask, jsonify, request, redirect, url_for, session, flash
from sqlalchemy import create_engine, text

PORT=8080
app = Flask(__name__)
app.secret_key = 'profetas123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:profetas@localhost:5432/profetas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

@app.route('/obtener-computadoras', methods=['GET']) # app llama a la funcion y el metodo determina si va a recibir o enviar
def obtener_computadoras():
    conexion = engine.connect()
    query = 'SELECT * FROM pcs;'
    resultado = conexion.execute(text(query)) # text da formato, execute ejecuta,  conexion vincuala a la db
    computadoras = []
    for fila in resultado:
        computadora = {
            'idpc': fila.idpc,
            'nombre': fila.nombre,
            'procesador': fila.procesador,
            'gpu': fila.gpu,
            'motherboard': fila.motherboard,
            'ram': fila.ram,
            'almacenamiento': fila.almacenamiento,
            'imagen': fila.imagen,
            'precio': fila.precio,
            'fuente': fila.fuente
        }
        computadoras.append(computadora)
    conexion.close()
    return jsonify(computadoras)

@app.route('/detalles-computadora/<idpc>', methods=['GET'])
def detalles_computadora(idpc):
    conexion = engine.connect()
    query = f'SELECT * FROM pcs WHERE idpc = {idpc};'
    resultado = conexion.execute(text(query))
    for fila in resultado:
        computadora = {
            'idpc': fila.idpc,
            'nombre': fila.nombre,
            'procesador': fila.procesador,
            'gpu': fila.gpu,
            'motherboard': fila.motherboard,
            'ram': fila.ram,
            'almacenamiento': fila.almacenamiento,
            'imagen': fila.imagen,
            'precio': fila.precio,
            'fuente': fila.fuente
        }
    return jsonify(computadora)

@app.route('/registrar-usuario', methods=['POST', 'GET'])
def registrar():
    if request.method == "POST":
        conexion = engine.connect()
        nuevo_usuario = request.json #recibe los datos en formato json

        usuario = nuevo_usuario.get('usuario')
        email = nuevo_usuario.get('email')
        contrasenia = nuevo_usuario.get('contrasenia')
        
        query_email = f"SELECT * FROM users WHERE email = '{email}';"

        resultado_email = conexion.execute(text(query_email)).fetchone()

        if resultado_email:
            conexion.close()
            return jsonify({"mensaje": "Nombre de usuario no disponible"}), 409
        
        query_nuevo_usuario = f"INSERT INTO users (usuario, email, contrasenia) VALUES ('{usuario}', '{email}', '{contrasenia}');"
        conexion.execute(text(query_nuevo_usuario))
        conexion.commit()
        conexion.close()

        return jsonify({'mensaje': 'Se ha registrado el usuario con exito'}), 201

@app.route('/login-user', methods=['POST', 'GET'])
def login():
    conexion = engine.connect()
    log = request.json
    email = log.get('email')
    contrasenia = log.get('contrasenia')

    query_usuario = f"SELECT * FROM users WHERE email = '{email}';"
    resultado = conexion.execute(text(query_usuario)).fetchone()

    if not resultado:
        conexion.close()
        return jsonify({'error': 'No se encontraron usuarios'}), 404
    
    if (contrasenia == resultado.contrasenia):
        user = {
            'id': resultado.id,
            'usuario': resultado.usuario,
            'email': resultado.email,
            'contrasenia': resultado.contrasenia
        }
        conexion.close() #cambio golheth
        return jsonify(user), 200
    
    else:
        conexion.close() #cambio golheth
        return jsonify({"mensaje": "Credenciales inválidas"}), 401

@app.route('/datos-de-usuario/<id>', methods=['GET', 'POST'])
def buscar_datos(id):
    conexion = engine.connect()
    query_usuario = f"SELECT * FROM users WHERE id = '{id}';"
    resultado = conexion.execute(text(query_usuario))
    for fila in resultado:
        user = {
            'id': fila.id,
            'usuario': fila.usuario,
            'email': fila.email,
            'contrasenia': fila.contrasenia
        }
    return jsonify(user)

@app.route('/subir-datos/<id>', methods=['PUT'])
def subir_datos(id):
    conexion = engine.connect()

    log = request.json
    usuario = log.get('usuario')
    email = log.get('email')
    contrasenia = log.get('contrasenia')

    query_usuario = f"UPDATE users SET usuario = '{usuario}', email = '{email}', contrasenia = '{contrasenia}' WHERE id = {id};"
    conexion.execute(text(query_usuario))
    conexion.commit()
    conexion.close() 

@app.route('/delete-user/<id>', methods=['GET', 'DELETE'])
def delete_user(id):
    conexion = engine.connect()
    query_usuario = f"DELETE FROM users WHERE id = '{id}';"
    conexion.execute(text(query_usuario))
    conexion.commit()
    conexion.close()

@app.route('/subir-compra', methods=['GET', 'POST'])
def subir_compra():
    conexion = engine.connect()

    datos = request.json
    productos, pcs_cantidad, userid  = datos[0], datos[1], datos[2]

    query_compra = f"INSERT INTO compras (iduser) VALUES ('{userid}');"
    conexion.execute(text(query_compra))

    query_info_compra = f"SELECT * FROM compras WHERE iduser = '{userid}';"
    compras_user = conexion.execute(text(query_info_compra))

    for idpc, cantidad in pcs_cantidad.items():
        id_pc = str(idpc)
        precio = productos[id_pc]['precio']

        query_info_compra = f"SELECT * FROM compras WHERE iduser = '{userid}';"
        compras_user = conexion.execute(text(query_info_compra))

        idcompras = []
        for fila in compras_user:
            idcompras.append(fila.idcompra)

        print(idcompras)
        idcompra = idcompras[-1]

        precio_total = cantidad*precio
        query_productoscomprados = f"INSERT INTO productoscomprados (idcompra, idpc, cantidad, precio) VALUES ('{idcompra}', '{idpc}', '{cantidad}', {precio_total});"
        conexion.execute(text(query_productoscomprados))

    conexion.commit()
    conexion.close()
    return jsonify({"Mensaje": "Compra exitosa!"}), 201


if __name__ == '__main__':
    app.run(debug=True, port=PORT)
