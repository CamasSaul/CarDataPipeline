import threading
import logging
import pathlib
import asyncio
import time
import bs4
import re
from playwright.async_api import async_playwright

# Typing imports
from typing import Any


# Resolver rutas
BASE_DIR = pathlib.Path(__file__).resolve().parent
LOG_FILE_PATH = BASE_DIR / "scrapper.log"

# Variables de configuracion
COOKIES_FILE_PATH = BASE_DIR / "cookies.json"
SCROLLS_PER_PAGE = 10


# Obtener logger
logger = logging.getLogger(__name__)


async def scrap_page(link:str):
   return link


async def scrapper_cicle(sources:list[dict[str, Any]]):
   # Abrir una instancia del navegador y conectar con la fuente
   engine = await async_playwright().start()
   navigator = getattr(engine, "firefox")
   browser = await navigator.launch(headless=False)
   # Usamos cookies como contexto para cargar las paginas
   context = await browser.new_context(storage_state=COOKIES_FILE_PATH, locale="es_LA")
   # TODO comenta esta linea
   while True:
      # El proceso re repite para cada web_source
      for source in sources:
         # Creamos la pagina y entramos al web_source
         page = await context.new_page()
         await page.goto(source["url"], wait_until='domcontentloaded')
         # Hacemos un scroll 'natural' al feed
         for _ in range(SCROLLS_PER_PAGE):
            await page.mouse.wheel(0, 100)
            await asyncio.sleep(0.1)
         # Extraemos el contenido del feed
         html = await page.content()
         soup = bs4.BeautifulSoup(html, "lxml")
         feed = soup.find("div", attrs={"role": "feed"})
         # Extraemos los links de cada publicacion del feed
         posts = feed.find_all("div", class_="html-div")
         # Por cada publicacion buscamos el link al item del marketplace,
         # siempre comienza con "/commerce/listing/"
         items_links:set[str] = set()
         for post in posts:
            anchors = post.find_all('a', attrs={"href": re.compile(r"^/commerce/listing/")})
            if anchors:
               items_links.update(anchors[0]["href"])
         # Ahora lanzamos un grupo de tareas para scrapear cada link al mismo tiempo
         async with asyncio.TaskGroup() as tg:
            tasks = []
            for link in items_links:
               task = tg.create_task(scrap_page(link))
               tasks.append(task)
         # Retornamos los datos extraidos
         yield [task.result() for task in tasks], []