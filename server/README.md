
# Proyecto de Búsqueda de PDFs con Milvus

Este proyecto permite consumir archivos PDF, extraer su contenido, generar embeddings de texto, almacenarlos en **Milvus** (una base de datos vectorial) y realizar búsquedas en lenguaje natural sobre el contenido de los PDFs.

## Requisitos

- **Python** 3.7 o superior
- **Docker** (para ejecutar Milvus)
- **Visual C++ Build Tools** (en caso de que se necesiten compilar extensiones en Windows)

## Estructura del Proyecto

```
project/
│
├── config/
│   └── config.py            # Configuración del entorno y parámetros (Milvus, directorios de PDFs)
│
├── data/
│   └── pdfs/                # Aquí se almacenan los PDFs
│
├── embeddings/
│   ├── __init__.py
│   ├── extractor.py         # Funciones para extraer texto de los PDFs
│   ├── vectorizer.py        # Funciones para generar embeddings
│
├── milvus/
│   ├── __init__.py
│   ├── milvus_client.py     # Funciones para interactuar con Milvus
│   ├── insert.py            # Funciones para insertar los datos en Milvus
│   ├── search.py            # Funciones para realizar búsquedas en Milvus
│
├── scripts/
│   ├── load_pdfs.py         # Script para cargar todos los PDFs y procesarlos
│   └── search_query.py      # Script para hacer búsquedas en los documentos
│
└── requirements.txt         # Dependencias del proyecto
```

---

## Instalación y Configuración

### 1. Clonar el Repositorio

Primero, clona el repositorio de este proyecto en tu máquina local:

```bash
git clone https://github.com/Gabicho258/AskYourManual
cd AskYourManual/server
```

### 2. Crear un Entorno Virtual

Se recomienda crear un entorno virtual para evitar conflictos de dependencias. Si no tienes un entorno virtual creado, puedes hacerlo ejecutando los siguientes comandos:

```bash
python -m venv AskYourManualEnv
```

Luego, activa el entorno virtual:

- En **Windows (PowerShell)**:

  ```bash
  .\AskYourManualEnv\Scripts\Activate.ps1
  ```

- En **Windows (CMD)**:

  ```bash
  .\AskYourManualEnv\Scripts\Activate
  ```

### 3. Instalar las Dependencias

Con el entorno virtual activado, instala las dependencias del proyecto utilizando el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Ejecutar Milvus con Docker

Este proyecto utiliza **Milvus** para almacenar los embeddings de los documentos PDF. Puedes ejecutarlo usando Docker.

1. **Instalar Docker**: Si no tienes Docker instalado, [descárgalo desde aquí](https://www.docker.com/products/docker-desktop).

2. **Ejecutar Milvus en Docker**:

   Ejecuta el siguiente comando para descargar y ejecutar Milvus:

   ```bash
   docker pull milvusdb/milvus:v2.0.0
   docker run -d --name milvus -p 19530:19530 -p 19121:19121 milvusdb/milvus:v2.0.0
   ```

   Esto ejecutará Milvus en los puertos `19530` (para la API) y `19121` (para la interfaz web). Puedes verificar que Milvus está funcionando accediendo a `http://localhost:19121`.

### 5. Configuración

Crea o edita el archivo de configuración **`config/config.py`** para especificar las rutas a tus PDFs y las configuraciones de Milvus.

```python
# Configuración de Milvus
MILVUS_HOST = 'localhost'
MILVUS_PORT = '19530'

# Ruta donde se almacenan los PDFs
PDF_DIR = './data/pdfs/'

# Dimensión de los embeddings
EMBEDDING_DIM = 384
```

---

## Uso del Proyecto

### 1. Cargar PDFs en Milvus

Para procesar los PDFs y cargar los embeddings en **Milvus**, ejecuta el siguiente script:

```bash
python scripts/load_pdfs.py
```

Este script extraerá el texto de los archivos PDF en el directorio `data/pdfs/`, generará embeddings y los insertará en la base de datos Milvus.

### 2. Realizar Búsquedas

Una vez que los PDFs se han cargado, puedes realizar búsquedas por similitud. Para ello, ejecuta el siguiente script, que tomará una consulta en lenguaje natural y buscará los documentos más relevantes:

```bash
python scripts/search_query.py
```

Modifica el script `search_query.py` para cambiar la consulta según lo que desees buscar en los documentos.

---

## Solución de Problemas

### Problema: "No se puede encontrar el archivo especificado"

Este error generalmente ocurre cuando el sistema no tiene permisos suficientes para escribir archivos en las carpetas del proyecto. Solución:

- Asegúrate de ejecutar el terminal como **Administrador** (en Windows).
- Verifica que el directorio donde se almacenan los PDFs tiene permisos de escritura.

### Problema: "Microsoft Visual C++ 14.0 or greater is required"

Si ves un error similar a este al instalar dependencias, debes instalar **Microsoft Visual C++ Build Tools** desde [aquí](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

---

## Estructura de los Archivos

### `load_pdfs.py`

Este script carga todos los PDFs desde el directorio configurado, extrae su texto, genera embeddings y los inserta en Milvus.

### `search_query.py`

Este script permite realizar búsquedas sobre los PDFs cargados en Milvus. La búsqueda se realiza transformando una consulta de texto en un embedding y buscando los vectores más cercanos en la base de datos.

---

## Actualización y Mantenimiento

Para actualizar las dependencias, simplemente ejecuta:

```bash
pip install --upgrade -r requirements.txt
```

---

## Licencia

Este proyecto está bajo la **Licencia MIT**. Ver el archivo `LICENSE` para más detalles.

