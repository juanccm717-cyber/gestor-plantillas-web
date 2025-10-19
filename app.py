from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client
import os

app = Flask(__name__)

# --- Configuración de Supabase ---
# Es mejor usar variables de entorno, pero para simplificar, las ponemos aquí.
SUPABASE_URL = "https://ylzpvpgcelbsbdcauqzw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlsenB2cGdjZWxic2JkY2F1cXp3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3OTkzNzcsImV4cCI6MjA3NjM3NTM3N30.b4v7l5Js-Dju1DCJ4oTnP5e2wzvFpM0qHTS8PtCY7Fc"

# Crear el cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY )

# --- Rutas de la Aplicación ---

@app.route('/')
def index():
    """Sirve la página principal de la aplicación."""
    return render_template('index.html')

@app.route('/get_registros')
def get_registros():
    """Obtiene todos los registros de la tabla 'registros'."""
    try:
        # Selecciona todas las columnas de la tabla y las ordena por id.
        response = supabase.table('registros').select('*').order('id').execute()
        
        # response.data ya es una lista de diccionarios, justo lo que necesita el frontend.
        return jsonify(response.data)
    except Exception as e:
        print(f"Error en /get_registros: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/search_diagnosticos')
def search_diagnosticos():
    """Busca diagnósticos en la tabla 'diagnosticos'."""
    query = request.args.get('q', '')
    if not query or len(query) < 3:
        return jsonify([])
    try:
        # Busca tanto en la columna 'codigo' como en 'descripcion'
        response = supabase.table('diagnosticos').select('id, codigo, descripcion').ilike('descripcion', f'%{query}%').limit(10).execute()
        
        # Si no encuentra por descripción, busca por código
        if not response.data:
            response = supabase.table('diagnosticos').select('id, codigo, descripcion').ilike('codigo', f'%{query}%').limit(10).execute()

        return jsonify(response.data)
    except Exception as e:
        print(f"Error en /search_diagnosticos: {e}")
        return jsonify({"error": str(e)}), 500

# Esta sección permite ejecutar el servidor con `python app.py` y activa el modo debug
if __name__ == '__main__':
    app.run(debug=True)
