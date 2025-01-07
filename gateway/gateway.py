from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import httpx
import json
import os
import jwt
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# URL del microservicio Flask
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://flask-api:5000")
FILM_SERVICE_URL = os.getenv("FILM_SERVICE_URL", "http://film_microservice:3000")

# Cliente HTTP
client = httpx.AsyncClient()

# Crear la aplicación FastAPI con la documentación personalizada
app = FastAPI(
    title="CineView API Gateway",
    description="Este es un gateway que redirige solicitudes y combina la documentación OpenAPI de CineView y sus microservicios.",
    version="1.0.0",
    docs_url="/docs",  # Ruta personalizada para la UI de Swagger
    redoc_url="/redoc"  # Ruta personalizada para la documentación en ReDoc
)

# JWT:
SECRET_KEY = "s_ke1"
ALGORITHM = "HS256"

# Seguridad para extraer el token
security = HTTPBearer()

# Función para verificar el JWT
def verify_jwt(http_authorization_credentials: str = Depends(security)):
    """Verifica JWT en solicitudes protegidas.
    Mediante Depends() podemos hacer una inyección de dependencia.
    """
    try:
        token = http_authorization_credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
# Esta funcion genera un token JWT.
# Este token es usado para que los microservicios solo respondan solicitudes
# provenientes del gateway
def generate_service_token():
    payload = {
        "sub": "gateway",  # Identidad del emisor
        "exp": datetime.utcnow() + timedelta(minutes=10)  # Expiración
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token



# Endpoint de proxy para el microservicio de USUARIOS
@app.api_route("/register", methods=["POST"])
async def register_proxy(request: Request):
    return await proxy_request(request, USER_SERVICE_URL)

@app.api_route("/login", methods=["POST"])
async def login_proxy(request: Request):
    response = await proxy_request(request, USER_SERVICE_URL)
    if response.status_code == 200:  # Login exitoso
        body = await request.json()
        username = body.get("username")
        if not username:
            raise HTTPException(status_code=400, detail="Username is required")
        # Crear el JWT
        payload = {
            "sub": username,
            "exp": datetime.utcnow() + timedelta(hours=2),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=response.status_code, detail="Login failed")


@app.api_route("/add_review", methods=["POST"])
async def add_review_proxy(request: Request, payload: dict = Depends(verify_jwt)):
    """Proxy para agregar reseñas, protegido por JWT."""
    # El payload contiene los datos decodificados del token
    return await proxy_request(request, USER_SERVICE_URL)
@app.api_route("/get_reviews_for_film_id", methods=["POST"])
async def register_proxy(request: Request):
    return await proxy_request(request, USER_SERVICE_URL)
# Endpoint de proxy para el microservicio de PELICULAS
@app.api_route("/pelicula/{id}", methods=["GET"])
async def get_pelicula_proxy(request: Request):
    return await proxy_request(request, FILM_SERVICE_URL)

@app.api_route("/director/{id}", methods=["GET"])
async def get_director_proxy(request: Request):
    return await proxy_request(request, FILM_SERVICE_URL)

@app.api_route("/actor/{id}", methods = ["GET"])
async def get_actor_proxy(request: Request):
    return await proxy_request(request, FILM_SERVICE_URL)
@app.api_route("/peliculas", methods = ["GET"])
async def get_all_peliculas_proxy(request: Request):
    return await proxy_request(request, FILM_SERVICE_URL)

# Función para reenviar las solicitudes al rest de microservicios
async def proxy_request(request: Request, service_url: str):
    method = request.method
    token = generate_service_token() # Generamos el token que autentica al gateway
    url = f"{service_url}{request.url.path}"
    print(f"Redirect to: {url}")
    headers = dict(request.headers)
    headers["Authorization"] = f"Bearer {token}"
    content = await request.body()

    try:
        response = await client.request(method, url, headers=headers, content=content)
        return  JSONResponse(status_code=response.status_code, content=response.json())
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

# Sobrescribir el esquema OpenAPI de FastAPI con las especificaciones combinadas
@app.on_event("startup")
async def load_combined_openapi():
    try:
        # FLASK:
        # Solicitar la especificación OpenAPI desde el microservicio Flask
        response = await client.get(f"{USER_SERVICE_URL}/openapi.json")
        response.raise_for_status()  # Lanza un error si la solicitud falla
        flask_openapi = response.json()

        # NODE:
        response = await client.get(f"{FILM_SERVICE_URL}/openapi.json")
        response.raise_for_status()  # Lanza un error si la solicitud falla
        node_openapi = response.json()


        # Modificar la especificación local de FastAPI para incluir las rutas del microservicio Flask y Node
        if not app.openapi_schema:
            app.openapi_schema = app.openapi()

        # COMBINE
        # Combinar las especificaciones OpenAPI
        combined_paths = {**app.openapi_schema.get("paths", {}),
                            **flask_openapi.get("paths", {}),
                            **node_openapi.get("paths", {})}
        combined_components = {**app.openapi_schema.get("components", {}),
                                **flask_openapi.get("components", {}), 
                                **node_openapi.get("components", {})}

        # Crear el nuevo esquema combinado
        app.openapi_schema = {
            "openapi": "3.0.0",
            "info": app.openapi_schema["info"],
            "paths": combined_paths,
            "components": combined_components,
        }

    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Error al cargar OpenAPI del microservicio Flask")
    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail="Error de conexión con el microservicio Flask")

# Cerrar el cliente
@app.on_event("shutdown")
async def shutdown():
    await client.aclose()

# Servicio de paginas HTML:

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
# Pagina principal
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.get("/register_user", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("register_user.html", {"request": request})
@app.get("/home_page", response_class=HTMLResponse)
async def home_page(request: Request):
    # Hacer una solicitud para obtener todas las películas
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8080/peliculas")
        peliculas = response.json()

    # Pasar las películas a la plantilla
    return templates.TemplateResponse("home_page.html", {"request": request, "peliculas": peliculas})
@app.get("/film_page/{id_pelicula}", response_class=HTMLResponse)
async def read_film_page(request: Request, id_pelicula: int):
    # Obtener la información de la película
    async with httpx.AsyncClient() as client:
        pelicula_response = await client.get(f"http://localhost:8080/pelicula/{id_pelicula}")
        pelicula = pelicula_response.json()

        # Obtener los actores de la película
        actores = [(actor["nombre"], actor["id"], actor["foto"]) for actor in pelicula["actores"]]

        # Obtener los directores de la película
        directores = [(director["nombre"], director["id"], director["foto"]) for director in pelicula["directores"]]
        
        
        # Obtener las reseñas de la película
        reviews_response = await client.post("http://localhost:8080/get_reviews_for_film_id", json={"movie_id": id_pelicula})
        reviews = reviews_response.json().get("reviews", [])

    # Pasar los datos a la plantilla
    return templates.TemplateResponse(
        "film_page.html",
        {
            "request": request,
            "nombre": pelicula["titulo"],
            "anio": pelicula["año"],
            "actores": actores,
            "directores": directores,
            "sinopsis": pelicula["sinopsis"],
            "foto_car_tula": pelicula["foto"],
            "reviews": reviews,
        }
    )

@app.get("/director_page/{id_director}", response_class=HTMLResponse)
async def read_film_page(request: Request, id_director: int):
    # Obtenemos infor del director
    director_response = await client.get(f"http://localhost:8080/director/{id_director}")
    director = director_response.json()
    return templates.TemplateResponse("director_page.html", {"request": request, "director": director})

@app.get("/actor_page/{id}", response_class=HTMLResponse)
async def read_film_page(request: Request, id: int):
    # Obtenemos infor del director
    resp = await client.get(f"http://localhost:8080/actor/{id}")
    actor = resp.json()
    return templates.TemplateResponse("actor_page.html", {"request": request, "actor": actor})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("gateway:app", host="0.0.0.0", port=8080, reload=True)
