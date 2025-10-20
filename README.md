# HealthConnect MVP

HealthConnect es un proyecto de Web App en el sector HealthTech que busca unificar la gestión de citas presenciales y virtuales, el acceso a historiales médicos y la teleasistencia en una sola plataforma.

## Estructura del Proyecto

```
healthConnect_MVP_38/
├── backend/               # API Backend (FastAPI)
│   ├── app/              # Módulo principal de la aplicación
│   ├── main.py           # Punto de entrada
│   ├── requirements.txt  # Dependencias Python
│   └── README.md         # Documentación del backend
├── frontend/             # Frontend Web (React + Vite)
│   ├── src/              # Código fuente React
│   ├── package.json      # Dependencias Node.js
│   └── README.md         # Documentación del frontend
└── README.md             # Este archivo
```

## Tecnologías Utilizadas

### Backend
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para base de datos
- **PostgreSQL** - Base de datos relacional
- **Google Calendar API** - Integración con calendario
- **Google Meet API** - Integración con videollamadas

### Frontend
- **React** - Biblioteca de UI
- **Vite** - Build tool y dev server
- **JavaScript** - Lenguaje de programación

## Instalación y Configuración

### Backend (LINUX, MAC, CODESPACE)
```bash
cd backend
pip install -r requirements.txt
python3 -m venv venv
./venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
bash (Windows)
```cd backend
python -m venv backedn/venv
./venv/Scripts/activate
pip install -r requirements.txt
pip install tzdata
pip install fastapi uvicorn[standard] sqlalchemy pydantic python-multipart python-decouple passlib[bcrypt] python-dotenv psycopg2-binary
pip install supabase
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Características Principales

- ✅ Gestión de usuarios y autenticación
- ✅ Sistema de citas médicas
- ✅ Integración con Google Calendar
- ✅ Videollamadas con Google Meet
- ✅ API REST con documentación automática
- ✅ Frontend moderno con React
- ✅ Base de datos PostgreSQL

## Documentación

- [Backend README](backend/README.md) - Documentación detallada del API
- [Frontend README](frontend/README.md) - Documentación del frontend React

## Desarrollo

Para desarrollo local:
1. Configurar PostgreSQL
2. Configurar variables de entorno (ver backend/.env.example)
3. Ejecutar backend en puerto 8000
4. Ejecutar frontend en puerto 5173 (Vite default)

La documentación interactiva del API está disponible en `http://localhost:8000/docs`.
<<<<<<< HEAD
=======

URL publica del backend para consumo posiblemente en fronted si es necesario: https://reimagined-carnival-695qvv6jjvxp3x4wx-5762.app.github.dev/
>>>>>>> f9ff98522ec626a25d70cff59a0898a0d5063808
