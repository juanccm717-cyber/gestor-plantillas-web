import sys
import os
from flask import Flask, render_template, request, jsonify
import json
import uuid

# Añade el directorio raíz a la ruta de Python para que encuentre PARAMETROS.py
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

# =========================================================================
# INICIO DE LA CORRECCIÓN CLAVE
# =========================================================================
# Obtener la ruta del directorio raíz del proyecto (un nivel arriba de 'api')
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Crear la aplicación Flask, indicando dónde están las plantillas y los archivos estáticos
app = Flask(
    __name__,
    template_folder=os.path.join(project_root, 'templates'),
    static_folder=os.path.join(project_root, 'static') # Aunque no tengamos 'static', es buena práctica
)
# =========================================================================
# FIN DE LA CORRECCIÓN CLAVE
# =========================================================================

app.secret_key = 'tu_clave_secreta_aqui'

# --- El resto del código no cambia ---

# La ruta raíz que renderiza la página principal
@app.route('/')
def home():
    # Ahora Flask sabe dónde encontrar 'index.html'
    return render_template('index.html')

# El resto de tus rutas de API...
@app.route('/search_codigos')
def search_codigos():
    query = request.args.get('query', '').lower()
    suggestions = []
    if query:
        for item in CODIGOS_PRESTACIONALES_CATEGORIZADOS:
            if query in item['codigo'].lower() or query in item['descripcion'].lower():
                suggestions.append({'codigo': item['codigo'], 'descripcion': item['descripcion']})
    return jsonify({'suggestions': suggestions})

@app.route('/get_actividades_por_codigo/<string:codigo_prestacional>')
def get_actividades_por_codigo(codigo_prestacional):
    codigos_actividad = RELACION_CODIGO_ACTIVIDADES.get(codigo_prestacional, RELACION_CODIGO_ACTIVIDADES.get('DEFAULT', []))
    actividades_desc = [ACTIVIDADES_PREVENTIVAS_MAP.get(cod, f"{cod}: Actividad no encontrada") for cod in sorted(list(codigos_actividad))]
    return jsonify({'actividades': actividades_desc})

# (Asegúrate de que el resto de tus rutas como /get_registros, etc., estén aquí)
# ...
