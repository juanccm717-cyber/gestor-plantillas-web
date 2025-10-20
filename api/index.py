from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import timedelta
import os
from sqlalchemy import create_engine, text, exc

# --- CONFIGURACIÓN DE LA BASE DE DATOS (SUPABASE) ---
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("La variable de entorno DATABASE_URL no está configurada.")

# Modificación para usar el "Connection Pooler"
if 'db.ylzpvpgcelbsbdcauqzw.supabase.co' in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace(
        'db.ylzpvpgcelbsbdcauqzw.supabase.co:5432',
        'pg.ylzpvpgcelbsbdcauqzw.supabase.co:6543'
    )

engine = create_engine(DATABASE_URL)

# --- IMPORTACIONES DE PARÁMETROS ---
from PARAMETROS import (
    CODIGOS_PRESTACIONALES_CATEGORIZADOS,
    ACTIVIDADES_PREVENTIVAS_MAP,
    RELACION_CODIGO_ACTIVIDADES
)

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'))
app.secret_key = 'tu_super_secreta_llave_aqui_4' # Pequeño cambio para forzar redespliegue
app.permanent_session_lifetime = timedelta(minutes=60)


# ======================================================================
# FUNCIÓN DE LECTURA CON DIAGNÓSTICO EXPLÍCITO
# ======================================================================

def leer_registros_desde_db():
    """Lee todas las plantillas, ahora con un diagnóstico de errores detallado."""
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT id, codigo_prestacional, descripcion_prestacional, actividades_preventivas, 
                       diagnostico_principal, diagnosticos_complementarios, medicamento_principal, 
                       medicamentos_adicionales_obs, procedimiento_principal, 
                       procedimientos_adicionales_obs
                FROM public.registros ORDER BY id ASC;
            """)
            result = conn.execute(query)
            keys = result.keys()
            registros = [dict(zip(keys, row)) for row in result]
            # Si llega hasta aquí, la lectura fue exitosa
            print("DIAGNÓSTICO: La lectura de la base de datos fue exitosa.")
            return registros
    except exc.SQLAlchemyError as e:
        # ======================================================================
        # ¡ESTA ES LA PARTE MÁS IMPORTANTE!
        # Imprimimos el error exacto en los logs de Vercel.
        # ======================================================================
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! ERROR CRÍTICO AL LEER DE LA BASE DE DATOS !!!")
        print(f"!!! TIPO DE ERROR: {type(e)}")
        print(f"!!! ERROR DETALLADO: {e}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return [] # Devolvemos una lista vacía para que el frontend no se rompa.
    except Exception as e:
        # Captura cualquier otro error inesperado
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! ERROR GENERAL INESPERADO !!!")
        print(f"!!! TIPO DE ERROR: {type(e)}")
        print(f"!!! ERROR DETALLADO: {e}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return []

# La función de escritura no necesita cambios
def escribir_registro_en_db(plantilla_data):
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
            "actividades_preventivas": plantilla_data.get("actividades_preventivas"),
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

# --- El resto del archivo no cambia ---

@app.route('/')
def home():
    if 'username' in session: return redirect(url_for('menu'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.permanent = True
        session['username'] = request.form['username']
        session['rol'] = request.form.get('rol', 'viewer')
        return redirect(url_for('menu'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/menu')
def menu():
    if 'username' not in session: return redirect(url_for('login'))
    return render_template('menu.html', username=session['username'], rol=session['rol'])

@app.route('/plantillas')
def plantillas():
    if 'username' not in session: return redirect(url_for('login'))
    return render_template('index.html', rol=session.get('rol', 'viewer'))

@app.route('/guardar_plantilla', methods=['POST'])
def guardar_plantilla():
    if session.get('rol') != 'admin':
        return jsonify({'message': 'Acceso no autorizado.'}), 403
    nueva_plantilla = request.json
    if not nueva_plantilla.get('codigo_prestacional'):
        return jsonify({'message': 'El código prestacional es obligatorio.'}), 400
    nuevo_id = escribir_registro_en_db(nueva_plantilla)
    return jsonify({'message': f"Plantilla guardada con éxito con ID: {nuevo_id}"}), 201

@app.route('/get_registros', methods=['GET'])
def get_registros():
    if 'username' not in session: return jsonify([]), 401
    registros = leer_registros_desde_db()
    return jsonify(registros)

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
