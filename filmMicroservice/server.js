// Importar dependencias
const express = require('express');
const neo4j = require('neo4j-driver');
const swaggerUi = require('swagger-ui-express');
const fs = require('fs');
const path = require('path');
const yaml = require('yaml');
const winston = require('winston');
const jwt = require('jsonwebtoken');

// Configurar Winston
const logger = winston.createLogger({
  level: 'info', // Nivel de log: info, warn, error, etc.
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.printf(({ timestamp, level, message }) => {
      return `[${timestamp}] ${level.toUpperCase()}: ${message}`;
    })
  ),
  transports: [
    new winston.transports.Console(), // Logs a la consola
    new winston.transports.File({ filename: 'logs/server.log' }) // Logs a archivo
  ]
});

// JWT middleware:
const SECRET_KEY = "s_ke1";  // Clave secreta debe ser la misma

// Middleware para validar JWT
function verifyJwt(req, res, next) {
    const authHeader = req.headers['authorization'];
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({ msg: 'Missing or invalid token' });
    }
    
    const token = authHeader.split(' ')[1];
    try {
        const payload = jwt.verify(token, SECRET_KEY);
        req.payload = payload;  // Pasar el payload a la siguiente función
        next();
    } catch (error) {
        return res.status(401).json({ msg: 'Invalid token' });
    }
}

// Crear la aplicación Express
const app = express();
const port = 3000;

// Configuración de la conexión a Neo4j usando variables de entorno
const driver = neo4j.driver(
  `bolt://${process.env.NEO4J_HOST}:${process.env.NEO4J_PORT}`, // Usamos las variables de entorno del contenedor
  neo4j.auth.basic(process.env.NEO4J_USER, process.env.NEO4J_PASSWORD),
  { disableLosslessIntegers: true }
);

// Crear una sesión
const session = driver.session();

// Cargar configuración de OpenAPI desde el archivo YAML
const openapiFile = fs.readFileSync(path.join(__dirname, 'static', 'openapi.yml'), 'utf8');
const swaggerSpec = yaml.parse(openapiFile);

// Middleware de logging para solicitudes
app.use((req, res, next) => {
  logger.info(`Solicitud entrante: ${req.method} ${req.url}`);
  next();
});

// Endpoints
// Configuración de Swagger UI en `/api-docs`, `/docs`, y Redoc en `/redoc`
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));
app.use('/docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

// Endpoint `/redoc` con una interfaz simplificada para documentación
app.get('/redoc', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>ReDoc</title>
        <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
      </head>
      <body>
        <redoc spec-url="/openapi.json"></redoc>
      </body>
    </html>
  `);
});


app.get('/pelicula/:id',verifyJwt, async (req, res) => {
  const peliculaId = parseInt(req.params.id);  // Convertir el ID a un número entero
  try {
    logger.info(`Buscando película con ID: ${peliculaId}`);
    
    const result = await session.run(
      `MATCH (p:Película)
      WHERE id(p) = $id
      OPTIONAL MATCH (p)<-[:ACTUA]-(a:Actor)
      OPTIONAL MATCH (p)<-[:DIRIGE]-(d:Director)
      WITH p, 
           collect(DISTINCT a {nombre: a.nombre, foto: a.foto, id: toInteger(id(a))}) AS actores, 
           collect(DISTINCT d {nombre: d.nombre, foto: d.foto, id: toInteger(id(d))}) AS directores
      RETURN p {titulo: p.titulo, 
                año: p.año, 
                crítica: p.crítica, 
                sinopsis: p.sinopsis, 
                foto: p.foto, 
                actores: actores, 
                directores: directores} AS pelicula`,
      { id: peliculaId }
    );

    if (result.records.length === 0) {
      logger.warn(`Película no encontrada: ${peliculaId}`);
      return res.status(404).json({ error: 'Película no encontrada' });
    }

    // Obtener el primer resultado
    const pelicula = result.records[0].get('pelicula');
    res.json(pelicula);
  } catch (error) {
    logger.error(`Error al obtener la película: ${error.message}`);
    res.status(500).json({ error: 'Error al acceder a la base de datos' });
  }
});


app.get('/director/:id', verifyJwt,async (req, res) => {
  const directorId = parseInt(req.params.id);  // Convertir el ID a un número entero
  try {
    logger.info(`Buscando director con ID: ${directorId}`);
    const result = await session.run(
      `
      MATCH (d:Director)
      WHERE id(d) = $id
      OPTIONAL MATCH (d)-[:DIRIGE]->(p:Película)
      WITH d, 
           collect(DISTINCT {
               id: toInteger(id(p)), 
               titulo: p.titulo, 
               año: p.año, 
               crítica: p.crítica, 
               foto: p.foto
           }) AS peliculas
      RETURN {
          id: toInteger(id(d)),
          nombre: d.nombre,
          foto: d.foto,
          fecha_nacimiento: d.fecha_nacimiento,
          biografia: d.biografia,
          peliculas: peliculas
      } AS director
      `,
      { id: directorId }
    );

    if (result.records.length === 0) {
      logger.warn(`Director no encontrado: ${directorId}`);
      return res.status(404).json({ error: 'Director no encontrado' });
    }

    const director = result.records[0].get('director');
    res.json(director);
  } catch (error) {
    logger.error(`Error al obtener el director: ${error.message}`);
    res.status(500).json({ error: 'Error al acceder a la base de datos' });
  }
});

app.get('/actor/:id',verifyJwt, async (req, res) => {
  const actorId = parseInt(req.params.id); // Convertir el ID a un número entero
  try {
    logger.info(`Buscando actor con ID: ${actorId}`);
    const result = await session.run(
      `MATCH (a:Actor)
      WHERE id(a) = $id
      OPTIONAL MATCH (a)-[:ACTUA]->(p:Película)
      WITH a, 
           collect(DISTINCT p {titulo: p.titulo, año: p.año, crítica: p.crítica, foto: p.foto, id: toInteger(id(p))}) AS peliculas
      RETURN a {
               nombre: a.nombre,
               foto: a.foto,
               fecha_nacimiento: a.fecha_nacimiento,
               biografia: a.biografia,
               peliculas: peliculas
      } AS actor`,
      { id: actorId }
    );

    if (result.records.length === 0) {
      logger.warn(`Actor no encontrado: ${actorId}`);
      return res.status(404).json({ error: 'Actor no encontrado' });
    }

    const actor = result.records[0].get('actor');
    res.json(actor);
  } catch (error) {
    logger.error(`Error al obtener el actor: ${error.message}`);
    res.status(500).json({ error: 'Error al acceder a la base de datos' });
  }
});
app.get('/peliculas',verifyJwt, async (req, res) => {
  try {
    logger.info('Buscando todas las películas');

    const result = await session.run(
      `MATCH (p:Película)
      OPTIONAL MATCH (p)<-[:ACTUA]-(a:Actor)
      OPTIONAL MATCH (p)<-[:DIRIGE]-(d:Director)
      WITH DISTINCT p, 
           collect(DISTINCT a {nombre: a.nombre, foto: a.foto, id: toInteger(id(a))}) AS actores, 
           collect(DISTINCT d {nombre: d.nombre, foto: d.foto, id: toInteger(id(d))}) AS directores
      RETURN DISTINCT p {
               id: id(p),
               titulo: p.titulo,
               año: p.año,
               crítica: p.crítica,
               sinopsis: p.sinopsis,
               foto: p.foto,
               actores: actores,
               directores: directores
      } AS pelicula`
    );

    res.json(result.records.map(record => record.get('pelicula')));
  } catch (error) {
    logger.error('Error al buscar las películas:', error);
    res.status(500).send('Error al buscar las películas');
  }
});



app.get('/health', async (req, res) => {
  try {
    await session.run('RETURN 1');
    res.json({ status: 'healthy' });
  } catch (error) {
    logger.error(`Error en la comprobación de salud: ${error.message}`);
    res.status(500).json({ status: 'unhealthy', error: 'Error al conectar con la base de datos' });
  }
});

app.get('/openapi.json', (req, res) => {
  try {
    const openapiJson = yaml.parse(openapiFile);
    res.status(200).json(openapiJson);
  } catch (err) {
    logger.error(`Error al servir OpenAPI: ${err.message}`);
    res.status(500).json({ error: 'Error inesperado', detail: err.message });
  }
});

// Iniciar el servidor
app.listen(port, () => {
  logger.info(`Servidor ejecutándose en http://localhost:${port}`);
});
