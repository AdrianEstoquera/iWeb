# Usa una imagen base de Python
FROM python:3.9

# Establece el directorio de trabajo
WORKDIR /app/userMicroservice

# Copia los archivos de tu proyecto al contenedor
COPY requirements.txt .

# Instala las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expón el puerto en el que corre la app Flask
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
