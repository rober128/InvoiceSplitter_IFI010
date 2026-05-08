import sys
from pathlib import Path

# =========================
# VALIDACIÓN PARÁMETROS
# =========================
if len(sys.argv) < 3:
    print("Uso: python filtrar_facturas.py <directorio_entrada> <directorio_salida>")
    sys.exit(1)

input_dir = Path(sys.argv[1])
output_dir = Path(sys.argv[2])

if not input_dir.exists():
    print(f"❌ No existe el directorio: {input_dir}")
    sys.exit(1)

output_dir.mkdir(parents=True, exist_ok=True)

# =========================
# CONFIGURACIÓN
# =========================
SUCURSALES_OBJETIVO = {"38", "39"}

# CUITs de proveedores a filtrar. Si está vacío, se aceptan todos.
CUITS_OBJETIVO = {
    "30709515833", # ACE    
    "30538880627", # DDS
    "30517059095", # Monroe
    "30516968431", # Suizo
    "30533285119"  # Asopro
}

# Fecha mínima de comprobantes a filtrar (formato AAAA-MM-DD). Si está vacío o es None, se aceptan todas.
FECHA_DESDE = "2026-05-04"

# =========================
# FUNCIÓN DE FILTRO
# =========================
def cumple_condicion(cabecera):
    try:
        campos = cabecera.split(";")
        sucursal = campos[2]   # tercer campo (índice 2)
        fecha    = campos[7]   # octavo campo (índice 7)
        cuit     = campos[9]   # décimo campo (índice 9)

        if sucursal not in SUCURSALES_OBJETIVO:
            return False

        if FECHA_DESDE and fecha < FECHA_DESDE:
            return False

        if CUITS_OBJETIVO and cuit not in CUITS_OBJETIVO:
            return False

        return True
    except:
        return False

# =========================
# PROCESAMIENTO
# =========================
def procesar_archivo(input_path, output_path):
    try:
        bloques_filtrados = []
        bloque_actual = []
        cabecera_actual = None

        with input_path.open("r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()

                if linea.startswith("C;"):  # CABECERA
                    # evaluar bloque anterior
                    if cabecera_actual and cumple_condicion(cabecera_actual):
                        bloques_filtrados.extend(bloque_actual)

                    cabecera_actual = linea
                    bloque_actual = [linea]

                elif linea.startswith("P;"):  # DETALLE
                    if cabecera_actual:
                        bloque_actual.append(linea)

                else:
                    print(f"⚠️ Línea desconocida en {input_path.name}: {linea}")

        # último bloque
        if cabecera_actual and cumple_condicion(cabecera_actual):
            bloques_filtrados.extend(bloque_actual)

        # guardar archivo
        if bloques_filtrados:
            with output_path.open("w", encoding="utf-8") as f:
                for linea in bloques_filtrados:
                    f.write(linea + "\n")
            print(f"✅ Generado: {output_path}")
        else:
            print(f"ℹ️ Sin coincidencias: {input_path.name}")

    except Exception as e:
        print(f"❌ Error en {input_path.name}: {e}")

# =========================
# LOOP PRINCIPAL
# =========================
print(f"📂 Procesando archivos en: {input_dir}")

for archivo in input_dir.glob("*.txt"):
    salida = output_dir / f"filtrado_{archivo.name}"
    procesar_archivo(archivo, salida)

print("🏁 Proceso terminado")


# python C:\Users\rborlenghi\Documents\Proyecto1\filtrar_facturas.py "C:\Users\rborlenghi\Documents\IFI010\APROCESAR_20260508" "C:\Users\rborlenghi\Documents\IFI010\PROCESADOS_20260508"