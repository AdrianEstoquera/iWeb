from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import json
import os

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

# Endpoint de proxy para el microservicio de USUARIOS
@app.api_route("/register", methods=["POST"])
async def register_proxy(request: Request):
    return await proxy_request(request, USER_SERVICE_URL)

@app.api_route("/login", methods=["POST"])
async def login_proxy(request: Request):
    return await proxy_request(request, USER_SERVICE_URL)

@app.api_route("/add_review", methods=["POST"])
async def add_review_proxy(request: Request):
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

# Función para reenviar las solicitudes al microservicio Flask
async def proxy_request(request: Request, service_url: str):
    method = request.method
    url = f"{service_url}{request.url.path}"
    print(f"Redirect to: {url}")
    headers = dict(request.headers)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("gateway:app", host="0.0.0.0", port=8080, reload=True)
