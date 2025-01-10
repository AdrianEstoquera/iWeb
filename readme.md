# 🎬 CineView
- [🎬 CineView](#-cineview)
   * [👨‍💻 Software que se necesita instalar](#-software-que-se-necesita-instalar)
      + [🐳 Docker](#-docker)
         - [📥 Instalación](#-instalación)
      + [⚡ Node.js](#-nodejs)
         - [📥 Instalación](#-instalación-1)
      + [🐍 Python](#-python)
         - [📥 Instalación](#-instalación-2)
      + [📊 R (Obligatorio)](#-r-obligatorio)
         - [📥 Instalación](#-instalación-3)
   * [🏁 Servicios que hay que arrancar](#-servicios-que-hay-que-arrancar)
      + [💿 mysql-container:](#-mysql-container)
         - [Configuración del Contenedor](#configuración-del-contenedor)
         - [Variables de Entorno](#variables-de-entorno)
         - [Healthcheck](#healthcheck)
         - [Uso](#uso)
            * [Requisitos Previos](#requisitos-previos)
            * [Ejecución](#ejecución)
      + [📀 Neo4j Microservice](#-neo4j-microservice)
         - [Descripción](#descripción)
         - [Configuración](#configuración)
         - [Variables de Entorno](#variables-de-entorno-1)
      + [🎥 Film Microservice](#-film-microservice)
         - [Descripción](#descripción-1)
         - [Configuración](#configuración-1)
         - [Variables de Entorno](#variables-de-entorno-2)
         - [Dependencias](#dependencias)
         - [Healthcheck](#healthcheck-1)
      + [👥 User Microservice](#-user-microservice)
         - [Descripción](#descripción-2)
         - [Configuración](#configuración-2)
      + [Dependencias](#dependencias-1)
      + [Healthcheck](#healthcheck-2)
      + [🏛️ FastAPI Gateway](#-fastapi-gateway)
         - [Descripción](#descripción-3)
         - [Configuración](#configuración-3)
         - [Variables de Entorno](#variables-de-entorno-3)
         - [Dependencias](#dependencias-2)
      + [🤜🤛 Orden de Dependencias](#-orden-de-dependencias)
   * [📦 Dependencias que hay que instalar](#-dependencias-que-hay-que-instalar)
      + [🐍 Flask](#-flask)
      + [🏛️ Fastapi](#-fastapi)
      + [🟩 Node](#-node)
      + [📊R](#r)
   * [💻 Cómo arrancar la parte servidora](#-cómo-arrancar-la-parte-servidora)
      + [🗃️ Poblar la Base de Datos](#-poblar-la-base-de-datos)
         - [Poblar MySQL](#poblar-mysql)
         - [Poblar Neo4j](#poblar-neo4j)
      + [🛠️ Dockerfiles de los Microservicios](#-dockerfiles-de-los-microservicios)
      + [1. **User Microservice (Flask)** ](#1-user-microservice-flask)
      + [2. **Gateway (FastAPI)**](#2-gateway-fastapi)
      + [3. **Film Microservice (Node.js)**](#3-film-microservice-nodejs)
   * [🌐 Cómo acceder a la parte cliente](#-cómo-acceder-a-la-parte-cliente)
## 👨‍💻 Software que se necesita instalar

### 🐳 Docker
Docker es esencial para ejecutar los microservicios en contenedores.
Hay que instalar

- **Docker Engine**: Para gestionar contenedores.
- **Docker Compose**: Para orquestar múltiples contenedores definidos en un archivo `docker-compose.yml`.

#### 📥 Instalación
Instala Docker y Docker Compose desde su [sitio oficial](https://www.docker.com/).

---

### ⚡ Node.js
Se requiere para desarrollar y ejecutar scripts escritos en JavaScript.

- **Versión Recomendada**: 18.x o superior (LTS).

#### 📥 Instalación
Descárgalo desde el [sitio oficial de Node.js](https://nodejs.org/).

---

### 🐍 Python
El microservicio `user_microservice` está escrito en Flask, que usa Python. Aunque todo está configurado para ejecutarse en Docker, puede ser útil tener Python instalado para depurar localmente.

- **Versión Recomendada**: 3.8 o superior.

#### 📥 Instalación
Descárgalo desde el [sitio oficial de Python](https://www.python.org/).
---

### 📊 R (Obligatorio)
El lenguaje de programación R es **obligatorio** para ejecutar el **scrapper web**

#### 📥 Instalación
Descarga e instala R desde su [sitio oficial](https://cran.r-project.org/).

---

## 🏁 Servicios que hay que arrancar
### 💿 mysql-container:
Este microservicio utiliza un contenedor de Docker basado en la imagen oficial de MySQL 8.0. Proporciona una base de datos configurada para el sistema **CineView**.

#### Configuración del Contenedor

- **Imagen**: `mysql:8.0`
- **Nombre del Contenedor**: `mysql-container`
- **Puertos**: 
  - Externo: `3307`
  - Interno: `3306`
- **Red**: `cineview-network`
- **Volumen Persistente**: 
  - Se utiliza `mysql_data` para almacenar los datos de la base de datos de manera persistente en `/var/lib/mysql`.

#### Variables de Entorno

El contenedor está configurado con las siguientes variables de entorno:

- `MYSQL_ROOT_PASSWORD`: Contraseña para el usuario `root` (`rootpass`).
- `MYSQL_DATABASE`: Nombre de la base de datos creada automáticamente al iniciar (`cineViewUsers`).
- `MYSQL_USER`: Usuario adicional de la base de datos (`cinemaViewWeb`).
- `MYSQL_PASSWORD`: Contraseña del usuario adicional (`pass`).

#### Healthcheck

El contenedor incluye una comprobación de salud para verificar el estado del servicio MySQL:

- **Comando**: `mysqladmin ping -h localhost -uroot -prootpass`
- **Intervalo**: 10 segundos.
- **Tiempo de espera**: 5 segundos.
- **Reintentos**: 3.

#### Uso

Pensado para proporcionar almacenamiento de datos de usuarios

##### Requisitos Previos

- Docker y Docker Compose instalados.
- Red de Docker llamada `cineview-network` configurada previamente.

##### Ejecución

Para ejecutar este contenedor, asegúrate de tener configurado el archivo `docker-compose.yml` correspondiente y usa el siguiente comando:

```bash
docker-compose up -d
```
### 📀 Neo4j Microservice

#### Descripción
Este microservicio proporciona una base de datos gráfica basada en Neo4j para gestionar datos relacionados con películas en **CineView**.

#### Configuración
- **Nombre del Contenedor**: `neo4j-container`
- **Puertos**: 
  - `7474:7474` (interfaz web)
  - `7687:7687` (protocolo Bolt)
- **Volumen Persistente**: 
  - `neo4j_data:/data`
  - `neo4j_logs:/logs`
- **Red**: `cineview-network`

#### Variables de Entorno
- `NEO4J_AUTH`: Usuario y contraseña (`neo4j/neo4jpassword`).

---

### 🎥 Film Microservice

#### Descripción
Este microservicio gestiona los datos relacionados con las películas en el sistema **CineView**, utilizando Neo4j como base de datos.

#### Configuración
- **Nombre del Contenedor**: `film-api`
- **Puerto**: `3000:3000`
- **Volúmenes**: 
  - `neo4j_data:/data`
  - `neo4j_logs:/logs`
- **Red**: `cineview-network`

#### Variables de Entorno
- `NEO4J_HOST`: `neo4j`
- `NEO4J_PORT`: `7687`
- `NEO4J_USER`: `neo4j`
- `NEO4J_PASSWORD`: `neo4jpassword`
- `FILM_SERVICE_URL`: `http://film_microservice:3000`

#### Dependencias
- Depende de **Neo4j Microservice**.

#### Healthcheck
- **Comando**: `curl -f http://localhost:3000/health`
- **Reintentos**: 10

---

### 👥 User Microservice

#### Descripción
Este microservicio, construido con Flask, gestiona los usuarios del sistema **CineView**. Requiere acceso a la base de datos MySQL.

#### Configuración
- **Nombre del Contenedor**: `flask-api`
- **Puerto**: `5000:5000`
- **Red**: `cineview-network`

### Dependencias
- Depende de **MySQL Microservice**.

### Healthcheck
- **Comando**: `curl -f http://localhost:5000/health`
- **Reintentos**: 3

---

### 🏛️ FastAPI Gateway

#### Descripción
El gateway es el punto de entrada centralizado para el sistema **CineView**. Proporciona una interfaz unificada y enruta las solicitudes a los microservicios apropiados.

#### Configuración
- **Nombre del Contenedor**: `fastapi-gateway`
- **Puerto**: `8080:8080`
- **Red**: `cineview-network`

#### Variables de Entorno
- `USER_SERVICE_URL`: `http://user_microservice:5000`
- `FILM_SERVICE_URL`: `http://film_microservice:3000`

#### Dependencias
- Depende de:
  - **User Microservice**
  - **Film Microservice**

---

### 🤜🤛 Orden de Dependencias

1. **MySQL Microservice**: Necesario para el **User Microservice**.
2. **Neo4j Microservice**: Necesario para el **Film Microservice**.
3. **Film Microservice**: Necesario para el **FastAPI Gateway**.
4. **User Microservice**: Necesario para el **FastAPI Gateway**.
5. **FastAPI Gateway**: Punto de entrada principal para el sistema.

## 📦 Dependencias que hay que instalar
Para **Flask** y  **FastApi**, la gestión de paquetes es llevada a cabo mediante un fichero requirements.txt para cada microservicio. 
**Node** gestiona sus dependencias mediante *package.json*.
**R** gestiona sus dependencias en el propio script
### 🐍 Flask
```
Flask==2.0.3
flask-swagger-ui==3.36.0
flask-openapi3==4.0.1
httpx==0.23.0
flask_sqlalchemy==2.5.1
Werkzeug==2.0.3
SQLAlchemy==1.4.49
flasgger
pymysql
cryptography
pyjwt==2.4.0
```
### 🏛️ Fastapi
```
fastapi==0.75.0
uvicorn[standard]==0.17.6
httpx==0.25.1
motor==2.5.1
pydantic==1.9.0
PyJWT==2.7.0
jinja2
aiofiles

```
### 🟩 Node
- express: ^4.18.2
- neo4j-driver: ^5.7.0
- swagger-ui-express: ^4.6.2
- yaml: ^2.2.1
- winston: ^3.10.0
- jsonwebtoken: ^8.5.1

### 📊R
```r
# Instalación de paquetes
install.packages("neo4r")     # Para interactuar con bases de datos Neo4j
install.packages("tidyverse") # Conjunto de paquetes para manipulación de datos
install.packages("rvest")     # Permite realizar web scraping
install.packages("polite")    # Verificación de robots.txt para web scraping
install.packages("promises")  # Para trabajar con promesas (funcionalidades asincrónicas)
```
## 💻 Cómo arrancar la parte servidora

Para iniciar los microservicios de la aplicación, puedes usar Docker Compose, lo cual facilitará la creación y gestión de los contenedores para cada uno de los servicios. Para arrancar el sistema, solo necesitas ejecutar el siguiente comando:

```bash
docker-compose up
```
Esto arrancará todos los microservicios definidos en el archivo docker-compose.yml, incluyendo la base de datos MySQL, Neo4j, el microservicio de usuarios (Flask), el microservicio de películas (Node.js) y el gateway (FastAPI).
### 🗃️ Poblar la Base de Datos
#### Poblar MySQL
Para poblar la base de datos MySQL, dentro del contenedor de userMicroservice existe un script Python llamado create_test_db.py. Este script se encarga de poblar la base de datos con datos de prueba que el sistema puede usar para la gestión de usuarios.

Para ejecutarlo, accede al contenedor de userMicroservice y ejecuta el siguiente comando:
```bash
docker exec -it flask-api python /app/userMicroservice/create_test_db.py
```
Esto ejecutará el script create_test_db.py, el cual insertará los datos iniciales necesarios en la base de datos cineViewUsers.
#### Poblar Neo4j
En cuanto a la base de datos de Neo4j, hay dos métodos posibles para poblarla:

1. Usar el script create_test_db.js: Dentro del microservicio de Node.js, existe un script JavaScript llamado create_test_db.js. Este script puede poblar Neo4j con datos iniciales. Para ejecutarlo, ingresa al contenedor de film_microservice y ejecuta el siguiente comando:
```bash
docker exec -it film-api node /app/filmMicroService/create_test_db.js

```
2. Usar el scrapper hecho en R (Recomendado): El método más recomendado para poblar Neo4j es utilizar un scrapper desarrollado en R. Este scrapper extrae los datos de IMDb que realmente se utilizan en la aplicación y los inserta en Neo4j utilizando el paquete neo4r. 
    Ejecuta el script de scrapping en R que usa neo4r para cargar los datos en la base de datos Neo4j siempre y cuando **el contenedor de Neo4j este activo**.

### 🛠️ Dockerfiles de los Microservicios
### 1. **User Microservice (Flask)** 

- **Base Image**: Utiliza una imagen base de Python 3.9.
- **Directorio de Trabajo**: Establece el directorio de trabajo dentro del contenedor en `/app/userMicroservice`, que es donde se almacenan los archivos del proyecto.
- **Instalación de Dependencias**: Copia el archivo `requirements.txt` al contenedor y luego instala las dependencias de Python listadas en ese archivo usando `pip`.
- **Copia de Archivos**: Copia todos los archivos del proyecto al contenedor.
- **Exposición del Puerto**: Expone el puerto 5000, que es el puerto donde Flask escuchará las peticiones HTTP.
- **Comando de Ejecución**: Define que el contenedor debe ejecutar el servidor Flask, indicando que debe escuchar en todas las interfaces de red (`--host=0.0.0.0`) en el puerto 5000.

### 2. **Gateway (FastAPI)**

- **Base Image**: Utiliza una versión más ligera de Python 3.9 llamada `python:3.9-slim`.
- **Directorio de Trabajo**: Establece el directorio de trabajo en `/app`, donde se almacenan los archivos del proyecto.
- **Instalación de Dependencias**: Copia el archivo `requirements.txt` y usa `pip` para instalar las dependencias necesarias.
- **Copia de Archivos**: Copia todos los archivos del proyecto al contenedor.
- **Exposición del Puerto**: Expone el puerto 8080, donde FastAPI manejará las solicitudes.
- **Comando de Ejecución**: Configura el contenedor para ejecutar el servidor FastAPI utilizando `uvicorn` como servidor ASGI, especificando que debe escuchar en todas las interfaces (`--host=0.0.0.0`) y en el puerto 8080.

### 3. **Film Microservice (Node.js)**

- **Base Image**: Usa una imagen oficial de Node.js (versión 16) como base.
- **Directorio de Trabajo**: Establece el directorio de trabajo en `/app`, donde se colocarán los archivos del proyecto.
- **Instalación de Dependencias**: Copia los archivos `package.json` y `package-lock.json` para gestionar las dependencias de Node.js, y luego ejecuta `npm install` para instalar las dependencias del proyecto.
- **Copia de Archivos**: Copia todo el código del proyecto al contenedor.
- **Exposición del Puerto**: Expone el puerto 3000, donde el microservicio de películas escuchará las solicitudes.
- **Comando de Ejecución**: Establece que el servidor debe ejecutarse después de un retraso de 60 segundos (por ejemplo, para esperar a que otros servicios estén listos). Luego ejecuta `node server.js` para iniciar el servidor.

## 🌐 Cómo acceder a la parte cliente
Una vez que los microservicios estén corriendo, puedes acceder a la parte cliente desde tu navegador web utilizando la siguiente URL:
```
http://localhost:8080
```
Esta URL te llevará a la interfaz gestionada por el microservicio de FastAPI (Gateway), donde podrás interactuar con los demás servicios de la aplicació