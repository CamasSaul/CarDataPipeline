# Library imports
import argparse
import asyncio
import pathlib
import logging
import psycopg
import hashlib
import csv
import sys
import os
from datetime import datetime

# modules imports
from scraper import scraper_cicle

# Resolver rutas
BASE_DIR = pathlib.Path(__file__).resolve().parent
LOG_FILE_PATH = BASE_DIR / "scraper.log"
METRICS_FILE_PATH = BASE_DIR / "metrics.csv"

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
   level=LOGGING_LEVEL,
   handlers=[
      logging.FileHandler(LOG_FILE_PATH, mode='w', encoding='utf-8'),
      logging.StreamHandler()
   ]
)
logger = logging.getLogger(__name__)

# Obtener variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", default="")
if not DATABASE_URL:
   logger.error("No se econtro la variable de entorno: DATABASE_URL")
   sys.exit(2)

### Variables de metrica ###
init_timestamp = datetime.now().timestamp()
metric_report = {
   "iteration_datetime": datetime.now().isoformat(),
   "total_web_sources_scraped": 0,
   "total_scraped_posts": 0,
   "total_new_rows": 0,
   "total_repeated_rows": 0,
   "total_cicles": 0,
   "total_spend_time_seconds": 0
}

# Probar conexion con postgres
def test_postgres_db() -> bool:
   with psycopg.connect(DATABASE_URL):
      logger.info("Conexion con postgres: ok")
   return True


# Obtener los web_sources de la base de datos
def get_web_sources() -> list[dict[str]]:
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
def insert_raw_posts_to_db(raw_posts:list) -> None:
   for raw_post in raw_posts:
      with psycopg.connect(DATABASE_URL) as conn:
         try:      
            conn.execute(
               "INSERT INTO raw_posts (" \
               "id_web_src," \
               "raw_text," \
               "hash," \
               "timestamp," \
               "process_status)" \
               " VALUES (%s,%s,%s,%s,%s)",
               raw_post
            )
            metric_report["total_new_rows"] += 1
         except psycopg.errors.UniqueViolation:
            logger.debug("UniqueViolation exception catched.")
            metric_report["total_repeated_rows"] += 1


# Main
async def main():
   try:
      # Probar conexion a la base de datos
      if not test_postgres_db():
         logger.error("No se pudo conectar con la db.")
         sys.exit(2)
      # Extraer la fuente para scrapear
      sources = get_web_sources()
      logger.info(f"Se obtuvieron {len(sources)} web sources para scrapear.")
      metric_report["total_web_sources_scraped"] = len(sources)
      # Consumir el generador asincrono del modulo scraper.py
      logger.info("Iniciando proceso de scrapping.")
      logger.info(f"Iniciando nuevo ciclo. {metric_report['total_cicles']} ciclos completados.")
      async for raw_texts, id_web_source in scraper_cicle(sources):
         # Insertar los datos extraidos a la db
         if raw_texts:
            raw_posts = [(
               id_web_source,
               raw_text,
               hashlib.sha256(raw_text.encode("utf-8")).hexdigest(),
               datetime.now().isoformat(),
               "pending")
               for raw_text in raw_texts
            ]
            insert_raw_posts_to_db(raw_posts)
         metric_report["total_scraped_posts"] += len(raw_texts)
         metric_report["total_cicles"] += 1
         logger.info(f"Ciclo completado. {len(raw_texts)} registros scrapeados.")
         logger.info(f"Total ciclos completados desde la ejecucion: {metric_report['total_cicles']}")
         logger.info(f"Tiempo total desde la ejecucion: {datetime.now().timestamp() - init_timestamp}s")
   except KeyboardInterrupt:
      logger.warning("Proceso detenido por el usuario.")
   except Exception as e:
      logger.exception(e)
      sys.exit(1)
   finally:
      # Guardar metric report
      logger.info("Terminando proceso.")
      logger.info("Guardando reporte de metricas.")
      metric_report["total_spend_time_seconds"] = datetime.now().timestamp() - init_timestamp
      file_exists = os.path.exists(METRICS_FILE_PATH)
      with open(METRICS_FILE_PATH, 'a', encoding='utf-8') as f:
         w = csv.DictWriter(f, fieldnames=metric_report.keys())
         if not file_exists:
            w.writeheader()
         w.writerow(metric_report)


# Zona de ejecucion
if __name__ == '__main__':
   asyncio.run(main())
   sys.exit(0)