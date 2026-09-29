# Arriendos: plataforma web de arriendo de inmuebles

Aplicación web desarrollada con **Django** y **PostgreSQL** para publicar, buscar y arrendar inmuebles. Fue mi proyecto final del bootcamp Fullstack Python de Desafío Latam.

## Funcionalidades

- Registro e inicio de sesión con dos roles: **arrendador** y **arrendatario**.
- Perfil de usuario editable.
- Publicación, edición y eliminación de inmuebles (arrendadores).
- Filtros de inmuebles por **región** y **comuna**.
- Flujo de arriendo que mantiene actualizada la disponibilidad de cada inmueble.
- Restricciones y transacciones a nivel de base de datos para evitar arriendos duplicados.
- Comandos de gestión para generar reportes.
- Pruebas automatizadas.

## Tecnologías

- Python y Django
- PostgreSQL
- HTML, CSS y Bootstrap 5
- Docker y Docker Compose

## Modelo de datos

Regiones, comunas, tipos de inmueble, inmuebles, arriendos y perfiles, en un modelo relacional en PostgreSQL.

## Cómo ejecutarlo

Requisitos: tener instalados [Docker](https://www.docker.com/) y Docker Compose.

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/AlvaroCS98/arriendos-django.git
   cd arriendos-django
   ```
2. Crear el archivo de variables de entorno (**COMPLETAR**: copiar tu `.env.example` o indicar las variables necesarias):
   ```bash
   cp .env.example .env
   ```
3. Levantar los servicios (**COMPLETAR** si tu comando es distinto):
   ```bash
   docker compose up --build
   ```
4. Abrir en el navegador: http://localhost:8000 (**COMPLETAR** si usas otro puerto).

## Usuarios de demostración

> Credenciales de prueba, solo para uso local.

| Rol          | Usuario        | Contraseña     |
| ------------ | -------------- | -------------- |
| Arrendador   | **COMPLETAR**  | **COMPLETAR**  |
| Arrendatario | **COMPLETAR**  | **COMPLETAR**  |

## Pruebas

```bash
docker compose exec web python manage.py test
```
(**COMPLETAR** con el nombre real de tu servicio si no es `web`.)

## Capturas de pantalla

<!-- COMPLETAR: reemplazar por los nombres reales de los archivos de la carpeta evidencias -->
![Listado de inmuebles](evidencias/NOMBRE_DE_LA_CAPTURA.png)
![Perfil de usuario](evidencias/NOMBRE_DE_LA_CAPTURA.png)

## Seguridad

- El modo de depuración debe estar desactivado y la `SECRET_KEY` en variables de entorno al publicar.
- Las credenciales de demostración son solo para pruebas locales.

## Mejoras a futuro

- Ampliar las pruebas automatizadas (registro, inicio de sesión y edición de perfil).
- Desplegar la aplicación en un servicio compatible con Django para probarla en línea.

## Autor

**Álvaro Catalán**: estudiante de Desarrollo Fullstack Python en Desafío Latam.

- GitHub: [AlvaroCS98](https://github.com/AlvaroCS98)
- LinkedIn: [Álvaro Catalán](https://www.linkedin.com/in/%C3%A1lvaro-catal%C3%A1n-972547405/)
- Correo: alvarocatalans98@gmail.com
