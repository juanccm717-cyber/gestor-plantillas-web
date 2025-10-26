from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# --- CONFIGURACIÓN DE LA BASE DE DATOS REAL (SUPABASE) ---
load_dotenv() # Carga las variables desde el archivo .env

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("La variable de entorno DATABASE_URL no está configurada.")
    
engine = create_engine(DATABASE_URL)
# ---------------------------------------------------------

# --- IMPORTACIÓN DE LISTAS ESTÁTICAS ---
try:
    from LISTAS import (
        CODIGOS_PRESTACIONALES_CATEGORIZADOS,
        ACTIVIDADES_PREVENTIVAS_MAP,
        RELACION_CODIGO_ACTIVIDADES
    )
    print("--- OK: Listas estáticas importadas desde LISTAS.py ---")
except ImportError:
    print("!!! ERROR: No se pudo encontrar LISTAS.py. !!!")
    CODIGOS_PRESTACIONALES_CATEGORIZADOS, ACTIVIDADES_PREVENTIVAS_MAP, RELACION_CODIGO_ACTIVIDADES = [], {}, {}

# --- INICIO DE LA APLICACIÓN FLASK ---
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'))
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "llave-secreta-de-desarrollo")

# --- RUTAS DEL NÚCLEO (LOGIN, MENU, ETC.) ---
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    usuarios_locales = [{"username": "admin", "password_hash": generate_password_hash("test1234", method='scrypt'), "role": "administrador"}, {"username": "usuario", "password_hash": generate_password_hash("test1234", method='scrypt'), "role": "usuario"}]
    if 'username' in session: return redirect(url_for('menu'))
    if request.method == 'POST':
        form_username = request.form['username']
        form_password = request.form['password']
        normalized_form_username = form_username.lower()
        found_user = next((user for user in usuarios_locales if user["username"].lower() == normalized_form_username), None)
        if found_user and check_password_hash(found_user['password_hash'], form_password):
            session['username'] = found_user['username']
            session['role'] = found_user['role']
            return redirect(url_for('menu'))
        else:
            return render_template('login.html', error='Credenciales inválidas.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/menu')
def menu():
    if 'username' not in session: return redirect(url_for('login'))
    return render_template('menu.html')

# --- RUTAS DE FORMULARIO Y APIs ---
@app.route('/plantillas')
def plantillas():
    if 'username' not in session: return redirect(url_for('login'))
    modo = request.args.get('modo', 'crear')
    plantilla_id = request.args.get('id', None)
    return render_template('plantillas.html', modo=modo, plantilla_id=plantilla_id)

@app.route('/search_codigos', methods=['GET'])
def search_codigos():
    if 'username' not in session: return jsonify({'suggestions': []}), 401
    query = request.args.get('query', '').strip()
    suggestions = [s for s in CODIGOS_PRESTACIONALES_CATEGORIZADOS if s['codigo'] == query]
    return jsonify({'suggestions': suggestions})

@app.route('/get_actividades_por_codigo/<codigo>', methods=['GET'])
def get_actividades_por_codigo(codigo):
    if 'username' not in session: return jsonify({'actividades': []}), 401
    codigos_actividad = RELACION_CODIGO_ACTIVIDADES.get(codigo, RELACION_CODIGO_ACTIVIDADES.get('DEFAULT', []))
    actividades_sugeridas = [{'codigo': c, 'descripcion': ACTIVIDADES_PREVENTIVAS_MAP.get(c, f'Desc no encontrada')} for c in sorted(list(codigos_actividad))]
    return jsonify({'actividades': actividades_sugeridas})

# --- RUTAS CRUD CONECTADAS A SUPABASE ---

@app.route('/get_registros', methods=['GET'])
def get_registros():
    if 'username' not in session: return jsonify({"error": "No autorizado"}), 401
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, tipo_atencion, codigo_prestacional FROM plantillas ORDER BY id ASC"))
        registros = [dict(row._mapping) for row in result]
        return jsonify(registros)

@app.route('/get_plantilla/<int:plantilla_id>', methods=['GET'])
def get_plantilla(plantilla_id):
    if 'username' not in session: return jsonify({"error": "No autorizado"}), 401
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM plantillas WHERE id = :id"), {"id": plantilla_id})
        plantilla = result.first()
        if plantilla:
            return jsonify(dict(plantilla._mapping))
        else:
            return jsonify({"error": "Plantilla no encontrada"}), 404

@app.route('/delete_plantilla/<int:plantilla_id>', methods=['DELETE'])
def delete_plantilla(plantilla_id):
    if session.get('role') != 'administrador': return jsonify({'message': 'No autorizado.'}), 403
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM plantillas WHERE id = :id"), {"id": plantilla_id})
        connection.commit()
        return jsonify({'message': f'Plantilla ID {plantilla_id} eliminada con éxito.'}), 200

@app.route('/guardar_plantilla', methods=['POST'])
def guardar_plantilla():
    if session.get('role') != 'administrador': return jsonify({'message': 'No autorizado.'}), 403
    
    data = request.json
    plantilla_id = data.get('plantilla_id')

    params = {
        "tipo_atencion": data.get("tipo_atencion"),
        "codigo_prestacional": data.get("codigo_prestacional"),
        "descripcion_prestacional": data.get("descripcion_prestacional"),
        "actividades_preventivas": data.get('actividades_preventivas', []),
        "diagnostico_principal": data.get("diagnostico_principal", []),
        "diagnosticos_excluyentes": data.get("diagnosticos_excluyentes", []),
        "diagnosticos_complementarios": data.get("diagnosticos_complementarios", []),
        "medicamentos_relacionados": data.get("medicamentos_relacionados", []),
        "insumos_relacionados": data.get("insumos_relacionados", []),
        "procedimientos_obligatorios": data.get("procedimientos_obligatorios", []),
        "procedimientos_excluyentes": data.get("procedimientos_excluyentes", []),
        "otros_procedimientos": data.get("otros_procedimientos", []),
        "observaciones": data.get("observaciones"),
    }

    with engine.connect() as connection:
        if plantilla_id:
            params['id'] = plantilla_id
            query = text("""
                UPDATE plantillas SET
                    tipo_atencion = :tipo_atencion, codigo_prestacional = :codigo_prestacional,
                    descripcion_prestacional = :descripcion_prestacional, actividades_preventivas = :actividades_preventivas,
                    diagnostico_principal = :diagnostico_principal, diagnosticos_excluyentes = :diagnosticos_excluyentes,
                    diagnosticos_complementarios = :diagnosticos_complementarios, medicamentos_relacionados = :medicamentos_relacionados,
                    insumos_relacionados = :insumos_relacionados, procedimientos_obligatorios = :procedimientos_obligatorios,
                    procedimientos_excluyentes = :procedimientos_excluyentes, otros_procedimientos = :otros_procedimientos,
                    observaciones = :observaciones
                WHERE id = :id
            """)
            connection.execute(query, params)
            connection.commit()
            return jsonify({'message': f'Plantilla ID {plantilla_id} actualizada con éxito.'}), 200
        else:
            query = text("""
                INSERT INTO plantillas (tipo_atencion, codigo_prestacional, descripcion_prestacional, actividades_preventivas, 
                                      diagnostico_principal, diagnosticos_excluyentes, diagnosticos_complementarios, 
                                      medicamentos_relacionados, insumos_relacionados, procedimientos_obligatorios, 
                                      procedimientos_excluyentes, otros_procedimientos, observaciones)
                VALUES (:tipo_atencion, :codigo_prestacional, :descripcion_prestacional, :actividades_preventivas, 
                        :diagnostico_principal, :diagnosticos_excluyentes, :diagnosticos_complementarios, 
                        :medicamentos_relacionados, :insumos_relacionados, :procedimientos_obligatorios, 
                        :procedimientos_excluyentes, :otros_procedimientos, :observaciones)
                RETURNING id
            """)
            result = connection.execute(query, params)
            new_id = result.scalar()
            connection.commit()
            return jsonify({'message': f'¡Éxito! Plantilla "{params["tipo_atencion"]}" guardada con ID: {new_id}'}), 201

@app.route('/ver_plantillas')
def ver_plantillas():
    if 'username' not in session: return redirect(url_for('login'))
    return render_template('ver_plantillas.html')

if __name__ == '__main__':
    app.run(debug=True)
