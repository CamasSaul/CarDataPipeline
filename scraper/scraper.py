import logging
import pathlib
import asyncio
import bs4
import sys
import re
import os
from playwright.async_api import async_playwright, TimeoutError

# Typing imports
from typing import Any


# Obtener logger
logger = logging.getLogger(__name__)

# Resolver rutas
BASE_DIR = pathlib.Path(__file__).resolve().parent
LOG_FILE_PATH = BASE_DIR / "scraper.log"

# Variables de configuracion
COOKIES_FILE_PATH = BASE_DIR / "secrets/cookies.json"
SCROLLS_PER_PAGE = 50
if not os.path.exists(COOKIES_FILE_PATH):
   logger.fatal("No hay cookies para el proceso de scraping.")
   sys.exit(3)


async def scrap_page(context, link:str):
   page = await context.new_page()
   await page.goto("https://facebook.com/" + link + "?locale=es_LA", wait_until='load')
   try:
      await page.get_by_role("button", name="See more").click()
   except:
      pass
   html = await page.content()
   await page.close()
   soup = bs4.BeautifulSoup(html, "lxml")
   text = " ".join(soup.get_text().replace('\n', ' ').split())
   return link, text


async def scraper_cicle(sources:list[dict[str, Any]]):
   # Abrir una instancia del navegador y conectar con la fuente
   engine = await async_playwright().start()
   navigator = getattr(engine, "firefox")
   browser = await navigator.launch(headless=True)
   # Usamos cookies como contexto para cargar las paginas
   context = await browser.new_context(locale="es_LA")
   await context.set_storage_state(COOKIES_FILE_PATH)
   # TODO comenta esta linea
   while True:
      try:
         # El proceso re repite para cada web_source
         for source in sources:
            logger.debug(f"Fuente de scraping: {source}")
            # Creamos la pagina y entramos al web_source
            page = await context.new_page()
            await page.goto(source["url"], wait_until='load')
            # Hacemos un scroll 'natural' al feed
            # por cada paso extraemos las publicaciones
            items_links:set[str] = set()
            for _ in range(SCROLLS_PER_PAGE):
               logger.debug(f"Scraping scroll ({_+1}/{SCROLLS_PER_PAGE})")
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
               for post in posts:
                  anchor = post.find('a', attrs={"href": re.compile(r"^/commerce/listing/")})
                  if anchor:
                     items_links.add(anchor["href"].split('?')[0])
               logger.debug(f"{len(items_links)} links extraidos.")
            await page.close()
            # Ahora lanzamos un grupo de tareas para scrapear cada link al mismo tiempo
            # el proceso se hace en grupos de 10 tasks
            items_links = list(items_links)
            results = []
            for i in range(0, len(items_links), 10):
               batch = items_links[i:i + 10]
               async with asyncio.TaskGroup() as tg:
                  tasks = [
                        tg.create_task(scrap_page(context, link))
                        for link in batch
                  ]
               for task in tasks:
                  results.append(task.result())
            # Retornamos los datos extraidos
            yield results, [], source["id"]
      except TimeoutError as e:
         logger.warning(f"TimeoutError catched: {e.__traceback__}")
         pass