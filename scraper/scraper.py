import logging
import pathlib
import asyncio
import bs4
import sys
import re
import os
from difflib import SequenceMatcher
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

# Obtener logger
logger = logging.getLogger(__name__)

# Resolver rutas
BASE_DIR = pathlib.Path(__file__).resolve().parent
LOG_FILE_PATH = BASE_DIR / "scraper.log"

# Variables de configuracion
COOKIES_FILE_PATH = BASE_DIR / "secrets/cookies.json"
SCROLLS_PER_WEB_SOURCE = 60
if not os.path.exists(COOKIES_FILE_PATH):
   logger.fatal("No hay cookies para el proceso de scraping.")
   sys.exit(3)


def clean_raw_text(text):
   text = text.replace("Facebook", " ")
   text = text.replace("facebook", " ")
   text = text.replace("Shared with Public group", " ")
   text = text.replace("See translation", " ")
   text = text.replace("See less", " ")
   text = text.replace("Hide original", " ")
   text = text.replace("Submit your first comment…", " ")
   text = text.replace("See translation", " ")
   text = text.replace("Rate this translation", " ")
   text = text.replace("Write a public comment", " ")
   text = text.replace("Message", " ")
   text = text.replace("responsive", " ")
   return " ".join(text.replace('\n', ' ').split())


async def click_buttons(page, name):
   buttons = page.get_by_role("button", name=name)
   count = await buttons.count()
   clicked = 0
   for i in range(count - 1, -1, -1):
      button = buttons.nth(i)
      try:
         if not await button.is_visible():
            continue
         await button.click(timeout=1500)
         clicked += 1
         # Pausa para permitir que cambie el DOM
         await asyncio.sleep(0.05)
      except PlaywrightTimeoutError:
         logger.debug(
            f"No se pudo presionar btn: {name}"
         )
      except Exception as e:
         logger.debug(
            f"Error presionando btn {name}: {e}"
         )
   return clicked



async def scraper_cicle(sources:list[dict]):
   # Abrir una instancia del navegador y conectar con la fuente
   engine = await async_playwright().start()
   navigator = getattr(engine, "firefox")
   browser = await navigator.launch(headless=True)
   # Usamos cookies como contexto para cargar las paginas
   context = await browser.new_context()
   await context.set_storage_state(COOKIES_FILE_PATH)
   # Este es el bucle generador
   while True:
      # Cada ciclo es una fuente scrapeada
      for source in sources:
         try:
            # Creamos la ventana y entramos al url
            logger.debug(f"Fuente de scraping: {source}")
            page = await context.new_page()
            await page.goto(source["url"], wait_until='load')
            # Hacemos un scroll 'natural' al feed para recolectar los posts
            for _ in range(SCROLLS_PER_WEB_SOURCE):
               # Scroll
               logger.debug(f"Scraping scroll ({_+1}/{SCROLLS_PER_WEB_SOURCE})")
               for _ in range(5):
                  await page.mouse.wheel(0, 180)
                  await asyncio.sleep(0.1)
               # Presionar el boton See more mientras se hace scroll al feed
               see_more_clicked = await click_buttons(page, "See more")
               if see_more_clicked:
                  logger.debug(
                     f"See more presionados: "
                     f"{see_more_clicked}"
                  )
               see_original_clicked = await click_buttons(page, "See original")
               if see_original_clicked:
                  logger.debug(
                     f"See original presionados: "
                     f"{see_original_clicked}"
                  )
            # Extraemos el html de tood el feed cargado
            html = await page.content()
            soup = bs4.BeautifulSoup(html, "lxml")
            feed = soup.find("div", attrs={"role": "feed"})
            # Extraemos las publicaciones individuales del feed
            posts = feed.find_all("div", attrs={"aria-posinset": True})
            # Recolectamos los textos de cada post y despues de un
            # proceso para evitar duplicados, los retornamos con yield
            results = set() # Este set contiene los datos scrapeados
            for post in posts:
               # Obtener unicamente el texto del html del post
               raw_text = post.get_text()
               # Limpiamos de caracteres/palabras inutiles
               raw_text = clean_raw_text(raw_text)
               # Validamos el texto
               if len(raw_text) < 30:
                  logger.debug("Omited cause empty")
                  continue
               if "See more" in raw_text:
                  logger.debug("Omited cause See more appears")
                  continue
               if "See original" in raw_text:
                  logger.debug("Omited cause See original appears")
                  continue
               if not results:
                  results.add(raw_text)
               # Omitimos los textos que tengan un 80% de similitud
               # con los textos ya guardados
               omit = False
               for r in results:
                  if SequenceMatcher(
                     None,
                     r,
                     raw_text
                  ).ratio() > .8:
                     # Si encontramos dos textos similares, conservamos 
                     # el que contenga mas carateres
                     if len(r) >= len(raw_text):
                        omit = True
                        break
                     else:
                        results.remove(r)
                        results.add(raw_text)
                     break
               # Gaurdamos el texto si paso la prueba de similitud
               if not omit:
                  results.add(raw_text)
            # Cerramos el ciclo y retornamos los datos
            await page.close()
            yield results, source["id"]
         except Exception as e:
            logger.warning(f'Error capturado durante el ciclo. {e}')
            yield [], 0