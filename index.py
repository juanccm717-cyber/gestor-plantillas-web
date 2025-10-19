from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import uuid

# --- Carga de datos ---
try:
    # Importamos la lista de códigos desde PARAMETROS.py
    from PARAMETROS import CODIGOS_PRESTACIONALES_CATEGORIZADOS
except ImportError:
    CODIGOS_PRESTACIONALES_CATEGORIZADOS = []

try:
    # Creamos un archivo cie10.json vacío si no existe para evitar errores
    with open('cie10.json', 'r', encoding='utf-8') as f:
        CIE10 = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    CIE10 = [] 

# --- Configuración de la App ---
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_cambiala' # Es importante cambiar esto

# --- Rutas de la Aplicación ---

@app.route('/')
def index():
    # Redirige a la página principal de plantillas
    return redirect(url_for('plantillas'))

@app.route('/plantillas')
def plantillas():
    modo = request.args.get('modo', 'ver')
    return render_template('index.html', modo=modo)

# =========================================================================
# RUTA CORREGIDA: Aquí estaba el problema
# =========================================================================
@app.route('/search_codigos')
def search_codigos():
    query = request.args.get('query', '').lower()
    suggestions = []
    if query:
        for item in CODIGOS_PRESTACIONALES_CATEGORIZADOS:
            if query in item['codigo'].lower() or query in item['descripcion'].lower():
                suggestions.append({
                    'codigo': item['codigo'],
                    'descripcion': item['descripcion']
                })
    
    # LA CORRECCIÓN: Usar jsonify para convertir el diccionario de Python
    # en una respuesta HTTP con el Content-Type 'application/json' correcto.
    # Flask se encarga de todo automáticamente con esta función.
    return jsonify({'suggestions': suggestions})
# =========================================================================

@app.route('/search_diagnosticos')
def search_diagnosticos():
    query = request.args.get('query', '').lower()
    suggestions = []
    if query:
        for item in CIE10:
            if query in item.get('code', '').lower() or query in item.get('description', '').lower():
                 suggestions.append(f"({item.get('code')}) {item.get('description')}")
    # Usamos jsonify aquí también por consistencia
    return jsonify({'suggestions': suggestions})

# --- Rutas de Datos (API) ---

def get_registros_data():
    try:
        with open('registros.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Si el archivo no existe o está vacío, creamos uno nuevo
        with open('registros.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
        return []

@app.route('/get_registros')
def get_registros():
    return jsonify(get_registros_data())

@app.route('/guardar_plantilla', methods=['POST'])
def guardar_plantilla():
    registros = get_registros_data()
    nueva_plantilla = request.json
    nueva_plantilla['id'] = str(uuid.uuid4())
    registros.append(nueva_plantilla)
    with open('registros.json', 'w', encoding='utf-8') as f:
        json.dump(registros, f, indent=4)
    return jsonify({'message': 'Plantilla guardada con éxito'})

# Necesario para Vercel
if __name__ == "__main__":
    app.run(debug=True)
