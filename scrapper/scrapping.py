import argparse
import asyncio
import pathlib
import logging
import psycopg
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


def get_web_sources() -> dict[int, tuple[str]]:
   with psycopg.connect(DATABASE_URL) as conn:
      cur = conn.execute("SELECT * FROM web_sources;")
      sources = cur.fetchall()
   return {
      source[0]: source[1:]
      for source in sources
   }


# Main
def main():
   try:
      # Probar conexion a la base de datos
      if not test_postgres_db():
         logger.error("No se pudo conectar con la db.")
         sys.exit(2)
      # Extraer la fuente para scrapear
      logger.debug("Web sources %s", get_web_sources())
      # sources = getSources()
      # scrapper = Scrapper(sources)
      # while True:
      #    data = asyncio.run(scrapper.cicle())
      #    insertDataToDB(data)
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