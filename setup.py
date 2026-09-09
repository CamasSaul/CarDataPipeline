import asyncio
import json
import os
from playwright.async_api import async_playwright

URL = "https://facebook.com"
COOKIES_PATH = "scraper/secrets/"
os.makedirs(COOKIES_PATH)


async def get_cookies():
   input("Se necesitan cookies para iniciar el proceso de scraper.\n" \
   "Inicie sesión por única vez para establecer la configuración.\n" \
   "A continuación se abrirá un navegador dónde tendrá que iniciar sesión en el portal de facebook y resolver el captcha.\n" \
   "Presione enter para continuar...")
   engine = await async_playwright().start()
   navigator = getattr(engine, "firefox")
   browser = await navigator.launch(headless=False)
   context = await browser.new_context(locale="es_LA")
   page = await context.new_page()
   await page.goto(URL)
   input("Presione de nuevo enter después de iniciar sesión...")
   cookies = await context.storage_state()
   with open(COOKIES_PATH + "cookies.json", 'w') as file:
      file.write(json.dumps(cookies))


if __name__ == "__main__":
   asyncio.run(get_cookies())