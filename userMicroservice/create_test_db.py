# Este codigo genera una base de datos de prueba:
# create_test_db.py
from flask import Flask
from models import db, User, Review
from config import Config


# Inicializa la aplicación Flask y la configuración de la base de datos
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Función para crear la base de datos y añadir datos de prueba
def create_test_database():
    with app.app_context():
        # Elimina y crea todas las tablas definidas en models.py
        db.drop_all()
        db.create_all()
        
        # Añade usuarios de prueba
        user1 = User(username="testuser1")
        user1.set_password("password123")
        user2 = User(username="testuser2")
        user2.set_password("password456")
        
        # Añade los usuarios a la sesión
        db.session.add(user1)
        db.session.add(user2)
        
        # Añade reseñas de prueba
        review1 = Review(user_id=1, movie_id=101, content="Great movie!")
        review2 = Review(user_id=2, movie_id=102, content="Not bad.")
        
        # Añade las reseñas a la sesión
        db.session.add(review1)
        db.session.add(review2)
        
        # Guarda todos los cambios en la base de datos
        db.session.commit()
        
        print("Base de datos de prueba creada con datos iniciales.")

if __name__ == "__main__":
    create_test_database()
