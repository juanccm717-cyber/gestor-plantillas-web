from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from supabase import create_client, Client
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
# Clave secreta para manejar las sesiones de login
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'una-clave-secreta-muy-dificil-de-adivinar')

# --- Configuración de Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Configuración de Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Si un usuario no logueado intenta acceder a una página protegida, lo redirige a /login

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
    # La página principal ahora es el login
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
        
        flash('Usuario o contraseña incorrectos', 'error')
        return render_template('login.html', error='Usuario o contraseña incorrectos')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Rutas de la Aplicación (Protegidas) ---

@app.route('/menu')
@login_required
def menu_principal():
    """Sirve la página del menú principal, pasando el rol del usuario."""
    return render_template('menu.html', role=current_user.role)

@app.route('/plantillas')
@login_required
def gestor_plantillas():
    """Sirve la página del gestor de plantillas."""
    return render_template('gestor.html')

# --- Rutas de la API (Protegidas) ---

@app.route('/get_registros')
@login_required
def get_registros():
    try:
        response = supabase.table('registros').select('*').order('id').execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
# ... (Otras rutas de API irían aquí y también deberían tener @login_required) ...

if __name__ == '__main__':
    app.run(debug=True)
