# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
