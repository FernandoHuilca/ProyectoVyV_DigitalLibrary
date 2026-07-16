from pathlib import Path

# Carpetas y archivos que usualmente queremos ignorar en un proyecto de Python
IGNORAR = {
    '.git',
    '__pycache__',
    '.venv',
    'venv',
    '.idea',
    '.vscode',
    '.pytest_cache',
    'build',
    'dist',
    '.DS_Store'  # Exclusivo de macOS
}


def mostrar_arbol(ruta_dir: Path, prefijo: str = ""):
    # Obtenemos y ordenamos el contenido: carpetas primero, luego archivos
    try:
        elementos = sorted(
            [x for x in ruta_dir.iterdir() if x.name not in IGNORAR],
            key=lambda x: (not x.is_dir(), x.name.lower())
        )
    except PermissionError:
        # Por si el script no tiene permisos para leer alguna carpeta del sistema
        return

    for i, elemento in enumerate(elementos):
        # Detectamos si es el último elemento del nivel para ajustar los caracteres de las ramas
        es_ultimo = (i == len(elementos) - 1)
        conector = "└── " if es_ultimo else "├── "

        # Imprimimos el archivo o carpeta actual
        print(f"{prefijo}{conector}{elemento.name}{'/' if elemento.is_dir() else ''}")

        # Si es una carpeta, llamamos recursivamente a la función
        if elemento.is_dir():
            nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
            mostrar_arbol(elemento, nuevo_prefijo)


if __name__ == "__main__":
    # "." indica el directorio actual (donde ejecutas el script)
    ruta_proyecto = Path(".")

    print(f"\n📁 Estructura del proyecto: {ruta_proyecto.resolve().name}/")
    print("─" * 40)
    mostrar_arbol(ruta_proyecto)
    print("─" * 40 + "\n")