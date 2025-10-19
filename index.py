from flask import Flask, render_template, request, jsonify
import json
import uuid

# --- Carga de datos desde PARAMETROS.py ---
try:
    from PARAMETROS import (
        CODIGOS_PRESTACIONALES_CATEGORIZADOS, 
        ACTIVIDADES_PREVENTIVAS_MAP, 
        RELACION_CODIGO_ACTIVIDADES
    )
except ImportError:
    # Valores por defecto en caso de que el archivo no se encuentre
    CODIGOS_PRESTACIONALES_CATEGORIZADOS = []
    ACTIVIDADES_PREVENTIVAS_MAP = {}
    RELACION_CODIGO_ACTIVIDADES = {}

# --- Configuración de la App ---
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_cambiala_por_algo_seguro'

# --- Funciones de ayuda para datos ---
def get_registros_data():
    try:
        with open('registros.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_registros_data(data):
    try:
        with open('registros.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False

# --- Rutas de la Interfaz de Usuario ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Rutas de la API ---

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
    # Busca los códigos de actividad relacionados. Usa 'DEFAULT' si no encuentra el código.
    codigos_actividad = RELACION_CODIGO_ACTIVIDADES.get(codigo_prestacional, RELACION_CODIGO_ACTIVIDADES.get('DEFAULT', []))
    
    # Busca las descripciones completas para cada código de actividad
    actividades_desc = [ACTIVIDADES_PREVENTIVAS_MAP.get(cod, f"{cod}: Actividad no encontrada") for cod in sorted(list(codigos_actividad))]
    
    return jsonify({'actividades': actividades_desc})

@app.route('/get_registros')
def get_registros():
    return jsonify(get_registros_data())

@app.route('/guardar_plantilla', methods=['POST'])
def guardar_plantilla():
    registros = get_registros_data()
    nueva_plantilla = request.json
    nueva_plantilla['id'] = str(uuid.uuid4())
    registros.append(nueva_plantilla)
    if save_registros_data(registros):
        return jsonify({'message': 'Plantilla guardada con éxito'})
    else:
        return jsonify({'message': 'Error: No se pudo guardar la plantilla.'}), 500

if __name__ == "__main__":
    app.run(debug=True)
