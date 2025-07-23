import time
import pandas as pd
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from common_utils import log_error


def inicializar_driver():
    options = Options()
    options.add_argument("--user-data-dir=C:/bot-whatsapp/usuario")
    options.add_argument("--profile-directory=Default")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 120)  
    return driver, wait

def enviar_mensajes(df, mensaje_base, callback_log=None, modo_prueba=False):
    enviados = 0
    fallidos = 0

    if not modo_prueba:
        driver, wait = inicializar_driver()
        driver.get("https://web.whatsapp.com")
        try:
            wait.until(EC.presence_of_element_located((By.ID, "side")))  # Espera a que cargue la interfaz
        except Exception:
            if callback_log:
                callback_log("❌ No se detectó el login de WhatsApp. ¿Escaneaste el QR?")
            return 0, len(df)
    else:
        driver = wait = None

    for _, row in df.iterrows():
        nombre = row.get("Nombre", "")
        telefono1 = row.get("Telefono1")
        telefono2 = row.get("Telefono2")
        numero = telefono1 or telefono2

        if not numero:
            log_error(nombre, "No hay número válido")
            if callback_log:
                callback_log(f"❌ {nombre}: Sin número válido.")
            fallidos += 1
            continue

        variables = row.to_dict()
        mensaje = mensaje_base
        for clave, valor in variables.items():
            mensaje = mensaje.replace(f"{{{clave}}}", str(valor) if pd.notna(valor) else "")

        if modo_prueba:
            if callback_log:
                callback_log(f"[MODO PRUEBA] A {nombre} ({numero}): {mensaje}")
            enviados += 1
            continue

        try:
            driver.get(f"https://web.whatsapp.com/send?phone={numero}")
            time.sleep(10)
            caja = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true" and @data-tab="10"]')))
            caja.click()
            caja.send_keys(mensaje)
            time.sleep(1)
            caja.send_keys(Keys.ENTER)
            enviados += 1
            if callback_log:
                callback_log(f"✅ Enviado a {nombre} ({numero})")
            delay = random.uniform(7, 15)  # Delay aleatorio entre mensajes
            time.sleep(delay)
        except Exception as e:
            log_error(nombre, str(e))
            if callback_log:
                callback_log(f"❌ Falló con {nombre}: {e}")
            fallidos += 1
            continue

    if driver:
        driver.quit()

    return enviados, fallidos
