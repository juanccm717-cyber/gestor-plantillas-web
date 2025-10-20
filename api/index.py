from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from sqlalchemy import create_engine, text, exc
from supabase import create_client, Client

# --- CONFIGURACIÓN DE CONEXIONES ---
# Variables de Entorno de Vercel
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

# Verificación de que todas las variables existen
if not all([SUPABASE_URL, SUPABASE_KEY, DATABASE_URL]):
    raise RuntimeError("Faltan una o más variables de entorno: SUPABASE_URL, SUPABASE_KEY, DATABASE_URL.")

# Cliente de Supabase (para autenticación y gestión de usuarios)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Motor de SQLAlchemy (para consultas SQL directas)
engine = create_engine(DATABASE_URL)

# --- IMPORTACIONES DE PARÁMETROS ---
from PARAMETROS import (
    CODIGOS_PRESTACIONALES_CATEGORIZADOS,
    ACTIVIDADES_PREVENTIVAS_MAP,
    RELACION_CODIGO_ACTIVIDADES
)

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'))
# La secret_key de Flask ya no es tan crucial para la sesión, pero es buena práctica tenerla
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "una-llave-secreta-por-defecto")

# --- FUNCIONES DE BASE DE DATOS (YA CORRECTAS) ---
def leer_registros_desde_db():
    try:
        with engine.connect() as conn:
            query = text("SELECT * FROM public.registros ORDER BY id ASC;")
            result = conn.execute(query)
            keys = result.keys()
            registros = [dict(zip(keys, row)) for row in result]
            return registros
    except exc.SQLAlchemyError as e:
        print(f"!!! ERROR AL LEER REGISTROS: {e}")
        return []

def escribir_registro_en_db(plantilla_data):
    # (Esta función no necesita cambios, la dejamos como estaba)
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

# --- NUEVA FUNCIÓN DE AUTENTICACIÓN ---
def obtener_usuario_desde_token(request):
    """Verifica el token JWT de Supabase y devuelve la información del usuario."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        # Verifica el token y obtiene el usuario
        user_response = supabase.auth.get_user(token)
        return user_response.user
    except Exception as e:
        print(f"!!! ERROR DE AUTENTICACIÓN: {e}")
        return None

# --- RUTAS DE LA APLICACIÓN ---
@app.route('/')
def home():
    # La lógica ahora es simple: siempre muestra el login. El frontend se encargará del resto.
    return render_template('login.html')

@app.route('/menu')
def menu():
    # Esta ruta sigue siendo útil para tener una URL limpia para el menú
    return render_template('menu.html')

@app.route('/plantillas')
def plantillas():
    # Igual que el menú, una URL limpia para el gestor
    return render_template('index.html')

# --- RUTAS DE API (REESCRITAS CON AUTENTICACIÓN REAL) ---
@app.route('/get_registros', methods=['GET'])
def get_registros():
    user = obtener_usuario_desde_token(request)
    if not user:
        return jsonify({"error": "No autorizado"}), 401
    
    # Si el usuario es válido, puede ver los registros.
    registros = leer_registros_desde_db()
    return jsonify(registros)

@app.route('/guardar_plantilla', methods=['POST'])
def guardar_plantilla():
    user = obtener_usuario_desde_token(request)
    if not user:
        return jsonify({"error": "No autorizado"}), 401
    
    # Verificamos el rol del usuario desde los metadatos de Supabase
    user_role = user.user_metadata.get('rol', 'viewer')
    if user_role != 'admin':
        return jsonify({"error": "Permiso denegado. Se requiere rol de administrador."}), 403

    nueva_plantilla = request.json
    nuevo_id = escribir_registro_en_db(nueva_plantilla)
    return jsonify({'message': f"Plantilla guardada con éxito con ID: {nuevo_id}"}), 201

# Las rutas de búsqueda no necesitan un rol específico, solo estar logueado
@app.route('/search_codigos', methods=['GET'])
def search_codigos():
    if not obtener_usuario_desde_token(request):
        return jsonify({"error": "No autorizado"}), 401
    query = request.args.get('query', '').lower()
    suggestions = [s for s in CODIGOS_PRESTACIONALES_CATEGORIZADOS if query in s['codigo'].lower() or query in s['descripcion'].lower()]
    return jsonify({'suggestions': suggestions})

@app.route('/get_actividades_por_codigo/<string:codigo>', methods=['GET'])
def get_actividades_por_codigo(codigo):
    if not obtener_usuario_desde_token(request):
        return jsonify({"error": "No autorizado"}), 401
    codigos_actividad = RELACION_CODIGO_ACTIVIDADES.get(codigo, RELACION_CODIGO_ACTIVIDADES.get('DEFAULT', []))
    actividades_sugeridas = [{'codigo': c, 'descripcion': ACTIVIDADES_PREVENTIVAS_MAP.get(c, 'Desc no encontrada')} for c in sorted(list(codigos_actividad))]
    return jsonify({'actividades': actividades_sugeridas})

if __name__ == '__main__':
    app.run(debug=True)
