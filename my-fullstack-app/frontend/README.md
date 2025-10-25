# Frontend Documentation

Este es el proyecto frontend de la aplicación de pila completa. A continuación se detallan los aspectos más importantes del proyecto.

## Estructura del Proyecto

La estructura del proyecto frontend es la siguiente:

```
frontend
├── src
│   ├── index.tsx         # Punto de entrada de la aplicación
│   ├── App.tsx           # Componente principal de la aplicación
│   └── components
│       └── Example.tsx   # Componente de ejemplo
├── public
│   └── index.html        # Plantilla HTML principal
├── package.json           # Configuración de npm
├── tsconfig.json         # Configuración de TypeScript
├── Dockerfile             # Instrucciones para construir la imagen Docker
└── .env.example           # Ejemplo de variables de entorno
```

## Instalación

Para instalar las dependencias del proyecto, ejecuta el siguiente comando en la raíz del directorio `frontend`:

```
npm install
```

## Ejecución

Para ejecutar la aplicación en modo de desarrollo, utiliza el siguiente comando:

```
npm start
```

Esto iniciará la aplicación y podrás acceder a ella en `http://localhost:3000`.

## Docker

Para construir y ejecutar la aplicación utilizando Docker, asegúrate de tener Docker instalado y ejecuta:

```
docker-compose up --build
```

Esto construirá la imagen Docker y levantará el contenedor.

## Variables de Entorno

Asegúrate de crear un archivo `.env` basado en el archivo `.env.example` y de definir las variables de entorno necesarias para la aplicación.

## Pruebas

Realiza pruebas locales para asegurarte de que la aplicación funcione correctamente antes de subirla al repositorio.

## Contribuciones

Si deseas contribuir a este proyecto, por favor abre un issue o envía un pull request. Agradecemos cualquier ayuda para mejorar la aplicación.