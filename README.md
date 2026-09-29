# Arriendos: plataforma web de arriendo de inmuebles

Aplicación web desarrollada con **Django** y **PostgreSQL** para publicar, buscar y arrendar inmuebles. Fue mi proyecto final del bootcamp Fullstack Python de Desafío Latam.

## Funcionalidades

- Registro e inicio de sesión con dos roles: **arrendador** y **arrendatario**.
- Perfil de usuario editable.
- Publicación, edición y eliminación de inmuebles (arrendadores).
- Filtros de inmuebles por **región** y **comuna**.
- Flujo de arriendo que mantiene actualizada la disponibilidad de cada inmueble.
- Restricciones y transacciones a nivel de base de datos para evitar arriendos duplicados.
- Comandos de gestión para generar reportes (`reporte_regiones` y `reporte_comunas`).
- Pruebas automatizadas.

## Tecnologías

- Python y Django
- PostgreSQL 16
- HTML, CSS y Bootstrap 5
- Docker y Docker Compose

## Modelo de datos

Regiones, comunas, tipos de inmueble, inmuebles, arriendos y perfiles, en un modelo relacional en PostgreSQL.

## Cómo ejecutarlo

Requisitos: tener instalados [Docker](https://www.docker.com/) y Docker Compose.

1. Clonar el repositorio y entrar a la carpeta del proyecto:
   ```bash
   git clone https://github.com/AlvaroCS98/arriendos-django.git
   cd "arriendos-django/Presentación del proyecto"
   ```
2. Levantar los servicios. Al iniciar, se crean las tablas, se cargan regiones, comunas y usuarios de demostración, y se levanta el servidor:
   ```bash
   docker compose up --build
   ```
3. Abrir en el navegador: http://localhost:8001

## Usuarios de demostración

> Credenciales de prueba, solo para uso local.

| Rol          | Usuario                        | Contraseña   |
| ------------ | ------------------------------ | ------------ |
| Arrendador   | `arrendador1` / `arrendador2`  | `Demo12345!` |
| Arrendatario | `arrendatario1` / `arrendatario2` | `Demo12345!` |

## Reportes y pruebas

Con los servicios levantados, en otra terminal y dentro de la misma carpeta:

```bash
docker compose exec web python manage.py reporte_regiones
docker compose exec web python manage.py reporte_comunas
docker compose exec web python manage.py test
```

## Capturas de pantalla

![Nuevo inmueble](Presentaci%C3%B3n%20del%20proyecto/evidencias/Nuevo%20inmueble.png)
![Editando inmueble](Presentaci%C3%B3n%20del%20proyecto/evidencias/Editando%20inmueble.png)
![Inmueble editado](Presentaci%C3%B3n%20del%20proyecto/evidencias/Inmueble%20editado.png)
![Perfil de arrendador](Presentaci%C3%B3n%20del%20proyecto/evidencias/Perfil%20de%20arrendador.png)

## Seguridad

- La configuración incluida (`compose.yaml`) es **solo para desarrollo local**: usa modo depuración y una clave de ejemplo.
- Al publicar, el modo de depuración debe estar desactivado y la `SECRET_KEY` debe ir en variables de entorno.
- Las credenciales de demostración son solo para pruebas locales.

## Mejoras a futuro

- Ampliar las pruebas automatizadas (registro, inicio de sesión y edición de perfil).
- Desplegar la aplicación en un servicio compatible con Django para probarla en línea.

## Autor

**Álvaro Catalán**: estudiante de Desarrollo Fullstack Python en Desafío Latam.

- GitHub: [AlvaroCS98](https://github.com/AlvaroCS98)
- LinkedIn: [Álvaro Catalán](https://www.linkedin.com/in/%C3%A1lvaro-catal%C3%A1n-972547405/)
