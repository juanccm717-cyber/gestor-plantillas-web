from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from sqlalchemy import create_engine, text, exc
# ======================================================================
# ¡ESTA ES LA LÍNEA QUE FALTABA Y QUE CAUSABA EL ERROR 500!
from werkzeug.security import check_password_hash
# ======================================================================
from datetime import timedelta

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("La variable de entorno DATABASE_URL no está configurada.")

engine = create_engine(DATABASE_URL)

# --- IMPORTACIONES DE PARÁMETROS ---
# (Asegúrate de que este archivo PARAMETROS.py esté dentro de la carpeta api/)
from PARAMETROS import (
    CODIGOS_PRESTACIONALES_CATEGORIZADOS,
    ACTIVIDADES_PREVENTIVAS_MAP,
    RELACION_CODIGO_ACTIVIDADES
)

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'))
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "llave-secreta-robusta-99999") # El número no importa
app.permanent_session_lifetime = timedelta(minutes=60)

# --- FUNCIONES DE BASE DE DATOS (SIN CAMBIOS) ---
def leer_registros_desde_db():
    try:
        with engine.connect() as conn:
            query = text("SELECT * FROM public.registros ORDER BY id ASC;")
            result = conn.execute(query)
            keys = result.keys()
            registros = [dict(zip(keys, row)) for row in result]
            return registros
    except Exception as e:
        print(f"!!! ERROR AL LEER REGISTROS: {e}")
        return []

def escribir_registro_en_db(plantilla_data):
    try:
        with engine.connect() as conn:
            stmt = text("""
                INSERT INTO public.registros (
                    codigo_prestacional, descripcion_prestacional, actividades_preventivas,
                    diagnostico_principal, diagnosticos_complementarios, medicamento_principal,
                    medicamentos_adicionales_obs, procedimiento_principal,
                    procedimientos_adicionales_obs
                ) VALUES (
                    :codigo_prestacional, :descripcion_prestacional, :actividades_preventivas,
                    :diagnostico_principal, :diagnosticos_complementarios, :medicamento_principal,
                    :medicamentos_adicionales_obs, :procedimiento_principal,
                    :procedimientos_adicionales_obs
                ) RETURNING id;
            """)
            params = {
                "codigo_prestacional": plantilla_data.get("codigo_prestacional"),
                "descripcion_prestacional": plantilla_data.get("descripcion_prestacional"),
                "actividades_preventivas": "\n".join(plantilla_data.get("actividades_preventivas", [])),
                "diagnostico_principal": plantilla_data.get("diagnostico_principal"),
                "diagnosticos_complementarios": plantilla_data.get("diagnosticos_complementarios"),
                "medicamento_principal": plantilla_data.get("medicamento_principal"),
                "medicamentos_adicionales_obs": plantilla_data.get("medicamentos_adicionales_obs"),
                "procedimiento_principal": plantilla_data.get("procedimiento_principal"),
                "procedimientos_adicionales_obs": plantilla_data.get("procedimientos_adicionales_obs"),
            }
            result = conn.execute(stmt, params)
            nuevo_id = result.scalar()
            conn.commit()
            return nuevo_id
    except Exception as e:
        print(f"!!! ERROR AL ESCRIBIR REGISTRO: {e}")
        return None

# --- RUTAS DE LA APLICACIÓN (YA CORRECTAS) ---
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('menu'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Búsqueda del usuario en la base de datos
        with engine.connect() as conn:
            query = text("SELECT username, password_hash, role FROM public.usuarios WHERE username = :username")
            result = conn.execute(query, {"username": username}).fetchone()

        # Verificación de la contraseña
        if result and check_password_hash(result[1], password):
            session.permanent = True
            session['username'] = result[0]
            session['rol'] = result[2]
            return redirect(url_for('menu'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/menu')
def menu():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('menu.html', username=session['username'], rol=session['rol'])

@app.route('/plantillas')
def plantillas():
    if 'username' not in session:
        return redirect(url_for('login'))
    modo = request.args.get('modo', 'crear')
    return render_template('index.html', rol=session.get('rol', 'usuario'), modo=modo)

# --- RUTAS DE API (YA CORRECTAS) ---
@app.route('/get_registros', methods=['GET'])
def get_registros():
    if 'username' not in session:
        return jsonify({"error": "No autorizado"}), 401
    registros = leer_registros_desde_db()
    return jsonify(registros)

@app.route('/guardar_plantilla', methods=['POST'])
def guardar_plantilla():
    if session.get('rol') != 'administrador':
        return jsonify({'message': 'Acceso no autorizado.'}), 403
    nueva_plantilla = request.json
    if not nueva_plantilla.get('codigo_prestacional'):
        return jsonify({'message': 'El código prestacional es obligatorio.'}), 400
    nuevo_id = escribir_registro_en_db(nueva_plantilla)
    if nuevo_id:
        return jsonify({'message': f"Plantilla guardada con éxito con ID: {nuevo_id}"}), 201
    else:
        return jsonify({'message': 'Error al guardar la plantilla en la base de datos.'}), 500

@app.route('/search_codigos', methods=['GET'])
def search_codigos():
    if 'username' not in session: return jsonify({'suggestions': []}), 401
    query = request.args.get('query', '').lower()
    suggestions = [s for s in CODIGOS_PRESTACIONALES_CATEGORIZADOS if query in s['codigo'].lower() or query in s['descripcion'].lower()]
    return jsonify({'suggestions': suggestions})

@app.route('/get_actividades_por_codigo/<string:codigo>', methods=['GET'])
def get_actividades_por_codigo(codigo):
    if 'username' not in session: return jsonify({'actividades': []}), 401
    codigos_actividad = RELACION_CODIGO_ACTIVIDADES.get(codigo, RELACION_CODIGO_ACTIVIDADES.get('DEFAULT', []))
    actividades_sugeridas = [{'codigo': c, 'descripcion': ACTIVIDADES_PREVENTIVAS_MAP.get(c, 'Desc no encontrada')} for c in sorted(list(codigos_actividad))]
    return jsonify({'actividades': actividades_sugeridas})

if __name__ == '__main__':
    app.run(debug=True)
