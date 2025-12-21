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
- SQL Server
- ODBC Driver 17 for SQL Server

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. Ejecutar migraciones de base de datos (si aplica)

## Ejecución

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en `http://localhost:8000`

Documentación interactiva:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

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
