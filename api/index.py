# api/index.py

import sys
import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import uuid

# --- Configuración de Rutas y Módulos ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__ ), '..')))
try:
    from PARAMETROS import (
        CODIGOS_PRESTACIONALES_CATEGORIZADOS, 
        ACTIVIDADES_PREVENTIVAS_MAP, 
        RELACION_CODIGO_ACTIVIDADES
    )
except ImportError:
    CODIGOS_PRESTACIONALES_CATEGORIZADOS, ACTIVIDADES_PREVENTIVAS_MAP, RELACION_CODIGO_ACTIVIDADES = [], {}, {}

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app = Flask(
    __name__,
    template_folder=os.path.join(project_root, 'templates'),
    static_folder=os.path.join(project_root, 'static')
)
app.secret_key = 'una-clave-muy-secreta-y-dificil-de-adivinar'

# --- Funciones de Datos (Guardar/Cargar JSON) ---
def get_registros_data():
    try:
        with open(os.path.join(project_root, 'registros.json'), 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_registros_data(data):
    try:
        with open(os.path.join(project_root, 'registros.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False

# --- Rutas de Autenticación y Navegación ---
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Lógica de autenticación (simplificada)
        # Aquí podrías verificar usuario y contraseña contra una base de datos
        session['user'] = request.form.get('username', 'usuario_desconocido')
        
        # NUEVO: Guardar el rol en la sesión
        session['rol'] = request.form.get('rol', 'viewer') # Por defecto 'viewer' si no se envía
        
        return redirect(url_for('menu'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/menu')
def menu():
    if 'user' not in session:
        return redirect(url_for('login'))
    # Pasamos el nombre de usuario y el rol a la plantilla del menú
    return render_template('menu.html', username=session.get('user'), rol=session.get('rol'))

@app.route('/plantillas')
def plantillas():
    if 'user' not in session:
        return redirect(url_for('login'))
    # Pasamos el rol a la plantilla principal para que el frontend sepa qué mostrar
    return render_template('index.html', rol=session.get('rol', 'viewer'))

# --- Rutas de API ---
@app.route('/search_codigos')
def search_codigos():
    if 'user' not in session: return jsonify({"error": "No autorizado"}), 401
    query = request.args.get('query', '').lower()
    suggestions = []
    if query:
        for item in CODIGOS_PRESTACIONALES_CATEGORIZADOS:
            if query in item['codigo'].lower() or query in item['descripcion'].lower():
                suggestions.append({'codigo': item['codigo'], 'descripcion': item['descripcion']})
    return jsonify({'suggestions': suggestions})

@app.route('/get_actividades_por_codigo/<string:codigo_prestacional>')
def get_actividades_por_codigo(codigo_prestacional):
    if 'user' not in session: return jsonify({"error": "No autorizado"}), 401
    codigos_actividad = RELACION_CODIGO_ACTIVIDADES.get(codigo_prestacional, RELACION_CODIGO_ACTIVIDADES.get('DEFAULT', []))
    actividades_desc = [ACTIVIDADES_PREVENTIVAS_MAP.get(cod, f"{cod}: Actividad no encontrada") for cod in sorted(list(codigos_actividad))]
    return jsonify({'actividades': actividades_desc})

@app.route('/get_registros')
def get_registros():
    if 'user' not in session: return jsonify({"error": "No autorizado"}), 401
    return jsonify(get_registros_data())

@app.route('/guardar_plantilla', methods=['POST'])
def guardar_plantilla():
    # Solo los administradores pueden guardar
    if session.get('rol') != 'admin':
        return jsonify({'message': 'Acción no permitida. Se requieren permisos de administrador.'}), 403
    
    registros = get_registros_data()
    nueva_plantilla = request.json
    nueva_plantilla['id'] = str(uuid.uuid4())
    registros.append(nueva_plantilla)
    
    if save_registros_data(registros):
        return jsonify({'message': 'Plantilla guardada con éxito'})
    else:
        return jsonify({'message': 'Error: No se pudo guardar la plantilla en el servidor.'}), 500
