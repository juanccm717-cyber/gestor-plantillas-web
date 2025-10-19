from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import uuid
import os # Importamos el módulo 'os'

# --- Configuración de la App ---
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_cambiala'

# --- Carga de datos ---
try:
    from PARAMETROS import CODIGOS_PRESTACIONALES_CATEGORIZADOS
except ImportError:
    CODIGOS_PRESTACIONALES_CATEGORIZADOS = []

try:
    with open('cie10.json', 'r', encoding='utf-8') as f:
        CIE10 = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    CIE10 = [] 

# =========================================================================
# FUNCIÓN CORREGIDA: Más robusta contra errores de sistema de archivos
# =========================================================================
def get_registros_data():
    try:
        with open('registros.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        # Capturamos cualquier error (FileNotFound, JSONDecodeError, PermissionError)
        # y simplemente devolvemos una lista vacía para no romper la app.
        print(f"Error al leer registros.json: {e}") # Esto se verá en los logs de Vercel
        return []

def save_registros_data(data):
    # Advertencia: Esto puede fallar en Vercel.
    try:
        with open('registros.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error al GUARDAR registros.json: {e}")
        return False
# =========================================================================

# --- Rutas ---
@app.route('/')
def index():
    return redirect(url_for('plantillas'))

@app.route('/plantillas')
def plantillas():
    modo = request.args.get('modo', 'ver')
    return render_template('index.html', modo=modo)

# --- Rutas de API ---
@app.route('/search_codigos')
def search_codigos():
    query = request.args.get('query', '').lower()
    suggestions = []
    if query:
        for item in CODIGOS_PRESTACIONALES_CATEGORIZADOS:
            if query in item['codigo'].lower() or query in item['descripcion'].lower():
                suggestions.append({'codigo': item['codigo'], 'descripcion': item['descripcion']})
    return jsonify({'suggestions': suggestions})

@app.route('/search_diagnosticos')
def search_diagnosticos():
    # ... (sin cambios)
    return jsonify({'suggestions': []}) # Simplificado por ahora

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
        # Devolvemos un error si no se pudo guardar
        return jsonify({'message': 'Error: No se pudo guardar la plantilla en el servidor.'}), 500

if __name__ == "__main__":
    app.run(debug=True)
