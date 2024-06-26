from app import app, productos,categorias,usuarios
from flask import render_template,request,jsonify,redirect,url_for,session
import yagmail
import os
from bson.objectid import ObjectId
import base64
from io import BytesIO
from pymongo.errors import PyMongoError
import threading

 

     
# creo la ruta raiz
@app.route('/', methods=["POST", "GET"])
def inicio():
    #obtengo los datos del nuevo usuario creado enviados por la url
    mensajeUser = request.args.get('mensajeUser')
    mensaje2= request.args.get('mensaje2')
    mensaje3= request.args.get('mensaje3')
    
    
    #/////////
    listaProductos=productos.find()
    listaP=[]
    print(listaP)
    
    for p in listaProductos:
        categoria=categorias.find_one({'_id':ObjectId(p['categoria'])})
        if p['categoria'] == categoria['_id']:
           p['categoria'] = categoria['nombre']
           listaP.append(p)
    
    return render_template("login.html",mensaje2=mensaje2,mensaje3=mensaje3, mensajeUser=mensajeUser, productos=listaP, MostrarProductos=listaProductos)


#///////////////////Validar Datos del Login/////////////////////////

@app.route('/datosLogin', methods=["POST"])
def inicioLogin():
    
    #/////////// USER ///////////
    
    # correo: onix7kingdom@gmail.com
    # password='eadtgrufikokctph'

    #/////////// USER 2 ///////////
    
    # correo; onix8kingdom@gmail.com
    # password='54321'
    
    #//////////////////////
    estado = False
    mensaje = ''
    emailLogin = request.form["correo"]
    password = request.form["contraseña"]
    user=usuarios.find()
    Productos=productos.find()
    listCategorias=categorias.find()
    

    try:
        for u in user:
            converContraseña= str(u['contraseña'])
            
            # se valida si el usuario existe en la base de datos 
            if u['correo'] == emailLogin and converContraseña == password:
                
                # se crea la variable de la sesion
                session['user']=emailLogin
                
                # cambia la variable estado para que renderice la pagina listarProductos
                estado = True
                mensaje = f'Bienvenid@ {u["nombre"]}'
                
                #////////// Enviar correo///////////////
                
                # email=yagmail.SMTP(emailLogin, password, encoding='UTF-8')
                # asunto='Reporte ingreso al sistema'
                # mensajeCorreo=f'Me permito informar que el usuario <b>{u['nombre']}</b> ha ingresado al sistema'
                # se envia un correo a la persona que ingresa a la app
                # email.send(to=emailLogin, subject=asunto, contents=mensajeCorreo)
                
                # ////////////// Enviar correo con thread para enviar en eparalelo/////////////
                
                # def enviarCorreo(email=None, destinatario=None, asunto=None, mensajeCorreo=None):
                #     email.send(to=emailLogin, subject=asunto, contents=mensaje)
                
                # la funcion thread permite realizar operaciones en paralelo, resive una funcion a realizar y los argumentos
                # thread=threading,thread(target=enviarCorreo, args=(email,emailLogin,asunto,mensajeCorreo))
                # thread.start()
                
                break  
    
        if Productos:
            mensaje2='Tus productos'
        else:
            mensaje2='No tienes productos'
            
        if estado:
            return render_template('listarProductos.html', mensaje=mensaje,mensaje2=mensaje2, Productos=Productos, listCategorias=listCategorias)
        else:
            mensaje2 = 'Correo o contraseña incorrectos'
        
            
    except PyMongoError as error:
        mensaje2=error
        
    return redirect(url_for('inicio', mensaje2=mensaje2))


#//////////////////// Crear cuenta ///////////////////

@app.route('/mostrarFormLogin', methods=["GET","POST"])
def mostrarFormLogin():
    return render_template('crearCuenta.html')


# //////////////// Envio de datos nuevo usuario a db////////////
        
@app.route('/crearUsuario', methods=["POST","GET"])
def crearUsuario():
    mensajeUser=''
    nombre= request.form['nombre']
    correo=request.form['correo']
    contraseña=request.form['contraseña']
    comprobar=usuarios.find_one({"correo":correo,"contraseña":contraseña})
    if comprobar:
        mensajeUser='Ya existe usuario con ese correo'
    else:
        mensajeUser='Registro exitoso'
        #inserto al nuevo usuario en la bd
        usuarios.insert_one({"nombre":nombre,"correo":correo, "contraseña":contraseña})
    return redirect(url_for('inicio',mensajeUser=mensajeUser))




# //////////////  vistaAgregarProducto ///////////////////////////////////////////

@app.route("/vistaAgregarProducto")
def vistaAgregarProducto():
    if("user" in session):
        listaCategorias=categorias.find()
        mensaje='Agrega un nuevo producto'
        return render_template("fmAgregarProductos.html", categorias=listaCategorias,mensaje=mensaje)
    else:
        mensaje3='Metodo invalido, por favor inicie sesión'
        return redirect(url_for("inicio",mensaje3=mensaje3))  
    



# ///////////////// agregarProducto ////////////////////////////////////////

@app.route("/agregarProducto", methods=["POST", "GET"])
def agregarProducto():
    if("user" in session):
        mensaje=None
        estado=False
        listCategorias=categorias.find()
        try:
            codigo =int(request.form["codigo"]) 
            nombre = request.form["nombre"]
            precio = int(request.form["precio"])
            idCategoria = request.form["categoria"]
            foto =request.files["fileFoto"]
            # idCliente=usuarios.find_one({"correo":})
            
                
            producto={
                'codigo':codigo,
                'nombre':nombre,
                'precio':precio,
                'categoria':ObjectId(idCategoria),
      
            }
            
            # /////////////// listar productos decodificados
            Productos=productos.find()
              
            pBusquedad=productos.find_one({"codigo":codigo})
            if not pBusquedad:
                resultado= productos.insert_one(producto)
                
                if (resultado.acknowledged):
                    idProducto= ObjectId(resultado.inserted_id)
                    nombreFoto=f"{idProducto}.jpg"
                    # esto guarda la foto en el disco
                    foto.save(os.path.join(app.config["UPLOAD_FOLDER"], nombreFoto))
                    estado=True
                    mensaje='Producto agregado correctamentre.'
                else:
                    mensaje='problemas al agregar el producto'
                
            if Productos:
                mensaje='Tus productos'
            else:
                mensaje='No tienes productos'
                
                
            return render_template('listarProductos.html',estado=estado, mensaje= mensaje, Productos=Productos, listCategorias=listCategorias)
        except PyMongoError as error:
            mensaje= error
    else:
        mensaje3='Metodo invalido, por favor inicie sesión'
        return redirect(url_for("inicio",mensaje3=mensaje3))  
    
    
# /////////// consultar producto////////////////////

@app.route('/consultar/<codigoP>', methods=['GET'])
def cosultarPorCodigo(codigoP):
    if("user" in session):
        estado=False
        mensaje=None
        producto=None
        conver=int(codigoP)
        try:
            ResultadoProducto= productos.find_one({'codigo':conver})
    
        except PyMongoError as error:
            mensaje=error
        queryCategoria=categorias.find_one({'_id':ResultadoProducto['categoria']})
        listaCategorias=categorias.find()
        return render_template('editarProducto.html', productos=ResultadoProducto,queryCategoria=queryCategoria, listaCategorias=listaCategorias )
    else:
        mensaje3='Metodo invalido, por favor inicie sesión'
        return redirect(url_for("inicio",mensaje3=mensaje3))
    

#//////////// editar /////////////////////

@app.route('/editar', methods=['POST',"GET"])
def editar():
    if("user" in session):
        estado=False
        mensaje=None
        try:
            codigo =int(request.form["codigo"]) 
            nombre = request.form["nombre"]
            precio = int(request.form["precio"])
            idCategoria = request.form["categoria"]
            foto =request.files["fileFoto"]
            # inputHidden= ObjectId(request.files["inputHidden"])
            
            producto={
                'codigo':codigo,
                'nombre':nombre,
                'precio':precio,
                'categoria':ObjectId(idCategoria)
            }
            
            
            # actualizando la base de datos con el id
            resultado= productos.update_one({"codigo":codigo},{"$set":producto})
            
            if (resultado.acknowledged):
                if(foto):
                    # nombreFoto= f'{inputHidden}.jpg'
                    foto.save(os.path.join(app.config["UPLOAD_FOLDER"]))
                
                mensaje='Producto actualizado correctamentre.'
            else:
                mensaje='problemas al actualizar el producto'
            
            Productos=productos.find()
            
        except PyMongoError as error:
            mensaje=error
        return render_template('listarProductos.html', Productos=Productos , mensaje=mensaje)
    else:
        mensaje3='Metodo invalido, por favor inicie sesión'
        return redirect(url_for("inicio",mensaje3=mensaje3))
    
#////////////////// Eliminar ///////////////////////

@app.route('/eliminar/<codigo>', methods=['GET'])
def eliminar_producto(codigo):
    if("user" in session):
        
        try:
            # Convertir el código a un entero
            codigo = int(codigo)
            
            # Buscar el producto en la base de datos por su código
            producto = productos.find_one({"codigo": codigo})
            prod=productos.find()
            if producto:
                # Si se encuentra el producto, eliminarlo de la base de datos
                productos.delete_one({"codigo": codigo})
                mensaje = f"El producto con código {codigo} ha sido eliminado exitosamente."
            
            if prod:
                mensaje='Tus productos'
            else:
                mensaje='No tienes productos'
                
        except Exception as e:
            mensaje = f"Error al eliminar el producto: {str(e)}"
    
        # Redireccionar a la página de listar productos con un mensaje
        return render_template('listarProductos.html', mensaje=mensaje, Productos=prod)
    else:
        mensaje3='Metodo invalido, por favor inicie sesión'
        return redirect(url_for("inicio",mensaje3=mensaje3))
    
# ////////////////////// Cerrar sesión ////////////////////////////

@app.route("/salir")
def salir():
    # session.clear()
    
    # Si la clave 'user' está presente en la sesión, esta función (pop()) la eliminará y devolverá su valor. Si la clave no está presente, devolverá None.
    session.pop('user', None)
    
    # Se establece una variable de sesión para mostrar el mensaje
    # el cual se validara si es true o false e en scritp del login.thml
    session['salir'] = True 
    return redirect('/')



# @app.route('/agregarProductoJson')
# def agregarProductoJson():
#     estado=False
#     mensaje=None
#     resultado= productos.insert_one(producto)
#     if (resultado.acknowledged):
#         rutaImagen=f"{os.path.join(app.config["UPLOAD_FOLDER"])}/{ producto['_id']}.jpg"   
#         estado=True
#         mensaje='Producto agregado correctamentre.'
#     else:
#         mensaje='problemas al agregar el producto'
    
