import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, get_flashed_messages



app = Flask(__name__)
app.secret_key = 'secreto' 
app = Flask(__name__)
app.secret_key = 'secreto'  # Necesario para usar mensajes flash y sesiones

# Ruta para mostrar el formulario de login
@app.route('/login', methods=['GET'])
def login_form():
    messages = get_flashed_messages(with_categories=True)  # Obtener los mensajes flash
    return render_template('login.html', messages=messages)

# Ruta para manejar el formulario de login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Verificar las credenciales con el archivo usuarios.txt
    try:
        with open('usuarios.txt', 'r') as file:
            for line in file:
                id, user, pwd = line.strip().split(';')
                if user == username and pwd == password:
                    session['username'] = username  # Guardar el usuario en la sesión
                    flash('¡Login exitoso!', 'success')  # Mensaje de éxito
                    return redirect(url_for('menu'))  # Redirigir al menú principal
    except FileNotFoundError:
        flash('Archivo de usuarios no encontrado.', 'danger')

    flash('Usuario o contraseña incorrectos', 'danger')  # Mensaje de error
    return redirect(url_for('login_form'))

# Ruta para mostrar el formulario de registro
@app.route('/register', methods=['GET'])
def register_form():
    return render_template('register.html')

# Ruta para manejar el registro
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    
    # Verificar si el usuario ya existe
    try:
        with open('usuarios.txt', 'r') as file:
            for line in file:
                id, user, _ = line.strip().split(';')
                if user == username:
                    flash('El nombre de usuario ya existe. Intenta con otro.', 'danger')
                    return redirect(url_for('register_form'))
    except FileNotFoundError:
        pass  # Si el archivo no existe, seguimos con el registro

    # Asignar un ID único al nuevo usuario
    try:
        with open('usuarios.txt', 'r') as file:
            usuarios = file.readlines()
            if usuarios:
                last_user = usuarios[-1]
                last_id = int(last_user.split(';')[0])
                new_id = last_id + 1
            else:
                new_id = 1  # Si no hay usuarios, el ID inicial es 1
    except FileNotFoundError:
        new_id = 1  # Si el archivo no existe, el primer ID será 1

    # Guardar los datos del nuevo usuario en el archivo usuarios.txt
    try:
        with open('usuarios.txt', 'a') as file:
            file.write(f'{new_id};{username};{password}\n')
        flash(f'Usuario registrado con éxito. Tu ID es {new_id}', 'success')
        return redirect(url_for('login_form'))
    except Exception as e:
        flash(f'Error al registrar: {str(e)}', 'danger')
        return redirect(url_for('register_form'))

# Ruta para el menú principal
@app.route('/menu')
def menu():
    if 'username' in session:
        return render_template('menu.html')
    else:
        flash('Debes iniciar sesión primero', 'danger')
        return redirect(url_for('login_form'))

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('username', None)  # Eliminar el usuario de la sesión
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('login_form'))
# Mostrar clientes cuando sea una petición GET
@app.route('/cliente', methods=['GET', 'POST'])
def gestionar_cliente():
    if request.method == 'POST':
        # Registro de cliente
        nombres = request.form['nombres']
        nit = request.form['nit']
        correo = request.form['correo']
        telefono = request.form['telefono']

        # Generar un ID único para el cliente
        try:
            with open('clientes.txt', 'r') as file:
                clientes = file.readlines()
                if clientes:
                    last_cliente = clientes[-1]
                    last_id = int(last_cliente.split(';')[0])
                    new_id = last_id + 1
                else:
                    new_id = 1
        except FileNotFoundError:
            new_id = 1

        # Guardar los datos del cliente en el archivo clientes.txt
        try:
            with open('clientes.txt', 'a') as file:
                file.write(f'{new_id};{nombres};{nit};{correo};{telefono}\n')
            flash(f'Cliente registrado con éxito. Código: {new_id}', 'success')
        except Exception as e:
            flash(f'Error al registrar cliente: {str(e)}', 'danger')

        return redirect(url_for('gestionar_cliente'))

    # Si es una petición GET, mostramos los clientes registrados
    print("Entrando en el método GET para mostrar clientes...")  # Para verificar si entra aquí
    clientes = []
    try:
        with open('clientes.txt', 'r') as file:
            for line in file:
                id, nombres, nit, correo, telefono = line.strip().split(';')
                clientes.append({
                    'id': id,
                    'nombres': nombres,
                    'nit': nit,
                    'correo': correo,
                    'telefono': telefono
                })
    except FileNotFoundError:
        flash('No se encontraron clientes registrados.', 'info')

    return render_template('cliente.html', clientes=clientes)

# Ruta para eliminar un cliente
@app.route('/eliminar_cliente/<int:id>')
def eliminar_cliente(id):
    clientes = []
    try:
        with open('clientes.txt', 'r') as file:
            clientes = [line.strip().split(';') for line in file]
        
        # Filtrar el cliente que se quiere eliminar
        clientes = [cliente for cliente in clientes if int(cliente[0]) != id]
        
        # Reescribir el archivo sin el cliente eliminado
        with open('clientes.txt', 'w') as file:
            for cliente in clientes:
                file.write(';'.join(cliente) + '\n')
                
        flash('Cliente eliminado con éxito', 'danger')
    except Exception as e:
        flash(f'Error al eliminar cliente: {str(e)}', 'danger')

    return redirect(url_for('gestionar_cliente'))

@app.route('/editar_cliente/<int:id>', methods=['GET'])
def editar_cliente(id):
    # Leer el archivo y buscar el cliente por ID
    try:
        with open('clientes.txt', 'r') as file:
            for line in file:
                cliente_id, nombres, nit, correo, telefono = line.strip().split(';')
                if int(cliente_id) == id:
                    # Si se encuentra el cliente, devolver los datos en formato JSON
                    return {
                        'id': cliente_id,
                        'nombres': nombres,
                        'nit': nit,
                        'correo': correo,
                        'telefono': telefono
                    }
    except FileNotFoundError:
        return {'error': 'Archivo de clientes no encontrado'}, 404

    # Si no se encuentra el cliente
    return {'error': 'Cliente no encontrado'}, 404


@app.route('/modificar_cliente', methods=['POST'])
def modificar_cliente():
    cliente_id = request.form['id']
    nombres = request.form['nombres']
    nit = request.form['nit']
    correo = request.form['correo']
    telefono = request.form['telefono']

    # Leer todos los clientes
    clientes = []
    try:
        with open('clientes.txt', 'r') as file:
            clientes = [line.strip().split(';') for line in file]

        # Modificar los datos del cliente específico
        with open('clientes.txt', 'w') as file:
            for cliente in clientes:
                if cliente[0] == cliente_id:  # Verifica que coincida el ID del cliente
                    file.write(f'{cliente_id};{nombres};{nit};{correo};{telefono}\n')
                else:
                    file.write(';'.join(cliente) + '\n')

        flash('Cliente modificado con éxito', 'success')
    except Exception as e:
        flash(f'Error al modificar cliente: {str(e)}', 'danger')

    return redirect(url_for('gestionar_cliente'))


# RUTA PARA GESTIONAR PRODUCTOS (REGISTRO Y LISTA)
@app.route('/producto', methods=['GET', 'POST'])
def gestionar_producto():
    if request.method == 'POST':
        # Registro de producto
        nombre_producto = request.form['nombre_producto']
        precio = request.form['precio']
        cantidad = request.form['cantidad']

        # Generar un ID único para el producto
        try:
            with open('productos.txt', 'r') as file:
                productos = file.readlines()
                if productos:
                    last_producto = productos[-1]
                    last_id = int(last_producto.split(';')[0])
                    new_id = last_id + 1
                else:
                    new_id = 1
        except FileNotFoundError:
            new_id = 1

        # Guardar los datos del producto en el archivo productos.txt
        try:
            with open('productos.txt', 'a') as file:
                file.write(f'{new_id};{nombre_producto};{precio};{cantidad}\n')
            flash(f'Producto registrado con éxito. Código: {new_id}', 'success')
        except Exception as e:
            flash(f'Error al registrar producto: {str(e)}', 'danger')

        return redirect(url_for('gestionar_producto'))

    # Mostrar productos registrados (GET)
    productos = []
    try:
        with open('productos.txt', 'r') as file:
            for line in file:
                id, nombre_producto, precio, cantidad = line.strip().split(';')
                productos.append({
                    'id': id,
                    'nombre_producto': nombre_producto,
                    'precio': precio,
                    'cantidad': cantidad
                })
    except FileNotFoundError:
        flash('No se encontraron productos registrados.', 'info')

    return render_template('producto.html', productos=productos)

# RUTA PARA ELIMINAR PRODUCTO
@app.route('/eliminar_producto/<int:id>')
def eliminar_producto(id):
    productos = []
    try:
        with open('productos.txt', 'r') as file:
            productos = [line.strip().split(';') for line in file]

        productos = [producto for producto in productos if int(producto[0]) != id]

        # Reescribir el archivo sin el producto eliminado
        with open('productos.txt', 'w') as file:
            for producto in productos:
                file.write(';'.join(producto) + '\n')

        flash('Producto eliminado con éxito', 'success')
    except Exception as e:
        flash(f'Error al eliminar producto: {str(e)}', 'danger')

    return redirect(url_for('gestionar_producto'))

# RUTA PARA MODIFICAR PRODUCTO
@app.route('/modificar_producto', methods=['POST'])
def modificar_producto():
    producto_id = request.form['id']
    nombre_producto = request.form['nombre_producto']
    precio = request.form['precio']
    cantidad = request.form['cantidad']

    productos = []
    try:
        with open('productos.txt', 'r') as file:
            productos = [line.strip().split(';') for line in file]

        with open('productos.txt', 'w') as file:
            for producto in productos:
                if producto[0] == producto_id:
                    file.write(f'{producto_id};{nombre_producto};{precio};{cantidad}\n')
                else:
                    file.write(';'.join(producto) + '\n')

        flash('Producto modificado con éxito', 'success')
    except Exception as e:
        flash(f'Error al modificar producto: {str(e)}', 'danger')

    return redirect(url_for('gestionar_producto'))

# RUTA PARA EDITAR PRODUCTO
@app.route('/editar_producto/<int:id>', methods=['GET'])
def editar_producto(id):
    try:
        with open('productos.txt', 'r') as file:
            for line in file:
                producto_id, nombre_producto, precio, cantidad = line.strip().split(';')
                if int(producto_id) == id:
                    return {
                        'id': producto_id,
                        'nombre_producto': nombre_producto,
                        'precio': precio,
                        'cantidad': cantidad
                    }
    except FileNotFoundError:
        return {'error': 'Archivo de productos no encontrado'}, 404

    return {'error': 'Producto no encontrado'}, 404
 # Necesario para usar mensajes flash y sesiones

# Ruta para gestionar la creación de una nueva factura
@app.route('/factura', methods=['GET', 'POST'])
def gestionar_factura():
    if request.method == 'POST':
        # Obtener los datos del formulario
        cliente_id = request.form['cliente_id']
        productos_seleccionados = request.form.getlist('productos')
        cantidades = request.form.getlist('cantidades')

        # Obtener el cliente por ID
        try:
            with open('clientes.txt', 'r') as file:
                for line in file:
                    id, nombres, nit, correo, telefono = line.strip().split(';')
                    if id == cliente_id:
                        cliente_nombre = nombres
                        cliente_nit = nit
                        break
        except FileNotFoundError:
            flash('No se encontró el archivo de clientes.', 'danger')
            return redirect(url_for('gestionar_factura'))

        # Generar la factura con los productos y el total
        factura_detalles = []
        total_general = 0
        try:
            with open('productos.txt', 'r') as file:
                productos = [line.strip().split(';') for line in file]

            for i, producto_id in enumerate(productos_seleccionados):
                for producto in productos:
                    if producto[0] == producto_id:
                        nombre_producto = producto[1]
                        precio_unitario = float(producto[2])
                        cantidad = int(cantidades[i])
                        total_producto = precio_unitario * cantidad
                        total_general += total_producto
                        factura_detalles.append({
                            'nombre': nombre_producto,
                            'precio_unitario': precio_unitario,
                            'cantidad': cantidad,
                            'total': total_producto
                        })

        except FileNotFoundError:
            flash('No se encontró el archivo de productos.', 'danger')
            return redirect(url_for('gestionar_factura'))

        # Obtener la fecha y hora actual
        fecha_hora_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return render_template('factura.html', cliente_nombre=cliente_nombre, cliente_nit=cliente_nit,
                               factura_detalles=factura_detalles, total_general=total_general,
                               fecha_hora_actual=fecha_hora_actual)

    # Obtener todos los clientes y productos para mostrar en el formulario
    clientes = []
    productos = []
    try:
        with open('clientes.txt', 'r') as file:
            for line in file:
                id, nombres, nit, correo, telefono = line.strip().split(';')
                clientes.append({'id': id, 'nombres': nombres})

        with open('productos.txt', 'r') as file:
            for line in file:
                id, nombre, precio, cantidad = line.strip().split(';')
                productos.append({'id': id, 'nombre': nombre, 'precio': precio, 'cantidad': cantidad})

    except FileNotFoundError:
        flash('No se encontraron los archivos necesarios.', 'danger')

    return render_template('crear_factura.html', clientes=clientes, productos=productos)




if __name__ == '__main__':
    app.run(debug=True)