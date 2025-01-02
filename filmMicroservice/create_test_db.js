// Este script crea unos datos de prueba para la bdd de neo4j para que pueda probarse el microservicio y que la bdd no esté vacia

const neo4j = require('neo4j-driver');

// Configuración de la conexión a la base de datos
const driver = neo4j.driver(
    'bolt://neo4j:7687', // Cambiar localhost por el nombre del servicio de Neo4j
    neo4j.auth.basic('neo4j', 'neo4jpassword') // Reemplaza con tus credenciales
  );
const session = driver.session();

// Datos de prueba
const peliculas = [
  {
    titulo: 'Inception',
    año: 2010,
    crítica: 87,
    sinopsis: 'Un ladrón que roba secretos corporativos a través del uso de tecnología de sueño compartido es dado la tarea inversa de plantar una idea en la mente de un CEO.',
    foto: 'https://m.media-amazon.com/images/I/912AErFSBHL._AC_UF1000,1000_QL80_.jpg',
  },
  {
    titulo: 'The Dark Knight',
    año: 2008,
    crítica: 94,
    sinopsis: 'Cuando la amenaza conocida como el Joker emerge de su misterioso pasado, causa estragos y caos en el pueblo de Gotham.',
    foto: 'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_.jpg',
  },
];

const actores = [
  {
    nombre: 'Leonardo DiCaprio',
    foto: 'https://www.hola.com/horizon/square/9f8c5881e0c8-leonardo-dicaprio.jpg',
    fecha_nacimiento: '1974-11-11',
    biografia: 'Actor y productor estadounidense, conocido por sus papeles en Titanic e Inception.',
  },
  {
    nombre: 'Christian Bale',
    foto: 'https://upload.wikimedia.org/wikipedia/commons/0/0a/Christian_Bale-7837.jpg',
    fecha_nacimiento: '1974-01-30',
    biografia: 'Actor galés conocido por su transformación física en sus papeles y su trabajo en The Dark Knight.',
  },
];

const directores = [
  {
    nombre: 'Christopher Nolan',
    foto: 'https://cdn.hobbyconsolas.com/sites/navi.axelspringer.es/public/media/image/2023/07/christopher-nolan-3097196.jpg?tf=3840x',
    fecha_nacimiento: '1970-07-30',
    biografia: 'Director, guionista y productor británico-estadounidense, conocido por sus películas de ciencia ficción y thrillers.',
  },
];

const relacionesActuado = [
  { actor: 'Leonardo DiCaprio', pelicula: 'Inception' },
  { actor: 'Christian Bale', pelicula: 'The Dark Knight' },
];

const relacionesDirigido = [
  { director: 'Christopher Nolan', pelicula: 'Inception' },
  { director: 'Christopher Nolan', pelicula: 'The Dark Knight' },
];

async function crearDatos() {
  try {
    // Crear nodos de Película
    for (const pelicula of peliculas) {
      await session.run(
        `CREATE (p:Película {
          titulo: $titulo, 
          año: $año, 
          crítica: $crítica, 
          sinopsis: $sinopsis, 
          foto: $foto
        })`,
        pelicula
      );
    }

    // Crear nodos de Actor
    for (const actor of actores) {
      await session.run(
        `CREATE (a:Actor {
          nombre: $nombre, 
          foto: $foto, 
          fecha_nacimiento: $fecha_nacimiento, 
          biografia: $biografia
        })`,
        actor
      );
    }

    // Crear nodos de Director
    for (const director of directores) {
      await session.run(
        `CREATE (d:Director {
          nombre: $nombre, 
          foto: $foto, 
          fecha_nacimiento: $fecha_nacimiento, 
          biografia: $biografia
        })`,
        director
      );
    }

    // Crear relaciones ACTUA
    for (const relacion of relacionesActuado) {
      await session.run(
        `MATCH (a:Actor {nombre: $actor}), (p:Película {titulo: $pelicula})
         CREATE (a)-[:ACTUA]->(p)`,
        relacion
      );
    }

    // Crear relaciones DIRIGE
    for (const relacion of relacionesDirigido) {
      await session.run(
        `MATCH (d:Director {nombre: $director}), (p:Película {titulo: $pelicula})
         CREATE (d)-[:DIRIGE]->(p)`,
        relacion
      );
    }

    console.log('Datos creados exitosamente.');
  } catch (error) {
    console.error('Error al crear los datos:', error);
  } finally {
    // Cerrar la sesión y el driver
    await session.close();
    await driver.close();
  }
}

// Ejecutar la función para crear los datos
crearDatos();
