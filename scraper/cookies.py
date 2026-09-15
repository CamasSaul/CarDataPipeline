import json
import pathlib
import logging
import asyncio
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

# Resolver rutas
BASE_DIR = pathlib.Path(__file__).resolve().parent

CREDENTIALS_FILEPATH = BASE_DIR / "secrets/credentials.json"
COOKIES_FILEPATH = BASE_DIR / "secrets/cookies.json"
WEB_LINK = "https://facebook.com"
WEB_LOGIN_LINK = WEB_LINK + "/login"
WEB_LOGED_LINK = WEB_LINK + "/"


# Test cookies
async def test_cookies():
   # Verificar que hay sesion iniciada
   play_init = await async_playwright().start()
   engine = play_init.firefox
   browser = await engine.launch(headless=False)
   context = await browser.new_context()
   page = await context.new_page()
   await page.goto(WEB_LOGED_LINK)
   try:
      profile_btn = page.get_by_label("Your profile").first
      await profile_btn.wait_for(state="visible", timeout=10000)
   except Exception as e:
      if logger.level == "DEBUG":
         logger.exception("Error al testear las cookies.")
      else:
         logger.error(f"Cookies test fallo: {e}")
      return False
   finally:
      await page.close()
   return True


# Obtener las cookies de la sesion con las credenciales proporcionadas
async def refresh_cookies():
   """ Retorna `True` si tuvo exito o `False` de lo contrario.
   Esta funcion usa las credenciales en secrets/ para iniciar
   sesion en facebook de forma automatica. Utiliza un ruta
   alternativa donde rellena un formulario con las credenciales y
   otros datos ficticios. Una vez iniciada la sesion guarda las
   cookies en el archivo correspondiente.
   """
   try:
      # Obtener credenciales
      with open(CREDENTIALS_FILEPATH, 'r') as f:
         creds = json.load(f)
      # Iniciar playwright y crear el navegador
      play_init = await async_playwright().start()
      engine = play_init.firefox
      browser = await engine.launch(headless=False)
      context = await browser.new_context()
      page = await context.new_page()
      # Ir inicio de sesion de la web
      await page.goto(WEB_LOGIN_LINK, wait_until="load")
      # Entrar a la seccion de crear cuenta
      await page.get_by_text("Create new account").click()
      # Rellenar los datos del formulario:
      #    - Nombre
      await page.get_by_text("First name").fill("Cookies")
      #    - Apellido
      await page.get_by_text("Last name").fill("Extractor")
      #    - Fecha de nacimeinto: Mes
      await page.get_by_role("combobox").filter(has_text="Month").click()
      await page.get_by_text("January").click()
      #    - Fecha de nacimeinto: Dia
      await page.get_by_role("combobox").filter(has_text="Day").click()
      await page.get_by_role("listbox").get_by_text("1", exact=True).click()
      #    - Fecha de nacimeinto: Anio
      await page.get_by_role("combobox").filter(has_text="Year").click()
      await page.get_by_text("2000").click()
      #    - Genero
      await page.get_by_role("combobox").filter(has_text="Select your gender").click()
      await page.get_by_role("listbox").get_by_text("Male", exact=True).click()
      #    - Correo electronico o numero de telefono
      await page.get_by_label("Mobile number or email").fill(creds["user"])
      #    - Password
      await page.get_by_label("Password").fill(creds["password"])
      # Enviar formulario
      await page.get_by_text("Submit").click()
      # Aceptar los terminos y condiciones
      i_agree = page.get_by_text("I agree", exact=True)
      await i_agree.wait_for(state="visible")
      await i_agree.click()
      # Esperar a que inicie sesion
      profile_btn = page.get_by_label("Your profile").first
      await profile_btn.wait_for(state="visible")
      # Obtener el context state y guardarlo en secrets
      cookies = await context.storage_state()
      with open(COOKIES_FILEPATH, 'w') as c:
         c.write(json.dumps(cookies))
      if await test_cookies():
         return True
      else:
         return False
   except Exception as e:
      if logger.level == "DEBUG":
         logger.exception("Error al extraer las cookies.")
      else:
         logger.error(f"Error al extraer las cookies: {e}")
      return False
   finally:
      await page.close()
   return True