# Este codigo genera una base de datos de prueba:
# create_test_db.py
from flask import Flask
from models import db, User, Review
from config import Config
import random


# Inicializa la aplicación Flask y la configuración de la base de datos
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def add_review(user_id, movie_id, session):
    good_reviews = [
    "Qué obra maestra. Me dejó sin palabras.",
    "Una experiencia inolvidable. Diez de diez.",
    "El final me emocionó hasta las lágrimas.",
    "Increíble dirección y actuaciones.",
    "Cada escena era un regalo visual.",
    "Wow. Me mantuvo al borde del asiento.",
    "Espectacular. Una joya del cine.",
    "Los personajes eran tan reales.",
    "Quiero verla otra vez.",
    "La música era pura magia.",
    "Risas, lágrimas y todo lo demás. Perfecta.",
    "El guion fue una genialidad.",
    "Un viaje emocional como ningún otro.",
    "El giro final me dejó boquiabierto.",
    "Cinematografía espectacular. Arte puro.",
    "Definitivamente una de mis favoritas.",
    "Una película que recordaré para siempre.",
    "Simplemente perfecta. Bravo.",
    "Una montana rusa de emociones.",
    "Gran historia, gran ejecución.",
    "Pura magia del cine.",
    "El elenco fue impresionante.",
    "Cada minuto fue fascinante.",
    "Me atrapó desde la primera escena.",
    "Altamente recomendable.",
    "Un tesoro escondido del cine.",
    "La actuación principal fue magistral.",
    "Perfecta para los amantes del cine.",
    "Llena de sorpresas y emociones.",
    "El director hizo un trabajo excepcional.",
    "No puedo esperar a verla otra vez.",
    "El mensaje detrás era tan poderoso.",
    "Una experiencia transformadora.",
    "Cautivadora de principio a fin.",
    "Una película que vale la pena cada minuto.",
    "Poesía visual en su máxima expresión.",
    "Las actuaciones secundarias también fueron geniales.",
    "Un clásico moderno.",
    "Qué espectáculo visual.",
    "El desarrollo de personajes fue impecable.",
    "Impresionante de principio a fin.",
    "La mejor que he visto este ano.",
    "Me hizo pensar mucho. Brillante.",
    "Una verdadera obra de arte.",
    "La química entre los actores era increíble.",
    "Totalmente imperdible.",
    "De esas películas que no quieres que terminen.",
    "Te deja reflexionando mucho tiempo después.",
    "Sencillamente brillante.",
    "El mejor final que he visto.",
    "Una experiencia cinematográfica única.",
    ]

    bad_reviews = [
    "Oh, genial. Otra película que nunca recordaré.",
    "Qué desastre tan elaborado.",
    "La peor película en anos, pero al menos es consistente.",
    "Por supuesto, alguien pensó que esto era arte.",
    "Los personajes eran tan profundos como un charco.",
    "El guion era como una broma interna. No divertida.",
    "Me dormí, lo que fue lo mejor que me pasó viendo esto.",
    "El final… Bueno, había un final.",
    "Tan memorable como mis tareas de la secundaria.",
    "Actuaciones que solo la familia del elenco podría elogiar.",
    "Predecible, pero al menos terminó.",
    "El presupuesto claramente se fue en café, no en la película.",
    "Un proyecto escolar con mejores intenciones.",
    "Ah, el viejo truco del cliché eterno.",
    "¿Se puede devolver el tiempo perdido?",
    "Perfecto para arrepentirse de tus elecciones.",
    "La música estaba… presente.",
    "Esto redefine los estándares de lo mediocre.",
    "Las escenas de acción eran casi graciosas. Casi.",
    "Nada tenía sentido, pero eso parece ser el punto.",
    "Un derroche de talento que nunca verán de vuelta.",
    "No es ni lo suficientemente mala como para reírse.",
    "La cinematografía era como una pintura… sin pintar.",
    "Una decepción más para la colección.",
    "Las buenas críticas deben ser parte de la ficción.",
    "Un guion con más agujeros que un queso suizo.",
    "Intentaron algo. Eso es lo mejor que puedo decir.",
    "La química entre los actores era tan eléctrica como una roca.",
    "Un tributo involuntario a todo lo que no funciona en cine.",
    "Esto pasó controles de calidad, aparentemente.",
    "Simplemente una película. Eso es todo.",
    "Perfecto para los que disfrutan ver pintura secarse.",
    "Cine experimental, en el peor sentido posible.",
    "Efectos especiales dignos de un videojuego de los 90.",
    "El desenlace fue como un mal chiste, pero sin remate.",
    "Fue difícil terminarla, pero la terminé. Lamentablemente.",
    "Carece de alma, pero al menos tiene créditos finales.",
    "Los diálogos eran como poesía… de aficionados.",
    "Quién pensó que esta idea era buena necesita un descanso.",
    "Humor tan efectivo como un chiste sin gracia.",
    "Nada sorprendente, pero eso no sorprende.",
    "Si el robo fuera legal, esta película sería el ejemplo perfecto.",
    "Emoción y energía están en otra película.",
    "Algo que debería quedarse en la sala de edición. Para siempre.",
    "Inolvidable… Por razones que preferirías olvidar.",
    ]


    if random.randint(0,1) == 1:
        content = random.choice(good_reviews)
    else:
        content = random.choice(bad_reviews)
    new_review = Review(user_id=user_id, movie_id=movie_id, content=content)
    session.add(new_review)

# Función para crear la base de datos y anadir datos de prueba
def create_test_database():
    with app.app_context():
        # Elimina y crea todas las tablas definidas en models.py
        db.drop_all()
        db.create_all()
        
        # Anade usuarios de prueba
        user1 = User(username="testuser1")
        user1.set_password("password123")
        user2 = User(username="testuser2")
        user2.set_password("password456")
        
        # Anade los usuarios a la sesión
        db.session.add(user1)
        db.session.add(user2)
        
        # Anade resenas de prueba
        review1 = Review(user_id=1, movie_id=101, content="Great movie!")
        review2 = Review(user_id=2, movie_id=102, content="Not bad.")
        
        # Anade las resenas a la sesión
        db.session.add(review1)
        db.session.add(review2)

        for i in range(1, 3):
            print(f"user ID: {i}")
            for j in range(250):
                print(f"Film: {j}")
                add_review(i, j, db.session)
            print("-----------------------------")
        
        # Guarda todos los cambios en la base de datos
        db.session.commit()
        
        print("Base de datos de prueba creada con datos iniciales.")

if __name__ == "__main__":
    create_test_database()
