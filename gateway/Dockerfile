# Usa una imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de tu proyecto al contenedor
COPY requirements.txt .

# Instala las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expón el puerto en el que corre el gateway FastAPI
EXPOSE 8080

# Comando para ejecutar el servidor FastAPI
CMD ["uvicorn", "gateway:app", "--host", "0.0.0.0", "--port", "8080"]
