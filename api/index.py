from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from datetime import timedelta

# No es necesario tocar las importaciones, ya están correctas.
from PARAMETROS import (
    CODIGOS_PRESTACIONALES_CATEGORIZADOS,
    ACTIVIDADES_PREVENTIVAS_MAP,
    RELACION_CODIGO_ACTIVIDADES
)

# ======================================================================
# CORRECCIÓN FINAL Y DEFINITIVA
# ======================================================================
# 1. Obtener la ruta del directorio raíz del proyecto (un nivel arriba de 'api/')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. Al crear la aplicación Flask, le decimos explícitamente dónde buscar las plantillas.
app = Flask(__name__, template_folder=os.path.join(PROJECT_ROOT, 'templates'))
# ======================================================================

app.secret_key = 'tu_super_secreta_llave_aqui'
app.permanent_session_lifetime = timedelta(minutes=60)

# --- MANEJO DE DATOS ---

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE_PATH = os.path.join(BASE_DIR, 'registros.json')

def leer_registros_desde_archivo():
    if not os.path.exists(JSON_FILE_PATH):
        return []
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content: return []
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return []

def escribir_registros_a_archivo(registros):
    try:
        with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(registros, f, indent=4)
    except IOError as e:
        print(f"Error al escribir en el archivo: {e}")


# --- RUTAS DE AUTENTICACIÓN Y MENÚ (Sin cambios) ---

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('menu'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        rol = request.form.get('rol', 'viewer')
        session.permanent = True
        session['username'] = username
        session['rol'] = rol
        return redirect(url_for('menu'))
    # Esta línea ahora funcionará porque le dijimos a Flask dónde está la carpeta 'templates'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('rol', None)
    return redirect(url_for('login'))

@app.route('/menu')
def menu():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('menu.html', username=session['username'], rol=session['rol'])


# --- RUTAS PRINCIPALES DE LA APLICACIÓN (Sin cambios) ---

@app.route('/plantillas')
def plantillas():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', rol=session.get('rol', 'viewer'))

@app.route('/guardar_plantilla', methods=['POST'])
def guardar_plantilla():
    if 'username' not in session or session.get('rol') != 'admin':
        return jsonify({'message': 'Acceso no autorizado.'}), 403
    nueva_plantilla = request.json
    if not nueva_plantilla.get('codigo_prestacional'):
        return jsonify({'message': 'El código prestacional es obligatorio.'}), 400
    registros = leer_registros_desde_archivo()
    nueva_plantilla['id'] = len(registros) + 1
    registros.append(nueva_plantilla)
    escribir_registros_a_archivo(registros)
    return jsonify({'message': f"Plantilla guardada con éxito con ID: {nueva_plantilla['id']}"}), 201


# --- RUTAS DE API (Sin cambios) ---

@app.route('/get_registros', methods=['GET'])
def get_registros():
    if 'username' not in session: return jsonify({'message': 'No autorizado'}), 401
    return jsonify(leer_registros_desde_archivo())

@app.route('/search_codigos', methods=['GET'])
def search_codigos():
    if 'username' not in session: return jsonify({'suggestions': []}), 401
    query = request.args.get('query', '').lower()
    suggestions = [s for s in CODIGOS_PRESTACIONALES_CATEGORIZADOS if query in s['codigo'].lower() or query in s['descripcion'].lower()]
    return jsonify({'suggestions': suggestions})

@app.route('/get_actividades_por_codigo/<string:codigo>', methods=['GET'])
def get_actividades_por_codigo(codigo):
    if 'username' not in session: return jsonify({'actividades': []}), 401
    codigos_actividad = RELACION_CODIGO_ACTIVIDADES.get(codigo, RELACION_CODIGO_ACTIVIDADES.get('DEFAULT', []))
    actividades_sugeridas = [{'codigo': c, 'descripcion': ACTIVIDADES_PREVENTIVAS_MAP.get(c, 'Descripción no encontrada')} for c in sorted(list(codigos_actividad))]
    return jsonify({'actividades': actividades_sugeridas})

if __name__ == '__main__':
    app.run(debug=True)
