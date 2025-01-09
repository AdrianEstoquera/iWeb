# app.py
from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from models import db, User, Review
from config import Config
from flask import jsonify
from flasgger import Swagger
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

app = Flask(__name__)

app.config.from_object(Config)
db.init_app(app)

# Cargar el blueprint de Swagger UI
SWAGGER_URL = '/swagger'
API_URL = '/static/openapi.yaml'  # Ruta donde se aloja el archivo OpenAPI
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
swagger = Swagger(app)

# JWT middleware:
SECRET_KEY = "s_ke1"
def verify_jwt():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"msg": "Missing or invalid token"}), 401
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except ExpiredSignatureError:
        return jsonify({"msg": "Token expired"}), 401
    except InvalidTokenError:
        return jsonify({"msg": "Invalid token"}), 401



# Endpoint de registro de usuario
@app.route('/register', methods=['POST'])
def register():
    # Validar JWT
    validation_response = verify_jwt()
    if isinstance(validation_response, tuple):  # Si hubo error
        return validation_response
    
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
    # Validar JWT
    validation_response = verify_jwt()
    if isinstance(validation_response, tuple):  # Si hubo error
        return validation_response
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        # El token de acceso ahora será gestionado por el gateway
        return jsonify({"msg": "Login successful", "user_id": user.id}), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401
import logging

logging.basicConfig(level=logging.DEBUG)

@app.route('/add_review', methods=['POST'])
def add_review():
    # Validar JWT
    validation_response = verify_jwt()
    if isinstance(validation_response, tuple):  # Si hubo error
        return validation_response

    try:
        data = request.get_json()
        app.logger.debug(f"Datos recibidos: {data}")  # Usamos logger en lugar de print
    except Exception as e:
        app.logger.error(f"Error al leer JSON: {str(e)}")
        return jsonify({"msg": "Invalid JSON format"}), 400

    user_id = data.get('user_id')
    movie_id = data.get('movie_id')
    content = data.get('content')

    # if not user_id or not movie_id or not content:
    #     return jsonify({"msg": "User ID, Movie ID, and content are required"}), 400

    review = Review(user_id=user_id, movie_id=movie_id, content=content)
    db.session.add(review)
    db.session.commit()

    return jsonify({"msg": "Review added successfully"}), 201

@app.route("/get_reviews_for_film_id", methods=["POST"])
def get_reviews_for_film_id():
    # Validar JWT
    validation_response = verify_jwt()
    if isinstance(validation_response, tuple):  # Si hubo error
        return validation_response
    
    # Obtener el ID de la película del cuerpo de la solicitud
    data = request.get_json()
    movie_id = data.get('movie_id')

    # Verificar que se haya proporcionado un movie_id
    if not movie_id:
        return jsonify({"msg": "Movie ID is required"}), 400
    
    # Obtener las reviews de la base de datos para la película especificada con el username
    reviews = db.session.query(Review, User).join(User, Review.user_id == User.id).filter(Review.movie_id == movie_id).all()
    
    # Si no hay reseñas, retornar un mensaje indicando que no hay reseñas para esa película
    if not reviews:
        return jsonify({"reviews": []}), 404
    
    # Formatear las reseñas para devolverlas de manera estructurada
    reviews_data = []
    for review, user in reviews:
        reviews_data.append({
            "username": user.username,
            "content": review.content,
        })
    
    return jsonify({"reviews": reviews_data}), 200

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
