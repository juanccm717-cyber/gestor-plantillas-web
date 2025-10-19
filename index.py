from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import uuid

# Importamos la lista de códigos desde PARAMETROS.py
try:
    from PARAMETROS import CODIGOS_PRESTACIONALES_CATEGORIZADOS
except ImportError:
    CODIGOS_PRESTACIONALES_CATEGORIZADOS = []

# Importamos la lista de diagnósticos CIE-10
# (Asumimos que tienes un archivo cie10.json o similar, si no, lo creamos)
try:
    with open('cie10.json', 'r', encoding='utf-8') as f:
        CIE10 = json.load(f)
except FileNotFoundError:
    CIE10 = [] # Si no existe, la búsqueda no devolverá nada.

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui' # Cambia esto por una clave segura

# --- RUTAS DE AUTENTICACIÓN Y MENÚ (simplificadas) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Lógica de autenticación simple
        session['user'] = 'admin' # o 'user'
        return redirect(url_for('plantillas'))
    return render_template('login.html')

@app.route('/menu')
def menu():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('menu.html')

# --- RUTA PRINCIPAL DE PLANTILLAS ---
@app.route('/')
@app.route('/plantillas')
def plantillas():
    modo = request.args.get('modo', 'ver') # 'editar' para admin, 'ver' para usuario
    return render_template('index.html', modo=modo)

# --- RUTAS DE BÚSQUEDA (APIs para Autocompletado) ---

@app.route('/search_codigos')
def search_codigos():
    query = request.args.get('query', '').lower()
    suggestions = []
    if query:
        for item in CODIGOS_PRESTACIONALES_CATEGORIZADOS:
            if query in item['codigo'].lower() or query in item['descripcion'].lower():
                # CORRECCIÓN CLAVE: Asegurarnos de que el diccionario que se envía
                # contiene las claves 'codigo' y 'descripcion'.
                suggestions.append({
                    'codigo': item['codigo'],
                    'descripcion': item['descripcion']
                })
    # La librería espera un objeto con una clave "suggestions"
    return jsonify({'suggestions': suggestions})

@app.route('/search_diagnosticos')
def search_diagnosticos():
    query = request.args.get('query', '').lower()
    suggestions = []
    if query:
        for item in CIE10:
            # Asumiendo que cie10.json tiene objetos con 'code' y 'description'
            if query in item.get('code', '').lower() or query in item.get('description', '').lower():
                 suggestions.append(f"({item.get('code')}) {item.get('description')}")
    return jsonify({'suggestions': suggestions})


# --- RUTAS DE GESTIÓN DE DATOS ---
def get_registros_data():
    try:
        with open('registros.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

@app.route('/get_registros')
def get_registros():
    return jsonify(get_registros_data())

@app.route('/guardar_plantilla', methods=['POST'])
def guardar_plantilla():
    registros = get_registros_data()
    nueva_plantilla = request.json
    nueva_plantilla['id'] = str(uuid.uuid4()) # Asigna un ID único
    registros.append(nueva_plantilla)
    with open('registros.json', 'w', encoding='utf-8') as f:
        json.dump(registros, f, indent=4)
    return jsonify({'message': 'Plantilla guardada con éxito'})

# Esto es necesario para Vercel
if __name__ == "__main__":
    app.run(debug=True)

