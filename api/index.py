from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from datetime import timedelta
import sys # Importar la librería del sistema

# ======================================================================
# CORRECCIÓN CRÍTICA PARA EL DESPLIEGUE EN VERCEL
# ======================================================================
# 1. Obtener la ruta del directorio raíz del proyecto.
#    os.path.dirname(__file__) es el directorio 'api'.
#    os.path.dirname(...) de eso nos da el directorio raíz.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. Añadir el directorio raíz a las rutas de búsqueda de Python.
#    Esto asegura que Python pueda encontrar 'PARAMETROS.py' sin importar cómo se ejecute.
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
# ======================================================================

# Ahora, la importación de PARAMETROS será siempre exitosa.
from PARAMETROS import (
    CODIGOS_PRESTACIONALES_CATEGORIZADOS,
    ACTIVIDADES_PREVENTIVAS_MAP,
    RELACION_CODIGO_ACTIVIDADES
)

app = Flask(__name__)
app.secret_key = 'tu_super_secreta_llave_aqui'
app.permanent_session_lifetime = timedelta(minutes=60)

# --- MANEJO DE DATOS ---

# La ruta al archivo JSON ahora se construye desde la raíz del proyecto
# para ser más explícita, aunque la lógica anterior también funcionaría
# con la corrección de sys.path.
JSON_FILE_PATH = os.path.join(PROJECT_ROOT, 'api', 'registros.json')

def leer_registros_desde_archivo():
    """Función robusta para leer el archivo JSON."""
    if not os.path.exists(JSON_FILE_PATH):
        return []
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return []

def escribir_registros_a_archivo(registros):
    """Función para escribir en el archivo JSON."""
    try:
        with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(registros, f, indent=4)
    except IOError as e:
        print(f"Error al escribir en el archivo: {e}")


# --- RUTAS DE AUTENTICACIÓN Y MENÚ ---

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


# --- RUTAS PRINCIPALES DE LA APLICACIÓN ---

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


# --- RUTAS DE API (PARA OBTENER DATOS) ---

@app.route('/get_registros', methods=['GET'])
def get_registros():
    if 'username' not in session:
        return jsonify({'message': 'No autorizado'}), 401
    
    registros = leer_registros_desde_archivo()
    return jsonify(registros)

@app.route('/search_codigos', methods=['GET'])
def search_codigos():
    if 'username' not in session:
        return jsonify({'suggestions': []}), 401
    
    query = request.args.get('query', '').lower()
    suggestions = [
        s for s in CODIGOS_PRESTACIONALES_CATEGORIZADOS
        if query in s['codigo'].lower() or query in s['descripcion'].lower()
    ]
    return jsonify({'suggestions': suggestions})

@app.route('/get_actividades_por_codigo/<string:codigo>', methods=['GET'])
def get_actividades_por_codigo(codigo):
    if 'username' not in session:
        return jsonify({'actividades': []}), 401

    codigos_actividad = RELACION_CODIGO_ACTIVIDADES.get(codigo, RELACION_CODIGO_ACTIVIDADES.get('DEFAULT', []))
    actividades_sugeridas = [
        {'codigo': c, 'descripcion': ACTIVIDADES_PREVENTIVAS_MAP.get(c, 'Descripción no encontrada')}
        for c in sorted(list(codigos_actividad))
    ]
    return jsonify({'actividades': actividades_sugeridas})

if __name__ == '__main__':
    app.run(debug=True)
