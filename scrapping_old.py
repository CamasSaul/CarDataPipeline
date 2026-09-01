import logging
import asyncio
import base64
import aiohttp
import os
import re
import json
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from playwright.async_api import async_playwright



from dbmanager import DataBase
from dbmanager import CarPost, Source # Data Models


logger = logging.getLogger(__name__)

# ===== CONFIG =====
WEB_URL = 'https://www.facebook.com/groups/281469946378043/?locale=es_ES'
STATE_FILE = 'data/state.json'
SCROLL_PAUSE = 2
MAX_SCROLLS = 10
INPUT_FILE = Path('publicaciones.json')
OUTPUT_FILE = Path('raw_data.json')

I_COUNT = 0
EXC_COUNT = 0

STATE_FILE = 'data/state.json'
WEB_LINLKS = [
   'https://www.facebook.com/groups/281469946378043/?locale=es_ES'
]


class Browser:
   def __init__(self):
      self.playwright = None
      self.browser = None

   async def create(self, navigator_name:str='chromium', headless:bool=False, slow_mo:int=100):
      self.playwright = await async_playwright().start()
      navigator = getattr(self.playwright, navigator_name)
      self.browser = await navigator.launch(headless=headless, slow_mo=slow_mo)

   async def _new_page(self, state_file:str=STATE_FILE):
      if not self.browser:
         await self.create()
      if state_file and os.path.exists(state_file):
         logger.info('Sesion cargada.')
         context = await self.browser.new_context(storage_state=state_file, locale="es-ES")
      else:
         logger.info('Cokkies no encontradas.')
         context = await self.browser.new_context(locale='es-ES')
         page = await context.new_page()
         await page.goto('https://www.facebook.com/login?locale=es_ES')
         input('Inicia sesion manualmente y presiona Enter para guardar la sesion...')
         await context.storage_state(path=STATE_FILE)
         logger.info('Sesion guardada en \'state.json\'.')
      return await context.new_page()

   async def close(self):
      if self.browser:
         await self.browser.close()
      if self.playwright:
         await self.playwright.stop()
   

class Scrapper:
   def __init__(self, config:dict=None):
      # Crear conexion a la base de datos
      self.db = DataBase('cardb')
      # Obtener tabla de paginas web para escrapear

   def _get_webpages_table (self) -> list:
      return self.db.select(Source)
   
   async def _get_image_as_base64(self, url):
      """Descarga una imagen y la devuelve en base64."""
      try:
         async with aiohttp.ClientSession() as session:
               async with session.get(url) as resp:
                  if resp.status == 200:
                     content = await resp.read()
                     return base64.b64encode(content).decode('utf-8')
      except Exception as e:
         logger.exception(f'Error descargando imagen {url}: {e}')
      return None

   async def _scroll_feed(self, page, scrolls=10, delay=1):
      for i in range(scrolls):
         logger.info(f'Scroll {i+1}/{scrolls}')
         await page.mouse.wheel(0, 3000)
         await asyncio.sleep(delay)

   # Escrapear la pagina
   async def _scrap_page(self, page, source_id):
      data = {}
      await self._scroll_feed(page)
      # Obtener HTML actual
      html = await page.content()
      soup = BeautifulSoup(html, 'lxml')
      # Buscar el feed principal
      feed = soup.find('div', attrs={'role': 'feed'})
      if not feed:
         logger.warning('No se encontro el feed principal.')
         return data
      
      # Buscar enlaces dentro del feed
      pubs = feed.find_all('div', class_='html-div')
      for pub in pubs:
         anchors = pub.find_all('a')
         for a in anchors:
               href = a.get('href')
               if href and '/commerce/listing' in href and 'media_id' not in href:
                  link = f'https://www.facebook.com{href}'
                  data[link] = True
                  break

      if not data:
         logger.warning('No se encontro ningun enlace de publicacion.')
         return data
      
      os.makedirs('images', exist_ok=True)

      # Iterar sobre los enlaces encontrados
      for link in list(data.keys()):
         try:
               new_page = await self.browser._new_page()
               logger.info(f'Abriendo link de publicacion')
               await new_page.goto(link, wait_until='domcontentloaded', timeout=20000)
               await asyncio.sleep(2)

               # Hacer clic en todos los botones "Ver mas" antes de leer el texto
               try:
                  # Esto cubrira textos como "Ver mas", "See more", "Mostrar mas"
                  buttons = await new_page.locator('text=/ver m\u00e1s|see more|mostrar m\u00e1s/i').all()
                  for btn in buttons:
                     try:
                           await btn.click(timeout=1000)
                           await asyncio.sleep(0.5)
                     except:
                           pass
               except Exception as e:
                  print(f'No se encontraron botones "Ver mas": {e}')

               # Extraer HTML actualizado despues del clic
               html = await new_page.content()
               soup = BeautifulSoup(html, 'lxml')

               # Extraer imagenes
               imgs = soup.find_all('img')
               imgs_scr = set()
               for img in imgs:
                  if len(imgs_scr) >= 4:
                     break
                  src = img.get('src')
                  if src:
                     imgs_scr.add(src)

               # Texto expandido completo
               inner_text = soup.get_text(separator=' ', strip=True)

               # Descargar la primera imagen (si existe)
               if imgs_scr:
                  first_img = next(iter(imgs_scr))  
                  img_b = await self._get_image_as_base64(first_img)

               data[link] = CarPost(
                     timestamp = datetime.utcnow(),
                     source = source_id,
                     post_link = link,
                     raw_text = inner_text,
                     raw_img = img_b,
                     imgs_scr = json.dumps(list(imgs_scr))
                  )
               logger.info('Publicacion extraida.')

         except Exception as e:
               logger.exception(f'Error procesando.')
         finally:
               await new_page.close()
      return data
   
   # Extrae una muestra de datos de cada pagina disponible
   async def sample (self):
      try:
         data = {}
         self.browser = Browser()
         # Obtener las urls de paginas web
         for obj in self._get_webpages_table():
               id = obj.id
               url = obj.url
               page = await self.browser._new_page(STATE_FILE) # Crear tab para navegar
               await page.goto(url, wait_until='domcontentloaded')
               data.update(await self._scrap_page(page, id))
               await asyncio.sleep(2)
               await page.close()
         for obj in data.values():
               self.db.insert(obj)
         await self.browser.close()
      except Exception as e:
         logger.exception('Error extrayendo datos.')
         await self.stop()

   async def loop (self):
      global I_COUNT, EXC_COUNT
      try:
         data = {}
         self.browser = Browser()
         # Obtener las urls de paginas web
         while True:
               I_COUNT += 1
               for obj in self._get_webpages_table():
                  if not obj:
                     return
                  id = obj.id
                  url = obj.url
                  page = await self.browser._new_page(STATE_FILE) # Crear una tab para navegar
                  await page.goto(url, wait_until='domcontentloaded')
                  data.update(await self._scrap_page(page, id))
                  await asyncio.sleep(2)
                  await page.close()
               for obj in data.values():
                  try:
                     self.db.insert(obj)
                  except:
                     EXC_COUNT += 1
                     logger.exception('Error extrayendo datos.')
      except Exception as e:
         logger.exception('E')
         await self.stop()
      finally:
         await self.browser.close()

   def pause (self):
      ...
   
   async def stop (self):
      await self.browser.close()


async def scrapping_main ():
   fatals = []
   scrapper = Scrapper()
   await scrapper.loop()


if __name__ == '__main__':
   import asyncio
   import time
   fatals = []
   try:
      while True:
         try:
               scrapper = Scrapper()
               asyncio.run(scrapper.loop())
         except Exception as e:
               logger.exception('Error fatal.')
               fatals.append(e)
         time.sleep(5*60)
   except:    
      logger.info('Total de errores fatales: %i fatals' % fatals)