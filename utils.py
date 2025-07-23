import pdfplumber
import pandas as pd
import re
from common_utils import formatear_telefono  


def extraer_datos_pdf(path_pdf):
    datos = []
    descartes = []

    with pdfplumber.open(path_pdf) as pdf:
        for i, pagina in enumerate(pdf.pages):
            print(f"--- Página {i + 1} ---")
            text = pagina.extract_text()

            if not text:
                print("⚠️ No se detectó texto en esta página.")
                continue

            lineas = text.split("\n")
            patrones = [
                r"(\d{5,})\s*([A-Za-zÁ-ú\s]+?)\s+(\d{2}/\d{2}/\d{4})\s*(\d{10,12})\s*(\d{10,12})\s*([0-9,\.]+)\s*([0-9,\.]+)\s*([0-9,\.]+)",  
                r"(\d{5,})\s*([A-Za-zÁ-ú\s]+?)\s+(\d{2}/\d{2}/\d{4})\s*(\d{10,12})\s*([0-9,\.]+)\s*([0-9,\.]+)\s*([0-9,\.]+)",  
                r"(\d{5,})\s*([A-Za-zÁ-ú\s]+?)\s+(\d{2}/\d{2}/\d{4})\s*([0-9,\.]+)\s*([0-9,\.]+)\s*([0-9,\.]+)",
            ]

            for linea in lineas:
                encontrado = False
                for patron in patrones:
                    match = re.search(patron, linea)

                    if match:
                        numero_cliente = match.group(1)
                        nombre_raw = match.group(2)
                        ult_vto = match.group(3)
                        telefono1 = match.group(4) if len(match.group(4)) > 0 else ""
                        telefono2 = match.group(5) if len(match.group(5)) > 0 else ""
                        debe = match.group(6).replace(",", "")
                        haber = match.group(7).replace(",", "")
                        saldo = match.group(8).replace(",", "")

                        nombre = nombre_raw.strip()

                        if float(debe) < 0 or float(saldo) < 0:
                            descartes.append((linea, "Saldo o debe negativo"))
                            continue

                        datos.append({
                            "Nombre": nombre,
                            "ULT_VTO": ult_vto,
                            "DEBE": float(debe),
                            "HABER": float(haber),
                            "SALDO": float(saldo),
                            "Telefono1": formatear_telefono(telefono1),
                            "Telefono2": formatear_telefono(telefono2)
                        })

                        encontrado = True
                        break

                if not encontrado:
                    descartes.append((linea, "No se encontró patrón"))

    df = pd.DataFrame(datos)

    with open("descartes.txt", "w", encoding="utf-8") as f:
        for linea, motivo in descartes:
            f.write(f"{motivo} → {linea}\n")

    print("Primeras filas válidas:")
    print(df.head(5))
    print(f"Total de registros válidos: {len(df)}")
    return df
