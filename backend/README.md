# HealthConnect - Backend

Este es el backend de HealthConnect, una aplicación de gestión médica desarrollada con FastAPI.

## Estructura del Proyecto

```
backend/
├── app/                    # Módulo principal de la aplicación
│   ├── models/            # Modelos de base de datos (SQLAlchemy)
│   │   ├── appointment.py # Modelo de citas médicas
│   │   └── user.py        # Modelo de usuarios
│   ├── routes/            # Rutas de la API
│   │   ├── citas.py       # Endpoints de citas
│   │   └── ruta.py        # Endpoints de autenticación
│   ├── utils/             # Utilidades y helpers
│   │   ├── google_tokens.py      # Integración con Google
│   │   ├── integration_helpers.py # Helpers de integración
│   │   ├── schemas.py            # Esquemas Pydantic
│   │   ├── security.py           # Funciones de seguridad
│   │   └── servicios_meet_calendar.py # Servicios de Google Meet
│   ├── config.py          # Configuración de la aplicación
│   ├── database.py        # Configuración de base de datos
│   └── excepciones.py     # Manejo de excepciones personalizadas
├── main.py                # Punto de entrada de la aplicación
├── requirements.txt       # Dependencias de Python
└── .env                   # Variables de entorno (no versionado)
```

## Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido para APIs
- **SQLAlchemy**: ORM para base de datos
- **PostgreSQL**: Base de datos relacional
- **Pydantic**: Validación de datos
- **Google Calendar API**: Integración con Google Calendar
- **Google Meet API**: Integración con Google Meet

## Instalación y Configuración

1. **Instalar dependencias:**
   ```bash
   cd backend  
   python3 -m venv venv
   source backend/venv/bin/activate
   pip install -r requirements.txt
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Configurar variables de entorno:**
   - Copiar `.env.example` a `.env`
   - Configurar las variables necesarias (base de datos, APIs de Google, etc.)

3. **Ejecutar la aplicación:**
   ```bash
   
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Endpoints

### Autenticación (`/api/v1/auth`)
- `POST /register` - Registro de usuarios
- `POST /login` - Inicio de sesión
- `POST /refresh` - Renovar token

### Citas (`/api/v1/appointments`)
- `GET /` - Listar citas
- `POST /` - Crear nueva cita
- `GET /{id}` - Obtener cita específica
- `PUT /{id}` - Actualizar cita
- `DELETE /{id}` - Eliminar cita

## Características

- ✅ Autenticación JWT
- ✅ Gestión de usuarios
- ✅ Gestión de citas médicas
- ✅ Integración con Google Calendar
- ✅ Integración con Google Meet
- ✅ CORS configurado
- ✅ Manejo de excepciones
- ✅ Logging configurado
- ✅ Validación de datos con Pydantic

## Desarrollo

Para desarrollo local, asegúrate de tener:
- Python 3.8+
- PostgreSQL ejecutándose
- Variables de entorno configuradas
- Credenciales de Google APIs configuradas

La aplicación se ejecuta en ` http://127.0.0.1:8000` y la documentación interactiva está disponible en `http://localhost:8000/docs`.
