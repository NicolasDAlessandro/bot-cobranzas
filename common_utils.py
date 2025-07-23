import pandas as pd
import re
from tkinter import messagebox 
from datetime import datetime
import os
import datetime
import time

def log_error(nombre, error_msg, carpeta_logs="logs", dias_retencion=7):
    if not os.path.exists(carpeta_logs):
        os.makedirs(carpeta_logs)
    hoy = datetime.date.today()
    for archivo in os.listdir(carpeta_logs):
        if archivo.startswith("error_log_") and archivo.endswith(".txt"):
            fecha_str = archivo.replace("error_log_", "").replace(".txt", "")
            try:
                fecha_archivo = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
                if (hoy - fecha_archivo).days > dias_retencion:
                    os.remove(os.path.join(carpeta_logs, archivo))
            except:
                continue

    log_file = os.path.join(carpeta_logs, f"error_log_{hoy}.txt")
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {nombre} - {error_msg}\n")


def limpiar_logs_antiguos(directorio="logs", dias=7):
    if not os.path.exists(directorio):
        return
    ahora = time.time()
    for archivo in os.listdir(directorio):
        path = os.path.join(directorio, archivo)
        if os.path.isfile(path):
            creado = os.path.getctime(path)
            if ahora - creado > dias * 86400:
                os.remove(path)

def formatear_telefono(telefono):
    if not telefono or not isinstance(telefono, str):
        return None

    telefono = re.sub(r'\D', '', telefono)  # Eliminar caracteres no numéricos

    if len(telefono) == 7:
        return None  # Fijos de Rosario, se descartan

    if telefono.startswith("15") and len(telefono) in [10, 11, 12]:
        telefono = "341" + telefono[2:]

    elif telefono.startswith("341") and len(telefono) == 10:
        pass 

    elif len(telefono) == 9 and telefono.startswith("15"):
        telefono = "341" + telefono[2:]

    elif telefono.startswith("549") and len(telefono) == 13:
        telefono = telefono[2:]

    elif len(telefono) == 10 and telefono.startswith("11") or telefono.startswith("15"):
        telefono = "341" + telefono[-8:]

    if len(telefono) == 10 and telefono.startswith("341"):
        return "54" + telefono

    return None


def cargar_datos_excel(path_excel):
    try:
        df = pd.read_excel(path_excel)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el archivo Excel.\n{e}")
        return None

    columnas_necesarias = {"Nombre", "ULT_VTO", "DEBE", "HABER", "SALDO"}
    columnas_telefono = {"Telefono1", "Telefono2"}
    if not columnas_necesarias.issubset(set(df.columns)):
        messagebox.showerror("Error", f"Faltan columnas obligatorias.\nSe requieren: {', '.join(columnas_necesarias)}")
        return None

    for col in columnas_telefono:
        if col not in df.columns:
            df[col] = None

    df["Telefono1"] = df["Telefono1"].apply(formatear_telefono)
    df["Telefono2"] = df["Telefono2"].apply(formatear_telefono)

    return df
