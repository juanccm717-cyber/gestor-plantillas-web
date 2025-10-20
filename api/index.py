import sys
import os
from flask import Flask, render_template, request, jsonify
import json
import uuid

# --- ESTA PARTE ES CRUCIAL ---
# Añade el directorio raíz a la ruta de Python para que encuentre PARAMETROS.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# --- FIN DE LA PARTE CRUCIAL ---

try:
    from PARAMETROS import (
        CODIGOS_PRESTACIONALES_CATEGORIZADOS, 
        ACTIVIDADES_PREVENTIVAS_MAP, 
        RELACION_CODIGO_ACTIVIDADES
    )
except ImportError as e:
    print(f"Error crítico al importar PARAMETROS: {e}")
    CODIGOS_PRESTACIONALES_CATEGORIZADOS, ACTIVIDADES_PREVENTIVAS_MAP, RELACION_CODIGO_ACTIVIDADES = [], {}, {}

# --- El resto de tu aplicación Flask ---
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# La ruta raíz que renderiza la página principal
@app.route('/')
def home():
    return render_template('index.html')

# El resto de tus rutas de API...
@app.route('/search_codigos')
def search_codigos():
    # ... tu código para buscar códigos ...
    query = request.args.get('query', '').lower()
    suggestions = []
    if query:
        for item in CODIGOS_PRESTACIONALES_CATEGORIZADOS:
            if query in item['codigo'].lower() or query in item['descripcion'].lower():
                suggestions.append({'codigo': item['codigo'], 'descripcion': item['descripcion']})
    return jsonify({'suggestions': suggestions})

# ... (Asegúrate de que todas tus otras rutas como /get_actividades_por_codigo, etc., estén aquí) ...
