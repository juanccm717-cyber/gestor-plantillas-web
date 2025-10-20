import sys
import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import uuid

# Añade el directorio raíz a la ruta de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from PARAMETROS import (
        CODIGOS_PRESTACIONALES_CATEGORIZADOS, 
        ACTIVIDADES_PREVENTIVAS_MAP, 
        RELACION_CODIGO_ACTIVIDADES
    )
except ImportError as e:
    print(f"Error crítico al importar PARAMETROS: {e}")
    CODIGOS_PRESTACIONALES_CATEGORIZADOS, ACTIVIDADES_PREVENTIVAS_MAP, RELACION_CODIGO_ACTIVIDADES = [], {}, {}

# --- Configuración de la App Flask ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app = Flask(
    __name__,
    template_folder=os.path.join(project_root, 'templates'),
    static_folder=os.path.join(project_root, 'static')
)
app.secret_key = 'una-clave-muy-secreta-y-dificil-de-adivinar'

# --- Rutas de Autenticación y Navegación ---

@app.route('/')
def home():
    # Si el usuario ya tiene una sesión, lo llevamos al menú principal
    if 'user' in session:
        # CAMBIO: Redirigir a /menu en lugar de /plantillas
        return redirect(url_for('menu'))
    # Si no, lo mandamos a la página de login
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = request.form.get('username', 'usuario_desconocido')
        session['modo'] = 'editar'
        
        # CAMBIO: Redirigimos al menú principal después del login
        return redirect(url_for('menu'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Limpia toda la sesión
    return redirect(url_for('login'))

# =========================================================================
# NUEVA RUTA PARA EL MENÚ PRINCIPAL
# =========================================================================
@app.route('/menu')
def menu():
    # Proteger esta ruta
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Renderiza la página del menú
    return render_template('menu.html')
# =========================================================================

@app.route('/plantillas')
def plantillas():
    # Proteger esta ruta
    if 'user' not in session:
        return redirect(url_for('login'))
    
    modo = session.get('modo', 'ver')
    return render_template('index.html', modo=modo)

# --- Rutas de la API (sin cambios) ---

@app.route('/search_codigos')
def search_codigos():
    # ... (código sin cambios)
    query = request.args.get('query', '').lower()
    suggestions = []
    if query:
        for item in CODIGOS_PRESTACIONALES_CATEGORIZADOS:
            if query in item['codigo'].lower() or query in item['descripcion'].lower():
                suggestions.append({'codigo': item['codigo'], 'descripcion': item['descripcion']})
    return jsonify({'suggestions': suggestions})

@app.route('/get_actividades_por_codigo/<string:codigo_prestacional>')
def get_actividades_por_codigo(codigo_prestacional):
    # ... (código sin cambios)
    codigos_actividad = RELACION_CODIGO_ACTIVIDADES.get(codigo_prestacional, RELACION_CODIGO_ACTIVIDADES.get('DEFAULT', []))
    actividades_desc = [ACTIVIDADES_PREVENTIVAS_MAP.get(cod, f"{cod}: Actividad no encontrada") for cod in sorted(list(codigos_actividad))]
    return jsonify({'actividades': actividades_desc})

# (Aquí irían el resto de tus rutas de API: /get_registros, /guardar_plantilla, etc.)
# ...
