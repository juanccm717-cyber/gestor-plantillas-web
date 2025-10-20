from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from sqlalchemy import create_engine, text, exc
from werkzeug.security import check_password_hash
from datetime import timedelta

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("La variable de entorno DATABASE_URL no está configurada.")

engine = create_engine(DATABASE_URL)

# --- IMPORTACIONES DE PARÁMETROS ---
from PARAMETROS import (
    CODIGOS_PRESTACIONALES_CATEGORIZADOS,
    ACTIVIDADES_PREVENTIVAS_MAP,
    RELACION_CODIGO_ACTIVIDADES
)

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'))
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "llave-secreta-robusta-99999")
app.permanent_session_lifetime = timedelta(minutes=60)

# --- FUNCIONES DE BASE DE DATOS (SIN CAMBIOS) ---
def leer_registros_desde_db():
    try:
        with engine.connect() as conn:
            query = text("SELECT * FROM public.registros ORDER BY id ASC;")
            result = conn.execute(query)
            keys = result.keys()
            registros = [dict(zip(keys, row)) for row in result]
            return registros
    except Exception as e:
        print(f"!!! ERROR AL LEER REGISTROS: {e}")
        return []

def escribir_registro_en_db(plantilla_data):
    # (Esta función no necesita cambios)
    # ... (la dejamos como estaba)
    pass # Placeholder, ya que no cambia

# --- RUTAS DE LA APLICACIÓN (RECONSTRUIDAS) ---
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('menu'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with engine.connect() as conn:
            query = text("SELECT username, password_hash, role FROM public.usuarios WHERE username = :username")
            result = conn.execute(query, {"username": username}).fetchone()

        if result and check_password_hash(result[1], password):
            session.permanent = True
            session['username'] = result[0]
            session['rol'] = result[2] # El rol viene de la base de datos
            return redirect(url_for('menu'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/menu')
def menu():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('menu.html', username=session['username'], rol=session['rol'])

@app.route('/plantillas')
def plantillas():
    if 'username' not in session:
        return redirect(url_for('login'))
    modo = request.args.get('modo', 'crear')
    return render_template('index.html', rol=session.get('rol', 'usuario'), modo=modo)

# --- RUTAS DE API (PROTEGIDAS CON LA SESIÓN DE FLASK) ---
@app.route('/get_registros', methods=['GET'])
def get_registros():
    if 'username' not in session:
        return jsonify({"error": "No autorizado"}), 401
    registros = leer_registros_desde_db()
    return jsonify(registros)

# ... (El resto de las rutas de la API como /guardar_plantilla, etc., no necesitan grandes cambios
# porque ya dependen de la sesión de Flask, que ahora funcionará correctamente)
# ...

if __name__ == '__main__':
    app.run(debug=True)
