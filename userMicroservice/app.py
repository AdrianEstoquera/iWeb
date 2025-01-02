# app.py
from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from models import db, User, Review
from config import Config
from flask import jsonify
from flasgger import Swagger

app = Flask(__name__)

app.config.from_object(Config)
db.init_app(app)

# Cargar el blueprint de Swagger UI
SWAGGER_URL = '/swagger'
API_URL = '/static/openapi.yaml'  # Ruta donde se aloja el archivo OpenAPI
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
swagger = Swagger(app)


# Endpoint de registro de usuario
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400
    
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"msg": "User created successfully"}), 201

# Endpoint de login de usuario
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        # El token de acceso ahora será gestionado por el gateway
        return jsonify({"msg": "Login successful", "user_id": user.id}), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401

# Endpoint para añadir review
@app.route('/add_review', methods=['POST'])
def add_review():
    data = request.get_json()
    user_id = data.get('user_id')  # Recibimos el user_id directamente del JSON
    movie_id = data.get('movie_id')
    content = data.get('content')
    
    if not user_id or not movie_id or not content:
        return jsonify({"msg": "User ID, Movie ID, and content are required"}), 400
    
    review = Review(user_id=user_id, movie_id=movie_id, content=content)
    db.session.add(review)
    db.session.commit()
    
    return jsonify({"msg": "Review added successfully"}), 201

import yaml
import os

# Nuevo endpoint para proporcionar la especificación OpenAPI al gateway
@app.route('/openapi.json', methods=['GET'])
def openapi_spec():
    try:
        # Ruta al archivo YAML
        openapi_path = os.path.join(os.path.dirname(__file__), 'static', 'openapi.yaml')
        
        # Leer y cargar el archivo YAML
        with open(openapi_path, 'r') as file:
            openapi_yaml = yaml.safe_load(file)
        
        # Devolver el contenido como JSON
        return jsonify(openapi_yaml), 200
    except FileNotFoundError:
        return jsonify({"error": "El archivo openapi.yaml no se encontró"}), 404
    except yaml.YAMLError as e:
        return jsonify({"error": "Error al procesar el archivo YAML", "detail": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Error inesperado", "detail": str(e)}), 500
    
# Servicio para comprobar que el microservicio puede aceptar peticiones
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True)