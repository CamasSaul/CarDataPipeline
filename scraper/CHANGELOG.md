# Changelog

Este es el historial de cambios al componente `scraper/`.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), y este proyecto se alinea al [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Se agregó un test en `cookies:test_cookies` para validar si las cookies guardadas son válidas y vigentes.
- Se automatizó la obtención de las cookies usando las credenciales de una cuenta de facebook registrada.
- Se agregó el módulo `cookies.py`.

## Removed

- Se eliminó el archivo `setup.py` debido a que quedó en desuso.


## [2.2.0] - 2026-09-13

### Added

- Se añadió una comprobación de inicio de sesión antes de scrapear cada ciclo.
- Se añadió funcionalidad al logging de `scraping.py`. Ahora tiene formatos mas detallados para el logfile y la salida de consola.

### Fixed

- Se corrigió una fuga de memoria en `scraper.py` relacionada con páginas abiertas sin cerrar después de una excepción.

### Changed

- Se modificaron los logs para ser más claros y específicos.
- Se agregó la instrucción para reiniciar el componente en caso de un error fatal.
- Se modificó el log para errores, ahora se guarda el traceback  completo.

### Removed

- Se eliminó el argumento --loglevel por completo, ya que estaba en desuso.


## [2.1.1] - 2026-09-12

### Fixed

- Se aumentó el número de scrolls por cilco de 60 a 100.
- Se agregaron palabras para remplazar en `scraper:clean_raw_text`.
- Se quitó un import en desuso.


## [2.1.0] - 2026-09-12

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


## [2.0.0] - 2026-09-11

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
