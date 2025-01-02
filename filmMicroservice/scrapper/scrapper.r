library(rvest)
library(jsonlite)

scrape_imdb_top_250 <- function() {
  url <- "https://www.imdb.com/chart/top/"
  page <- read_html(url)

  # Extraer títulos, años y puntuaciones
  titles <- page %>% html_nodes(".titleColumn a") %>% html_text()
  years <- page %>% html_nodes(".titleColumn span") %>% html_text() %>% gsub("\\(|\\)", "", .)
  ratings <- page %>% html_nodes(".imdbRating strong") %>% html_text()

  # Aquí puedes añadir scraping adicional para actores, directores, fotos, y sinopsis.
  # Por simplicidad, se asignarán valores de ejemplo para estos campos.
  
  movies <- data.frame(
    title = titles,
    year = years,
    rating = ratings,
    synopsis = "Sinopsis de ejemplo",
    photo_url = "https://via.placeholder.com/150",
    actors = I(list(list(
      list(name = "Actor 1", photo_url = "https://via.placeholder.com/150", birth_date = "01-01-1980", biography = "Biografía del actor 1"),
      list(name = "Actor 2", photo_url = "https://via.placeholder.com/150", birth_date = "02-02-1985", biography = "Biografía del actor 2")
    ))),
    director = I(list(list(
      name = "Director Ejemplo",
      photo_url = "https://via.placeholder.com/150",
      birth_date = "01-01-1970",
      biography = "Biografía del director"
    )))
  )

  return(toJSON(movies, pretty = TRUE))
}

# Ejecutar la función y devolver la salida
cat(scrape_imdb_top_250())
