# READ HERE.
# TODO


# Library imports
import argparse
import asyncio
import pathlib
import logging
import psycopg
import sys
import os

# Local modules imports
from scraper import scraper_cicle

# Typing imports
from typing import Any


# Resolver rutas
BASE_DIR = pathlib.Path(__file__).resolve().parent
LOG_FILE_PATH = BASE_DIR / "scraper.log"

# Obtener argumentos
parser = argparse.ArgumentParser()
parser.add_argument(
   "-l", "--loglevel",
   help="el nivel del logging. Opciones: 'd':DEBUG, 'i':INFO, 'w':WARNING, 'e':ERROR",
   choices=['d', 'i', 'w', 'e'],
   default='i'
)
parser.add_argument(
   "-d", "--debug",
   action="store_true",
   help="inicia el proceso en modo debug."
)
args = parser.parse_args()
letter_to_level = {
   'd' : logging.DEBUG,
   'i' : logging.INFO,
   'w' : logging.WARNING,
   'e' : logging.ERROR
}
letter = args.loglevel
if args.debug:
   letter = 'd'
LOGGING_LEVEL = letter_to_level[letter]

# Configurar logging
logging.basicConfig(
   filename=LOG_FILE_PATH,
   encoding='utf-8',
   level=LOGGING_LEVEL,
   filemode='w'
)
logger = logging.getLogger(__name__)

# Obtener variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", default="")
if not DATABASE_URL:
   logger.error("No se econtro la variable de entorno: DATABASE_URL")
   sys.exit(2)

### Funciones ###

# Probar conexion con postgres
def test_postgres_db() -> bool:
   with psycopg.connect(DATABASE_URL):
      logger.info("Conexion con postgres: ok")
   return True


# Obtener los web_sources de la base de datos
def get_web_sources() -> list[dict[str, Any]]:
   with psycopg.connect(DATABASE_URL) as conn:
      cur = conn.execute("SELECT * FROM web_sources;")
      sources = cur.fetchall()
   return [
      {"id": source[0],
      "url": source[1],
      "title": source[2]}
      for source in sources
   ]


# Insertar los datos de un cilco de scraping a la base de datos
def insert_raw_posts_to_db(raw_posts:list[tuple[Any]]) -> None:
   for raw_post in raw_posts:
      with psycopg.connect(DATABASE_URL) as conn:
         conn.execute(
            "INSERT INTO raw_posts (" \
            "id_web_src," \
            "post_link," \
            "raw_text," \
            "VALUES (?,?,?)",
            raw_post
         )


# Main
async def main():
   try:
      # Probar conexion a la base de datos
      if not test_postgres_db():
         logger.error("No se pudo conectar con la db.")
         sys.exit(2)
      # Extraer la fuente para scrapear
      sources = get_web_sources()
      # Consumir el generador asincrono del modulo scraper.py
      logger.
      # async for raw_posts, raw_imgs in scraper_cicle(sources):
      #    # Insertar los datos extraidos a la db
      #    logger.debug(f'{len(raw_posts)} posts scrapeados.')
      #    # TODO insert_raw_posts_to_db(raw_posts)
      #    # Procesar las imagenes extraidas (comprimir, seleccionar)
      #    # TODO process_raw_imgs(raw_imgs)
      #    # Insertar imagenes procesadas a la db
      #    # TODO insert_imgs_to_db
      #    # TODO Esperar un delay
      # Pasos finales del proceso de scraping
   except KeyboardInterrupt:
      logger.warning("Proceso detenido por el usuario.")
   except Exception as e:
      logger.exception(e)
      sys.exit(1)
   finally:
      logger.info("Terminando proceso.")


# Zona de ejecucion
if __name__ == '__main__':
   asyncio.run(main())
   sys.exit(0)