# Usar una imagen oficial de Node.js
FROM node:16

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el package.json y package-lock.json (si existe)
COPY package*.json ./

# Instalar las dependencias
RUN npm install

# Copiar todo el código del proyecto al contenedor
COPY . .

# Exponer el puerto en el que correrá el servidor
EXPOSE 3000

# Ejecutar el servidor con un retraso de 60 segundos al iniciar el contenedor
CMD ["sh", "-c", "sleep 60 && node server.js"]
