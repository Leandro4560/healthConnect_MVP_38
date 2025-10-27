# HealthConnect MVP

## Deploy trigger

HealthConnect es un proyecto de Web App en el sector HealthTech que busca unificar la gestión de citas presenciales y virtuales, el acceso a historiales médicos y la teleasistencia en una sola plataforma.

## Estructura del Proyecto

```bash
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
# HealthConnect MVP

## Deploy trigger

HealthConnect es un proyecto de Web App en el sector HealthTech que busca unificar la gestión de citas presenciales y virtuales, el acceso a historiales médicos y la teleasistencia en una sola plataforma.

## Estructura del proyecto

```bash
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

## Tecnologías utilizadas

### Backend

- **FastAPI** — Framework web moderno y rápido
- **SQLAlchemy** — ORM para base de datos
- **PostgreSQL** — Base de datos relacional
- **Google Calendar API** — Integración con calendario
- **Google Meet API** — Integración con videollamadas

### Frontend

- **React** — Biblioteca de UI
- **Vite** — Build tool y dev server
- **JavaScript** — Lenguaje de programación

## Instalación y configuración

### Backend (Linux / macOS / Codespace)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Backend (Windows — cmd)

```cmd
cd backend
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install tzdata
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Características principales

- ✅ Gestión de usuarios y autenticación
- ✅ Sistema de citas médicas
- ✅ Integración con Google Calendar
- ✅ Videollamadas con Google Meet
- ✅ API REST con documentación automática
- ✅ Frontend moderno con React
- ✅ Base de datos PostgreSQL

## Documentación

- [Backend README](backend/README.md) — Documentación detallada del API
- [Frontend README](frontend/README.md) — Documentación del frontend React

## Desarrollo

Para desarrollo local:

1. Configurar PostgreSQL
2. Configurar variables de entorno (ver `backend/.env.example`)
3. Ejecutar backend en puerto 8000
4. Ejecutar frontend en puerto 5173 (Vite default)

La documentación interactiva del API está disponible en [http://localhost:8000/docs](http://localhost:8000/docs).

URL pública del backend (uso opcional desde frontend):

[https://reimagined-carnival-695qvv6jjvxp3x4wx-5762.app.github.dev/](https://reimagined-carnival-695qvv6jjvxp3x4wx-5762.app.github.dev/)

