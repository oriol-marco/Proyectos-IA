from flask import Flask, render_template, request, redirect, url_for

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLAlCHEMY_DATABASE_URI'] = 'sqlite:///database/tareas.db'
db = SQLAlchemy(app)


class Tarea(db.Model):
    __tablename__ = "tarea"
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.String(200))
    hecha = db.Column(db.Boolean)


db.create_all()
db.session.commit()


@app.route('/')
def home():
    todas_las_tareas = Tarea_query.all()
    return render_template("index.html", lista_de_tareas=todas_las_tareas)


@app.route('/crear-tarea', methods=['POST'])
def crear():
    tarea = Tarea(contenido=request.form['contenido_tarea'], hecho=False)
    db.session.add(tarea)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/eliminar-tarea/<id>')
def eliminar(id):
    tarea = Tarea.query.filter_by(id=int(id)).delete()

    db.session.commit()
    return redirect(url_for('home'))

@app.route('/tarea-hecha/<id>')
def hecha(id):
    tarea = Tarea.query.filter_by(id=int(id)).first()
    tarea.hecha = not(tarea.hecha)

    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
