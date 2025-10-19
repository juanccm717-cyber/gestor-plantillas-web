from flask import Flask, render_template, request, jsonify, redirect, url_for
from supabase import create_client, Client
import os
from werkzeug.security import check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'clave-secreta-por-defecto')

# --- Configuración de Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Configuración de Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    response = supabase.table('usuarios').select('*').eq('id', user_id).execute()
    if response.data:
        user_data = response.data[0]
        return User(id=user_data['id'], username=user_data['username'], role=user_data['role'])
    return None

# --- Rutas de Autenticación ---
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        response = supabase.table('usuarios').select('*').eq('username', username).execute()
        if response.data:
            user_data = response.data[0]
            if check_password_hash(user_data['password_hash'], password):
                user = User(id=user_data['id'], username=user_data['username'], role=user_data['role'])
                login_user(user)
                return redirect(url_for('menu_principal'))
        return render_template('login.html', error='Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Rutas de la Aplicación ---
@app.route('/menu')
@login_required
def menu_principal():
    return render_template('menu.html', role=current_user.role)

@app.route('/plantillas')
@login_required
def gestor_plantillas_vista():
    """Muestra el gestor en modo 'solo vista'."""
    return render_template('gestor.html', modo='vista')

@app.route('/plantillas/crear')
@login_required
def gestor_plantillas_crear():
    """Muestra el gestor en modo 'crear/editar'."""
    if current_user.role != 'administrador':
        return redirect(url_for('menu_principal')) # Seguridad extra
    return render_template('gestor.html', modo='editar')

# --- Rutas de la API ---
@app.route('/get_registros')
@login_required
def get_registros():
    try:
        response = supabase.table('registros').select('*').order('id').execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search_diagnosticos')
@login_required
def search_diagnosticos():
    query = request.args.get('q', '')
    if not query or len(query) < 3:
        return jsonify([])
    try:
        response = supabase.table('diagnosticos').select('id, codigo, descripcion').ilike('descripcion', f'%{query}%').limit(10).execute()
        if not response.data:
            response = supabase.table('diagnosticos').select('id, codigo, descripcion').ilike('codigo', f'%{query}%').limit(10).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
@app.route('/guardar_plantilla', methods=['POST'])
@login_required
def guardar_plantilla():
    if current_user.role != 'administrador':
        return jsonify({"error": "No tienes permiso para realizar esta acción"}), 403

    datos = request.get_json()
    
    # Aquí iría la lógica para insertar los datos en la tabla 'registros' de Supabase
    try:
        # La data que llega del frontend debe coincidir con las columnas de la tabla
        response = supabase.table('registros').insert(datos).execute()
        if len(response.data) > 0:
            return jsonify({"success": True, "data": response.data[0]}), 201
        else:
             raise Exception("La inserción no devolvió datos.")
    except Exception as e:
        print(f"Error al guardar plantilla: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
