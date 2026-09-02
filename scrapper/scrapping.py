import playwright
import argparse
import pathlib
import logging
import psycopg
import bs4
import sys
import os

# Resolver rutas
BASE_DIR = pathlib.Path(__file__).resolve().parent
LOG_FILE_PATH = BASE_DIR / "scrapper.log"

# Obtener argumentos
parser = argparse.ArgumentParser()
parser.add_argument(
   "-l", "--loglevel",
   help="el nivel del logging. Opciones: 'd':DEBUG, 'i':INFO, 'w':WARNING, 'e':ERROR",
   choices=['d', 'i', 'w', 'e'],
   default='i'
)
args = parser.parse_args()
letter_to_level = {
   'd' : logging.DEBUG,
   'i' : logging.INFO,
   'w' : logging.WARNING,
   'e' : logging.ERROR
}
LOGGING_LEVEL = letter_to_level[args.loglevel]

# Configurar logging
logging.basicConfig(
   filename=LOG_FILE_PATH,
   encoding='utf-8',
   level=LOGGING_LEVEL,
   filemode='w'
)
logger = logging.getLogger(__name__)

# Obtener variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")


### Funciones ###

# Probar conexion con postgres
def test_postgres_db():
   if not DATABASE_URL:
      logger.error("No se econtro la variable de entorno: DATABASE_URL")
      return False
   with psycopg.connect(DATABASE_URL):
      logger.info("Conexion con postgres: ok")
   return True


# Main
def main ():
   try:
      # Probar conexion a la base de datos
      if not test_postgres_db():
         logger.error("No se pudo conectar con la db.")
         sys.exit(2)
      # Extraer la fuente para scrapear TODO
      # Loop de scrapping
      #    - Abrir una instancia del navegador y conectar con la fuente
      #    - Hacer scroll al feed
      #    - Extraer los links individuales de las publicaciones
      #    - Extraer toda la informacion e imgs de cada publicacion
      #    - Procesar la multimedia recolectada
      #    - Insertar la informacion a la base de datos
      #    - Esperar un delay (si aplica), y repetir
      # Pasos finales del proceso de scrapping
   except Exception as e:
      logger.exception(e)
      sys.exit(1)
   finally:
      ...


# Zona de ejecucion
if __name__ == '__main__':
   main()
   sys.exit(0)