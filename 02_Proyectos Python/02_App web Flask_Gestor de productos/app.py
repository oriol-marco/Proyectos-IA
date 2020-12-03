from tkinter import ttk
from tkinter import *
import sqlite3


class Producto:

    def __init__(self, root):
        self.ventana = root
        self.ventana.title("App Gestor de Productos")
        self.ventana.resizable(1,1)
        self.ventana.iconbitmap('recursos/icon.ico')

        frame = LabelFrame(self.ventana, text = "Registrar un nuevo Producto", font=('Calibri', 16, 'bold'))
        frame.grid(row = 0, column = 0, columnspan = 3, pady = 20)

        self.etiqueta_nombre = Label(frame, text="Nombre: ", font = ('Calibri', 13))
        self.etiqueta_nombre.grid(row=1, column=0)
        self.nombre = Entry(frame, font = ('Calibri', 13))
        self.nombre.focus()
        self.nombre.grid(row=1, column=1)

        self.etiqueta_precio = Label(frame, text="Precio: ", font = ('Calibri', 13))
        self.etiqueta_precio.grid(row=2, column=0)
        self.precio = Entry(frame, font = ('Calibri', 13))
        self.precio.grid(row=2, column=1)

        s = ttk.Style()
        s.configure('my.TButton', font=('Calibri', 14, 'bold'))
        self.boton_aniadir = ttk.Button(frame, text = "Guardar Producto", command = self.add_producto, style='my.TButton')
        self.boton_aniadir.grid(row = 3, columnspan = 2, sticky =W +E)

        style = ttk.Style()
        style.configure("mystyle.Treeview", hightlightthickness=0, bd=0, font=('Calibri', 11))
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 13, 'bold'))
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

        self.tabla = ttk.Treeview(height =20, column =2, style="mystyle.Treeview")
        self.tabla.grid(row=4, column=0, columnspan =2)
        self.tabla.heading('#0', text = 'Nombre', anchor = CENTER)
        self.tabla.heading('#1', text = 'Precio', anchor = CENTER)

        self.mensaje = Label(text = '', fg = 'red')
        self.mensaje.grid(row = 3, column = 0, columnspan = 2, sticky = W + E)

        s = ttk.Style()
        s.configure('my.TButton', font=('Calibri', 14, 'bold'))
        boton_eliminar = ttk.Button(text = 'ELIMINAR', command = self.del_producto, style='my.TButton')
        boton_eliminar.grid(row = 5, column = 0, sticky = W + E)

        s = ttk.Style()
        s.configure('my.TButton', font=('Calibri', 14, 'bold'))
        boton_editar = ttk.Button(text = 'EDITAR', command = self.edit_producto, style= 'my.TButton')
        boton_editar.grid(row = 5, column = 1, sticky = W + E)


    db = 'database/productos.db'

    def db_consulta(self, consulta, parametros=()):
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            resultado = cursor.execute(consulta, parametros)
            con.commit()
        return resultado

    def get_productos(self):

        registros_tabla = self.tabla.get_children()
        for fila in registros_tabla:
            self.tabla.delete(fila)

        query = 'SELECT * FROM producto ORDER BY nombre DESC'

        registros_db = self.db_consulta(query)
        for fila in registros_db:
            print(fila)
            self.tabla.insert('', 0, text=fila[1], values=fila[2])

        #self.get_productos()
        # # En este punto si le doy a refresh en el DB Browser me actualiza el producto introducido pero me sale
        # error al ejecutar la app.py


    def validacion_nombre(self):
        nombre_introducido_por_usuario = self.nombre.get()
        return len(nombre_introducido_por_usuario) != 0

    def validacion_precio(self):
        precio_introducido_por_usuario = self.precio.get()
        return len(precio_introducido_por_usuario) != 0

    def add_producto(self):
        if self.validacion_nombre() and self.validacion_precio():
            query = 'INSERT INTO producto VALUES(NULL, ?, ?)'
            parametros = (self.nombre.get(), self.precio.get())
            self.db_consulta(query, parametros)
            print("Datos guardados")
            self.mensaje['text'] = 'Producto {} añadido con exito'.format(self.nombre.get())
            self.nombre.delete(0, END)
            self.precio.delete(0, END)

        elif self.validacion_nombre() and self.validacion_precio() == False:
            print("El precio es obligatorio")
            self.mensaje['text'] = 'El precio es obligatorio'
        elif self.validacion_nombre() == False and self.validacion_precio():
            print("El nombre es obligatorio")
            self.mensaje['text'] = 'El nombre es bligatorio'
        else:
            print("El nombre y el precio son obligatorios")
            self.mensaje['text'] = 'El nombre y el precio son obligatorios'

        self.get_productos()

    def del_producto(self):
        #Debug
        #print(self.tabla.item(self.tabla.selection()))
        #print(self.tabla.item(self.tabla.selection())['text'])
        #print(self.tabla.item(self.tabla.selection())['values'])
        #print(self.tabla.item(self.tabla.selection())['values'][0])

        self.mensaje['text'] = ''

        try:
            self.tabla.item(self.tabla.selection())['text'][0]
        except IndexError as e:
            self.mensaje['text'] = 'Por favor, selecciona un producto'
            return

        self.mensaje['text'] = ''
        nombre = self.tabla.item(self.tabla.selection())['text']
        query = 'DELETE FROM producto WHERE nombre = ?'
        self.db_consulta(query, (nombre,))
        self.mensaje['text'] = 'Producto {} eliminado con exito'.format(nombre)
        self.get_productos()

    def edit_producto(self):
        self.mensaje['text'] = ''

        try:
            self.tabla.item(self.tabla.selection())['text'][0]
        except IndexError as e:
            self.mensaje['text'] = 'Por favor, selecciona un producto'
            return

        nombre = self.tabla.item(self.tabla.selection())['text']
        old_precio = self.tabla.item(self.tabla.selection())['values'][0]

        #Ventana nueva EDITAR

        self.ventana_editar = Toplevel()
        self.ventana_editar.title = "Editar Producto"
        self.ventana_editar.resizable(1,1)
        self.ventana_editar.wm_iconbitmap('recursos/icon.ico')

        titulo = Label(self.ventana_editar, text = 'Edición de Productos', font=('Calibri', 50, 'bold'))
        titulo.grid(column = 0, row = 0)

        frame_ep = LabelFrame(self.ventana_editar, text = "Editar el siguiente Producto", font = ('Calibri', 16, 'bold'))
        frame_ep.grid(row = 1, column = 0, columnspan = 20, pady = 20)

        self.etiqueta_nombre_antiguo = Label(frame_ep, text = "Nombre Antiguo: ", font = ('Calibri', 13))
        self.etiqueta_nombre_antiguo.grid(row = 2, column = 0)
        self.input_nombre_antiguo = Entry(frame_ep, textvariable=StringVar(self.ventana_editar, value=nombre), state= 'readonly', font = ('Calibri', 13))
        self.input_nombre_antiguo.grid(row = 2, column = 1)

        self.etiqueta_nombre_nuevo = Label(frame_ep, text="Nombre Nuevo: ", font = ('Calibri', 13))
        self.etiqueta_nombre_nuevo.grid(row=3, column=0)
        self.input_nombre_nuevo = Entry(frame_ep, font = ('Calibri', 13))
        self.input_nombre_nuevo.grid(row=3, column=1)
        self.input_nombre_nuevo.focus()

        self.etiqueta_precio_antiguo = Label(frame_ep, text="Precio Antiguo: ", font = ('Calibri', 13))
        self.etiqueta_precio_antiguo.grid(row=4, column=0)
        self.input_precio_antiguo = Entry(frame_ep, textvariable=StringVar(self.ventana_editar, value=old_precio), state='readonly', font = ('Calibri', 13))
        self.input_precio_antiguo.grid(row=4, column=1)

        self.etiqueta_precio_nuevo = Label(frame_ep, text="Precio Nuevo: ", font = ('Calibri', 13))
        self.etiqueta_precio_nuevo.grid(row=5, column=0),
        self.input_precio_nuevo = Entry(frame_ep, font = ('Calibri', 13))
        self.input_precio_nuevo.grid(row=5, column=1),

        s = ttk.Style()
        s.configure('my.TButton', font=('Calibri', 14, 'bold'))
        self.boton_actualizar = ttk.Button(frame_ep, text= "Actualizar Producto", style='my.TButton', command = lambda:
        self.actualizar_productos(self.input_nombre_nuevo.get(),
        self.input_nombre_antiguo.get(),
        self.input_precio_nuevo.get(),
        self.input_precio_antiguo.get()))

        self.boton_actualizar.grid(row = 6, columnspan = 2, sticky = W + E)

    def actualizar_productos(self, nombre_nuevo, nombre_antiguo, precio_nuevo, precio_antiguo):
        producto_modificado = False
        query ='UPDATE producto SET nombre = ?, precio = ?, WHERE nombre = ? AND precio = ?'
        if nombre_nuevo != '' and precio_nuevo != '':
            parametros = (nombre_nuevo, precio_nuevo, nombre_antiguo, precio_antiguo)
            producto_modificado = True
        elif nombre_nuevo != '' and precio_nuevo != '':
            parametros = (nombre_nuevo, precio_antiguo, nombre_antiguo, precio_antiguo)
            producto_modificado = True
        elif nombre_nuevo == '' and precio_nuevo != '':
            parametros = (nombre_antiguo, precio_nuevo, nombre_antiguo, precio_antiguo)
            producto_modificado = True
        if(producto_modificado):
            self.db_consulta(query, parametros)
            self.ventana_editar.destroy()
            self.mensaje['text'] = 'El Producto {} ha sido actualizado con éxito'.format(nombre_antiguo)
            self.get_productos()
        else:
            self.ventana_editar.destroy()
            self.mensaje['text'] = 'El Producto {} NO ha sido actualizado'.format(nombre_antiguo)



if __name__ == '__main__':
    root = Tk()
    app = Producto(root)
    root.mainloop()

# ## Me abre bien el programa pero al actualizar un precio y/o nombre de un producto, me salen diferentes errores
# relacionados con la consulta SQL!!!!


