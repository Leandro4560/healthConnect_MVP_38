# My Fullstack App

Este proyecto es una aplicación fullstack que incluye un backend y un frontend, ambos dockerizados. A continuación se detallan las características y la estructura del proyecto.

## Estructura del Proyecto

```
my-fullstack-app
├── backend
│   ├── src
│   │   ├── index.ts
│   │   ├── controllers
│   │   │   └── exampleController.ts
│   │   ├── routes
│   │   │   └── index.ts
│   │   └── config
│   │       └── index.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── Dockerfile
│   ├── .env.example
│   └── README.md
├── frontend
│   ├── src
│   │   ├── index.tsx
│   │   ├── App.tsx
│   │   └── components
│   │       └── Example.tsx
│   ├── public
│   │   └── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── Dockerfile
│   ├── .env.example
│   └── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── Makefile
└── README.md
```

## Requisitos

- Docker y Docker Compose instalados en tu máquina.
- Node.js y npm para el desarrollo local.

## Configuración

1. **Backend**: 
   - Navega al directorio `backend` y ejecuta `npm install` para instalar las dependencias.
   - Asegúrate de que el archivo `.env` esté configurado correctamente.

2. **Frontend**: 
   - Navega al directorio `frontend` y ejecuta `npm install` para instalar las dependencias.
   - Asegúrate de que el archivo `.env` esté configurado correctamente.

3. **Docker**:
   - Los Dockerfiles para el backend y el frontend están configurados para construir las imágenes necesarias.
   - El archivo `docker-compose.yml` orquesta ambos servicios.

## Ejecución

Para ejecutar la aplicación, utiliza el siguiente comando en la raíz del proyecto:

```bash
docker-compose up
```

Esto iniciará tanto el backend como el frontend en contenedores Docker.

## Pruebas

Realiza pruebas locales para asegurarte de que tanto el backend como el frontend funcionan correctamente antes de subir el proyecto al repositorio.

## Contribuciones

Si deseas contribuir a este proyecto, por favor abre un issue o un pull request en el repositorio.

## Licencia

Este proyecto está bajo la Licencia MIT.