import threading
import logging
import pathlib
import asyncio
import time
import bs4
import re
import os
from playwright.async_api import async_playwright

# Typing imports
from typing import Any


# Resolver rutas
BASE_DIR = pathlib.Path(__file__).resolve().parent
LOG_FILE_PATH = BASE_DIR / "scraper.log"

# Variables de configuracion
COOKIES_FILE_PATH = BASE_DIR / "secrets/cookies.json"
SCROLLS_PER_PAGE = 10
if not os.path.exists(COOKIES_FILE_PATH):
   get_cookies()


# Obtener logger
logger = logging.getLogger(__name__)


async def get_cookies() -> bool:
   input("Se necesitan cookies para iniciar el proceso de scraper." \
   "Inicie sesión por única vez para establecer la configuración." \
   "A continuación se abrirá un navegador dónde tendrá que iniciar sesión en el portal de facebook y resolver el captcha." \
   "Presione enter para continuar...")
   engine = await async_playwright().start()
   navigator = getattr(engine, "firefox")
   browser = await navigator.launch(headless=False)
   context = await browser.new_context(storage_state=COOKIES_FILE_PATH, locale="es_LA")
   return True


async def scrap_page(context, link:str):
   page = await context.new_page()
   await page.goto("https://facebook.com/" + link, wait_until='domcontentloaded')
   html = await page.content()
   soup = bs4.BeautifulSoup(html, "lxml")
   logger.debug("Text: " + " ".join(soup.get_text().replace('\n', ' ').split()))
   page.close()
   return link


async def scraper_cicle(sources:list[dict[str, Any]]):
   # Abrir una instancia del navegador y conectar con la fuente
   engine = await async_playwright().start()
   navigator = getattr(engine, "firefox")
   browser = await navigator.launch(headless=True)
   # Usamos cookies como contexto para cargar las paginas
   context = await browser.new_context(storage_state=COOKIES_FILE_PATH, locale="es_LA")
   # TODO comenta esta linea
   while True:
      # El proceso re repite para cada web_source
      for source in sources:
         logger.debug(f"Fuente de scraping: {source}")
         # Creamos la pagina y entramos al web_source
         page = await context.new_page()
         await page.goto(source["url"], wait_until='domcontentloaded')
         # Hacemos un scroll 'natural' al feed
         # por cada paso extraemos las publicaciones
         items_links:set[str] = set()
         for _ in range(SCROLLS_PER_PAGE):
            logger.debug(f"Scraping scroll ({_}/{SCROLLS_PER_PAGE}))")
            for _ in range(5):
               await page.mouse.wheel(0, 180)
               await asyncio.sleep(0.1)
            # Extraemos el contenido del feed
            html = await page.content()
            soup = bs4.BeautifulSoup(html, "lxml")
            feed = soup.find("div", attrs={"role": "feed"})
            # Extraemos los links de cada publicacion del feed
            posts = feed.find_all("div", attrs={"aria-posinset": True})
            # Por cada publicacion buscamos el link al item del marketplace,
            # siempre comienza con "/commerce/listing/"
            lil = len(items_links)
            for post in posts:
               anchor = post.find('a', attrs={"href": re.compile(r"^/commerce/listing/")})
               if anchor:
                  items_links.add(anchor["href"])
            logger.debug(f"{(len(items_links) - lil)} links extraidos.")
         # Ahora lanzamos un grupo de tareas para scrapear cada link al mismo tiempo
         # el proceso se hace en grupos de 10 tasks
         items_links = list(items_links)
         results = []
         for _ in range(int(len(items_links) / 10) + 1):
            async with asyncio.TaskGroup() as tg:
               tasks = []
               for link in items_links[:10]:
                  task = tg.create_task(scrap_page(context, link))
                  tasks.append(task)
                  items_links.remove(link)
            results.extend([task.result for task in tasks])
         await page.close()
         # Retornamos los datos extraidos
         yield results, []