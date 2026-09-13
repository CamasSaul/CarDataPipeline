# Changelog

Este es el historial de cambios al componente scraper.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), y este proyecto se alinea al [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



## [2.1.1]

### Fixed

- Se aumentó el número de scrolls por cilco de 60 a 100.
- Se agregaron palabras para remplazar en `scraper:clean_raw_text`.
- Se quitó un import en desuso.


## [2.1.0]

### Added

- Se añadio una funcion `scraper:click_buttons`. Para modularizar.
- Se añadieron más de 100 registros web_source al `init.sql`.
- Sea añadió el campo `hash` a la tabla `raw_posts` para tener un identificador único y no repetir registros.

### Changed

- Textos extraidos de publicaciones que no se hayan expandido o que estén traducidas automáticamente, son descartados.

### Fixed

- Se corrigió problemas con el tamaño de `raw_text`.
- Se corrigió la forma en que se presionan los botones del feed.
- Se corrigió el origen de textos no expandidos en `scraper.py`.

### Removed

- Se eliminó la instrucción UNIQUE del campo `raw_text`, ya que limitaba el tamaño máximo de un texto extraído.


## [2.0.0]

### Added

- Se agrego el archivo `CHANGELOG.md` a los componente `app` y `scraper`.
- Se agregó un `StreamHandler` al logging de `scraping.py`.
- Se agregó la función `scraper:clean_raw_text`.

### Fixed

- Se corrigió el bloqueo de las fuentes de `facebook.com` mediante una modificación en el algoritmo de scraping.

### Changed

- Se actualizó el módulo `scraper.py`.
- Se actualizó el módulo `scraping.py`, para soportar la nueva estructura de la base de datos.

### Removed

- Se eliminaron las columnas `link_profile` y `trim` de la tabla `cars` en `sql/init.sql`, ya que el proceso de scraping no las soporta.
- Se eliminó la columna `profile_link` de la tabla `raw_posts`, ya que está en desuso.
- Se eliminó por completo la tabla `raw_imgs`, ya que el proyecto no dará soporte a esta funcionalidad a corto o mediano plazo.
- Se eliminó la función `scraper:scrap_page`.
