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

### Con Docker (Recomendado)

- Docker Desktop 20.10+
- Docker Compose 2.0+
- SQL Server accesible (local o remoto)

### Sin Docker (Desarrollo local)

- Python 3.9+
- SQL Server 2016 o superior
- ODBC Driver 17 for SQL Server

## Instalación y Ejecución

### Opción 1: Con Docker Compose (Recomendado)

#### 1. Clonar el repositorio

```bash
git clone <url-repositorio>
cd pqrs_back
```

#### 2. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
copy .env.example .env   # Windows
cp .env.example .env     # Linux/Mac

# Editar .env con tus configuraciones
```

**Configurar DATABASE_URL:**

> **Importante:** Si tu SQL Server está en tu máquina local (fuera de Docker), usa `host.docker.internal` en lugar de `localhost`:

Con autenticación SQL Server:

```env
DATABASE_URL=mssql+pyodbc://usuario:contraseña@host.docker.internal:1433/db_pqrs?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

Con SQL Server remoto:

```env
DATABASE_URL=mssql+pyodbc://usuario:contraseña@servidor.ejemplo.com:1433/db_pqrs?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

**Generar SECRET_KEY segura:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 3. Crear base de datos

Conectarse a SQL Server y ejecutar:

```sql
CREATE DATABASE db_pqrs;
GO

USE db_pqrs;
GO
```

#### 4. Construir y ejecutar con Docker Compose

```bash
# Construir la imagen y levantar el contenedor
docker-compose up --build

# O en modo detached (segundo plano)
docker-compose up -d --build
```

#### 5. Crear tablas en la base de datos

```bash
# Ejecutar dentro del contenedor
docker exec -it pqrs_api python create_tables.py
```

Seleccionar opción 1 para crear las tablas.

#### 6. Acceder a la aplicación

- API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- Documentación ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

#### Comandos útiles de Docker

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs solo del servicio api
docker-compose logs -f api

# Detener el contenedor
docker-compose stop

# Detener y eliminar los contenedores
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Reiniciar el servicio
docker-compose restart

# Reconstruir sin caché
docker-compose build --no-cache

# Ejecutar comandos dentro del contenedor
docker exec -it pqrs_api bash
docker exec -it pqrs_api python -c "from app.database import verify_connection; print('OK' if verify_connection() else 'ERROR')"
```

---

### Opción 2: Sin Docker (Desarrollo local)

#### 1. Clonar el repositorio

```bash
git clone <url-repositorio>
cd pqrs_back
```

#### 2. Configurar SQL Server

##### Instalar ODBC Driver 17 for SQL Server

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

##### Crear base de datos

Conectarse a SQL Server y ejecutar:

```sql
CREATE DATABASE db_pqrs;
GO

USE db_pqrs;
GO
```

#### 3. Crear entorno virtual e instalar dependencias

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

#### 4. Configurar variables de entorno

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

#### 5. Crear tablas en la base de datos

```bash
python create_tables.py
```

Seleccionar opción 1 para crear las tablas.

#### 6. Verificar instalación

```bash
# Verificar conexión a base de datos
python -c "from app.database import verify_connection; print('OK' if verify_connection() else 'ERROR')"
```

#### 7. Ejecutar la aplicación

**Modo desarrollo:**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Modo producción:**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 8. Acceder a la aplicación

- API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- Documentación ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Ejecutar Tests

### Con Docker

```bash
# Todos los tests
docker exec -it pqrs_api pytest

# Tests con cobertura
docker exec -it pqrs_api pytest --cov=app tests/

# Tests con output detallado
docker exec -it pqrs_api pytest -v
```

### Sin Docker

```bash
# Todos los tests
pytest

# Tests con cobertura
pytest --cov=app tests/

# Tests con output detallado
pytest -v
```

## Troubleshooting

### Problemas comunes con Docker

#### 1. Error de conexión a SQL Server

**Síntoma:** `Cannot open database "db_pqrs"`

**Solución:**

- Verifica que SQL Server esté corriendo
- Usa `host.docker.internal` en lugar de `localhost` en DATABASE_URL
- Asegúrate de que la base de datos existe

#### 2. Error "TrustServerCertificate"

**Síntoma:** `SSL Provider: The certificate chain was issued by an authority that is not trusted`

**Solución:**
Agrega `TrustServerCertificate=yes` a tu DATABASE_URL:

```env
DATABASE_URL=mssql+pyodbc://user:pass@host.docker.internal:1433/db_pqrs?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

#### 3. Contenedor se detiene inmediatamente

**Síntoma:** El contenedor inicia pero se detiene de inmediato

**Solución:**

```bash
# Ver logs para identificar el error
docker-compose logs api

# Verificar variables de entorno
docker exec -it pqrs_api env | grep DATABASE_URL
```

#### 4. Cambios en el código no se reflejan

**Síntoma:** Modificas el código pero no ves los cambios

**Solución:**

- El modo `--reload` está activo, los cambios deberían reflejarse automáticamente
- Si no funciona, reinicia el contenedor:

```bash
docker-compose restart
```

#### 5. Puerto 8000 ya en uso

**Síntoma:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solución:**

```bash
# Opción 1: Detener el proceso que usa el puerto
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i :8000
kill -9 <PID>

# Opción 2: Cambiar el puerto en docker-compose.yml
# Modificar: "8001:8000" en lugar de "8000:8000"
```

### Verificar estado del sistema

```bash
# Ver contenedores corriendo
docker ps

# Ver uso de recursos
docker stats pqrs_api

# Verificar conexión a base de datos desde el contenedor
docker exec -it pqrs_api python -c "from app.database import verify_connection; print('✅ OK' if verify_connection() else '❌ ERROR')"

# Ver variables de entorno del contenedor
docker exec -it pqrs_api env
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
├── uploads/          # Archivos cargados
├── Dockerfile        # Configuración de imagen Docker
├── docker-compose.yml # Orquestación de contenedores
└── requirements.txt  # Dependencias Python
```

## Configuración de Docker

### Dockerfile

El proyecto incluye un `Dockerfile` optimizado que:

- Usa Python 3.11.9 slim como base
- Instala ODBC Driver 18 for SQL Server
- Instala dependencias de WeasyPrint para generación de PDFs
- Configura el entorno de desarrollo con hot-reload

### docker-compose.yml

Configuración del servicio:

- **Puerto:** 8000 (mapeado a localhost:8000)
- **Volúmenes:** Código montado para desarrollo en vivo
- **Variables de entorno:** Cargadas desde archivo `.env`
- **Networking:** Acceso a `host.docker.internal` para SQL Server local
- **Restart policy:** `always` para alta disponibilidad

### Mejores Prácticas

1. **Variables de entorno sensibles:**

   - Nunca commitear el archivo `.env`
   - Usar `.env.example` como plantilla
   - Rotar SECRET_KEY regularmente

2. **Desarrollo:**

   - Usar `docker-compose up` (sin `-d`) para ver logs en tiempo real
   - Los cambios en el código se reflejan automáticamente (hot-reload)
   - Usar `docker-compose logs -f` para seguir logs

3. **Producción:**

   - Cambiar `--reload` por configuración de workers en `docker-compose.yml`
   - Usar variables de entorno específicas de producción
   - Configurar health checks y monitoring

4. **Base de datos:**
   - Mantener SQL Server fuera del contenedor para persistencia
   - Usar `host.docker.internal` para conexión desde Docker
   - Hacer backups regulares de la base de datos

## Tecnologías

- FastAPI
- SQLAlchemy
- Pydantic
- Python-JOSE (JWT)
- WeasyPrint (PDFs)
- APScheduler
- Microsoft Graph API
