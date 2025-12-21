# Sistema de Gestión de PQR Escaladas

Backend API desarrollado con FastAPI para la gestión de Peticiones, Quejas y Reclamos (PQR) escaladas.

## Características

- API RESTful con FastAPI
- Autenticación JWT
- Integración con Microsoft Graph para correo electrónico
- Generación de PDFs
- Gestión de adjuntos
- Auditoría de operaciones
- Programación de tareas automatizadas
- Base de datos SQL Server

## Requisitos

- Python 3.9+
- SQL Server 2016 o superior
- ODBC Driver 17 for SQL Server

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-repositorio>
cd pqrs_back
```

### 2. Configurar SQL Server

#### Instalar ODBC Driver 17 for SQL Server

**Windows:**
- Descargar desde: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
- Ejecutar el instalador

**Linux:**
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

#### Crear base de datos

Conectarse a SQL Server y ejecutar:

```sql
CREATE DATABASE db_pqrs;
GO

USE db_pqrs;
GO
```

### 3. Crear entorno virtual e instalar dependencias

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
copy .env.example .env   # Windows
cp .env.example .env     # Linux/Mac

# Editar .env con tus configuraciones
```

**Configurar DATABASE_URL:**

Con autenticación SQL Server:
```env
DATABASE_URL=mssql+pyodbc://usuario:contraseña@localhost:1433/db_pqrs?driver=ODBC+Driver+17+for+SQL+Server
```

Con autenticación Windows:
```env
DATABASE_URL=mssql+pyodbc://localhost/db_pqrs?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

**Generar SECRET_KEY segura:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Crear tablas en la base de datos

```bash
python create_tables.py
```

Seleccionar opción 1 para crear las tablas.

### 6. Verificar instalación

```bash
# Verificar conexión a base de datos
python -c "from app.database import verify_connection; print('OK' if verify_connection() else 'ERROR')"
```

## Ejecución

### Modo desarrollo

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Modo producción

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Acceder a la aplicación

- API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- Documentación ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests con cobertura
pytest --cov=app tests/

# Tests con output detallado
pytest -v
```

## Estructura del Proyecto

```
pqr-backend/
├── app/              # Código fuente principal
│   ├── api/          # Endpoints de la API
│   ├── core/         # Módulos core (seguridad, excepciones)
│   ├── models/       # Modelos de base de datos
│   ├── schemas/      # Esquemas Pydantic
│   ├── services/     # Lógica de negocio
│   ├── templates/    # Templates HTML/PDF
│   └── utils/        # Utilidades
├── tests/            # Tests
└── uploads/          # Archivos cargados
```

## Tecnologías

- FastAPI
- SQLAlchemy
- Pydantic
- Python-JOSE (JWT)
- WeasyPrint (PDFs)
- APScheduler
- Microsoft Graph API
