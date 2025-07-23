import pdfplumber
import pandas as pd
import re
from utils import formatear_telefono

def extraer_datos_pdf(path_pdf):
    datos = []

    with pdfplumber.open(path_pdf) as pdf:
        # Recorremos todas las páginas del PDF
        for i, pagina in enumerate(pdf.pages):
            print(f"--- Página {i + 1} ---")
            text = pagina.extract_text()  # Extraemos todo el texto de la página

            if not text:
                print("⚠️ No se detectó texto en esta página.")
                continue

            # Procesamos el texto para extraer los datos de forma flexible
            lineas = text.split("\n")

            # Recorremos todas las líneas buscando los patrones
            for linea in lineas:
                # Ajustamos el patrón para ser más flexible con el nombre y los números
                patron = r"(\d{5,})\s*([A-Za-zÁ-ú\s]+)\s+(\d{2}/\d{2}/\d{4})\s*(\d{10,12})\s*(\d{10,12})\s*([0-9,\.]+)\s*([0-9,\.]+)\s*([0-9,\.]+)"
                match = re.search(patron, linea)

                if match:
                    numero_cliente = match.group(1)  # Número de cliente (lo descartamos)
                    nombre_raw = match.group(2)  # El nombre completo
                    ult_vto = match.group(3)
                    telefono1 = match.group(4)
                    telefono2 = match.group(5)
                    debe = match.group(6).replace(",", "")  # Limpiamos las comas
                    haber = match.group(7).replace(",", "")
                    saldo = match.group(8).replace(",", "")

                    # Limpiar el nombre: eliminamos el número de cliente al principio
                    nombre = nombre_raw.strip()

                    # Validar que los números de saldo y debe no sean negativos
                    if float(debe) < 0 or float(saldo) < 0:
                        continue

                    # Añadimos la información en la lista de datos
                    datos.append({
                        "Nombre": nombre,
                        "ULT_VTO": ult_vto,
                        "DEBE": float(debe),
                        "HABER": float(haber),
                        "SALDO": float(saldo),
                        "Telefono1": formatear_telefono(telefono1),
                        "Telefono2": formatear_telefono(telefono2)
                    })

    # Creamos el DataFrame con los datos extraídos
    df = pd.DataFrame(datos)
    print("Primeras filas válidas:")
    print(df.head(5))  # Mostrar las primeras filas
    return df

if __name__ == "__main__":
    # Reemplaza con la ruta de tu archivo PDF
    df = extraer_datos_pdf("CuentaCorriente.pdf")
    print(f"Total de registros válidos: {len(df)}")
    # Aquí podrías guardarlo en un archivo Excel si lo deseas
    # df.to_excel("clientes_extraidos.xlsx", index=False)
