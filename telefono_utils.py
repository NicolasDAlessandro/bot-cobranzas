import re

def formatear_telefono(telefono):
    if not telefono or not isinstance(telefono, str):
        return None

    # Eliminar caracteres no numéricos
    telefono = re.sub(r'\D', '', telefono)

    # Si es número fijo de Rosario (7 dígitos)
    if len(telefono) == 7:
        return None  # descartamos fijos (si querés usarlo, devolvé "0341" + telefono)

    # Si empieza con 15 y es un celular local
    if telefono.startswith("15") and len(telefono) in [10, 11, 12]:
        telefono = "341" + telefono[2:]

    # Si empieza con 341 (característica de Rosario)
    elif telefono.startswith("341") and len(telefono) == 10:
        pass  # está bien

    # Si es celular sin característica, por ejemplo 152785685 → agregamos 341
    elif len(telefono) == 9 and telefono.startswith("15"):
        telefono = "341" + telefono[2:]

    # Si es celular completo internacional (con 549)
    elif telefono.startswith("549") and len(telefono) == 13:
        telefono = telefono[2:]  # removemos el 54

    # Si es celular sin 54
    elif len(telefono) == 10 and telefono.startswith("11") or telefono.startswith("15"):
        telefono = "341" + telefono[-8:]

    # Validar que tenga 10 dígitos para WhatsApp (sin +54)
    if len(telefono) == 10 and telefono.startswith("341"):
        return "54" + telefono

    return None  # si no pasa validaciones
