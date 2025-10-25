# Backend Documentation

Este es el backend de la aplicación `my-fullstack-app`. A continuación se detallan los componentes y cómo configurar y ejecutar el proyecto.

## Estructura del Proyecto

- **src/**: Contiene el código fuente de la aplicación.
  - **index.ts**: Punto de entrada de la aplicación. Inicializa el servidor y configura middleware y rutas.
  - **controllers/**: Contiene los controladores que manejan la lógica de negocio.
    - **exampleController.ts**: Controlador de ejemplo que maneja las solicitudes relacionadas con el ejemplo.
  - **routes/**: Define las rutas de la aplicación.
    - **index.ts**: Configura las rutas utilizando `ExampleController`.
  - **config/**: Contiene la configuración de la aplicación, como la conexión a la base de datos.

## Requisitos

- Node.js
- TypeScript
- Docker (opcional, para ejecutar en contenedor)

## Instalación

1. Clona el repositorio:
   ```
   git clone <url-del-repositorio>
   cd my-fullstack-app/backend
   ```

2. Instala las dependencias:
   ```
   npm install
   ```

3. Configura las variables de entorno:
   - Copia el archivo `.env.example` a `.env` y ajusta los valores según sea necesario.

## Ejecución

Para ejecutar el backend localmente, utiliza el siguiente comando:
```
npm start
```

## Docker

Para construir y ejecutar el backend en un contenedor Docker, utiliza los siguientes comandos:

1. Construir la imagen:
   ```
   docker build -t my-backend .
   ```

2. Ejecutar el contenedor:
   ```
   docker run -p 3000:3000 --env-file .env my-backend
   ```

## Pruebas

Asegúrate de realizar pruebas locales para verificar que el backend funcione correctamente antes de subir el proyecto al repositorio.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o un pull request para discutir cambios.

## Licencia

Este proyecto está bajo la Licencia MIT.