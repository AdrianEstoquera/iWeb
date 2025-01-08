#install.packages("neo4r")
#install.packages("tidyverse")
#install.packages("rvest")
#install.packages("polite")
#install.packages("promises")
library(tidyverse) # Para manipular datos
library(rvest)     # Permite realizar web scraping
library(polite)    # Verificación de robots.txt para web scraping
library(neo4r)


clean_text <- function(input_text) {
  # Remover números y puntos
  trimws(gsub("[0-9.]", "", input_text))
}

# Función para scrapear la página principal del top 250 de IMDb
scrape_imdb_top_250 <- function() {
  url <- "https://www.imdb.com/chart/top/"
  cat("Scrapping", url, "\n")
  page <- read_html(url) 
  Sys.sleep(1) 
  page <- html_element(page,"body")
  
  # Extraer títulos
  titles <- page %>% 
    html_elements("a.ipc-title-link-wrapper") %>% 
    html_element("h3.ipc-title__text") %>%
    html_text() %>% 
    clean_text()
  
  
  cat(length(titles), "titles found!\n")
  
  # URL de las películas
  link_to_film_page <- page %>% 
    html_elements("a.ipc-title-link-wrapper") %>% 
    html_attr("href")
  film_url <- paste0("https://www.imdb.com/es", link_to_film_page)
  
  
  # Año de la película
  years <- page %>%
    html_elements("div.cli-title-metadata") %>%
    html_elements("span") %>%
    html_text()
  years <- years[seq(1, length(years), by = 3)]
  
  # Ratings de las películas
  ratings <- page %>%
    html_elements("span.ipc-rating-star--rating") %>%
    html_text()
  
  # Inicializar listas para almacenar datos adicionales
  resumen <- vector("list", length(titles))
  all_photos <- vector("list", length(titles))
  all_relaciones_actuar <- list()
  all_relaciones_dirigir <- list()
  actors_to_process <- list()
  directors_to_process <- list()
  
  for (i in seq_along(film_url)) {
    film_details <- scrappe_film(film_url[i], titles[i])
    
    resumen[[i]] <- film_details$rating
    all_photos[[i]] <- film_details$photo_url
    
    actors_to_process <- unique(c(actors_to_process, film_details$actors_to_process))
    directors_to_process <- unique(c(directors_to_process, film_details$directors_to_process))
    
    all_relaciones_actuar <- c(all_relaciones_actuar, film_details$relacion_actuado)
    all_relaciones_dirigir <- c(all_relaciones_dirigir, film_details$relacion_dirigido)
  }
  
  # Scrapeo de actores
  scrapped_actors <- lapply(actors_to_process, scrappe_person)
  
  # Scrapeo de directores
  scrapped_directors <- lapply(directors_to_process, scrappe_person)
  
  # Crear data frame de películas
  movies <- tibble(
    titles = titles,
    years = years,
    ratings = ratings,
    resumenes = resumen,
    photos = all_photos
  )
  
  return(list(
    movies = movies,
    actors = scrapped_actors,
    directors = scrapped_directors,
    relaciones_actuar = all_relaciones_actuar,
    relaciones_dirigir = all_relaciones_dirigir
  ))
}

# Función para scrapear detalles de una película individual
scrappe_film <- function(url, titulo) {
  cat("Inspecting", titulo, "\n")
  
  page <- read_html(url) %>% html_element("body")
  
  # Extraer el rating de la película
  rating <- page %>%
    html_element("span.sc-3ac15c8d-1.gkeSEi") %>%
    html_text()
  
  # Obtener la foto de la película
  photo_container_url <- page %>%
    html_element("a.ipc-lockup-overlay") %>%
    html_attr("href") %>%
    paste0("https://www.imdb.com", .)
  
  photo_url <- scrappe_img(photo_container_url)
  
  # Obtener los actores
  actors_to_process <- page %>%
    html_elements("a.sc-cd7dc4b7-1") %>% #
    html_attr("href") %>%
    paste0("https://www.imdb.com", .)
  actors_name <- page %>%
    html_elements("a.sc-cd7dc4b7-1") %>% # 
    html_text()
  
  relacion_actuado <- lapply(actors_name, function(actor_n) list(actor_n, titulo))
  
  # Obtener los directores
  directors_to_process <- page %>%
    html_element("a.ipc-metadata-list-item__list-content-item") %>%
    html_attr("href") %>%
    paste0("https://www.imdb.com", .)
  directors_name <- page %>%
    html_element("a.ipc-metadata-list-item__list-content-item") %>%
    html_text()
  
  relacion_dirigido <- lapply(directors_name, function(director_n) list(director_n, titulo))
  
  return(list(
    rating = rating,
    photo_url = photo_url,
    actors_to_process = actors_to_process,
    directors_to_process = directors_to_process,
    relacion_actuado = relacion_actuado,
    relacion_dirigido = relacion_dirigido
  ))
}

scrappe_img <- function(url){
  cat(" · Inspecting", url, "\n")
  page <- read_html(url) %>% html_element("body")
  photo_url <- page %>%
    html_elements("img.sc-7c0a9e7c-0.ekJWmC") %>%
    html_attr("src")
  photo_url <- photo_url[1]
  cat(" · Img URL:", photo_url, "\n")
  return(photo_url)
}

# Función para scrapear detalles de una persona (actor o director)
scrappe_person <- function(url) {
  cat("Inspecting", url, "\n")
  
  page <- read_html(url) %>% html_element("body")
  
  name <- page %>%
    html_element("span.hero__primary-text") %>%
    html_text()
  cat(" · Name:", name, "\n")
  
  photo_container_url <- page %>%
    html_element("a.ipc-lockup-overlay") %>%
    html_attr("href") %>%
    paste0("https://www.imdb.com", .)
  photo <- scrappe_img(photo_container_url)
  
  birth_date <- page %>%
    html_elements("span.sc-59a43f1c-2") %>%
    html_text()
  birth_date <- birth_date[2]
  cat(" · Birth date:", birth_date, "\n")
  
  bio <- page %>%
    html_element("div.ipc-html-content-inner-div") %>%
    html_text()
  
  return(list(name = name, photo = photo, birth_date = birth_date, bio = bio))
}

# Ejecutar la función y devolver la salida
result <- scrape_imdb_top_250()
movies <- result$movies
actors <- result$actors
directors <- result$directors
relaciones_actuar <- result$relaciones_actuar
relaciones_dirigir <- result$relaciones_dirigir


########################### NEO4R ########################### 


# Configura la conexión a Neo4j
neo4j_con <- neo4r::neo4j_api$new(
  url = "http://localhost:7474",  # Usar el protocolo HTTP para `neo4r`
  user = "neo4j", 
  password = "neo4jpassword"
)

# Comprueba la conexión con Neo4j
neo4j_con$ping()

# Iterar sobre las películas y agregarlas a la base de datos
for (i in 1:nrow(movies)) {
  # Crear la consulta Cypher para cada película
  movie_query <- sprintf(
    "MERGE (m:Película {titulo: '%s', año: '%s', critica: '%s', sinopsis: '%s', foto: '%s'});",
    movies$titles[i],
    movies$years[i],
    movies$ratings[i],
    movies$resumenes[[i]],
    movies$photos[[i]]
  )
  
  # Ejecutar la consulta en Neo4j
  movie_query %>% call_neo4j(con=neo4j_con)
}
for(actor in actors){
  query <- sprintf(
    "MERGE (a:Actor {nombre: '%s', foto: '%s', fecha_nacimiento: '%s', biografia: '%s'});",
    actor$name,
    actor$photo,
    actor$birth_date,
    actor$bio
  )
  
  # Ejecutar la consulta en Neo4j
  query %>% call_neo4j(con=neo4j_con)
}

for(director in directors){
  query <- sprintf(
    "MERGE (d:Director {nombre: '%s', foto: '%s', fecha_nacimiento: '%s', biografia: '%s'});",
    director$name,
    director$photo,
    director$birth_date,
    director$bio
  )
  
  # Ejecutar la consulta en Neo4j
  query %>% call_neo4j(con=neo4j_con)
}
# Relacion ACTUA
for(relation in relaciones_actuar){
  actor <- relation[[1]]
  movie <- relation[[2]]
  
  query <- sprintf(
    "MATCH (a:Actor {nombre: '%s'}), (m:Película {titulo: '%s'}) 
     MERGE (a)-[:ACTUA]->(m);",
    actor, movie
  )
  tryCatch({
    # Ejecutar la consulta en Neo4j
    query %>% call_neo4j(con = neo4j_con)
  }, error = function(e) {
    cat("Error en la relación entre actor y película:", actor, "y", movie, "\n")
    cat("Detalles del error:", e$message, "\n")
  })
  
}
# Relacion DIRIGE
for(relation in relaciones_dirigir){
  director <- relation[[1]]
  movie <- relation[[2]]
  
  query <- sprintf(
    "MATCH (a:Director {nombre: '%s'}), (m:Película {titulo: '%s'}) 
     MERGE (a)-[:DIRIGE]->(m);",
    director, movie
  )
  tryCatch({
    # Ejecutar la consulta en Neo4j
    query %>% call_neo4j(con = neo4j_con)
  }, error = function(e) {
    cat("Error en la relación entre actor y película:", actor, "y", movie, "\n")
    cat("Detalles del error:", e$message, "\n")
  })
  
}

neo4j_con <- NULL


