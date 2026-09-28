"""
Requerimiento 2 del Hito 3:
Consultar listado de inmuebles para arriendo separado por comunas,
usando solo los campos "nombre" y "descripcion", conectando a la DB
tanto con el ORM de Django como con SQL directo, y guardando el
resultado en un archivo de texto.

Uso:
    python manage.py reporte_comunas
"""
from django.core.management.base import BaseCommand
from django.db import connection

from inmuebles.models import Comuna


class Command(BaseCommand):
    help = "Genera un reporte de inmuebles agrupados por comuna (ORM y SQL)."

    def handle(self, *args, **options):
        lineas = []
        lineas.append("REPORTE DE INMUEBLES POR COMUNA")
        lineas.append("=" * 60)

        # --- Parte 1: usando el ORM de Django ---
        lineas.append("")
        lineas.append("--- Consulta usando el ORM de Django ---")
        comunas = Comuna.objects.filter(inmuebles__isnull=False).distinct().order_by("nombre")
        for comuna in comunas:
            lineas.append("")
            lineas.append(f"Comuna: {comuna.nombre}")
            for inmueble in comuna.inmuebles.all().order_by("nombre"):
                lineas.append(f"  - {inmueble.nombre}: {inmueble.descripcion}")

        # --- Parte 2: usando SQL directo ---
        lineas.append("")
        lineas.append("")
        lineas.append("--- Consulta usando SQL directo ---")
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT c.nombre AS comuna, i.nombre AS nombre, i.descripcion AS descripcion
                FROM inmuebles_inmueble i
                INNER JOIN inmuebles_comuna c ON i.comuna_id = c.id
                ORDER BY c.nombre, i.nombre
                """
            )
            filas = cursor.fetchall()

        comuna_actual = None
        for comuna_nombre, nombre, descripcion in filas:
            if comuna_nombre != comuna_actual:
                lineas.append("")
                lineas.append(f"Comuna: {comuna_nombre}")
                comuna_actual = comuna_nombre
            lineas.append(f"  - {nombre}: {descripcion}")

        contenido = "\n".join(lineas)
        with open("reporte_comunas.txt", "w", encoding="utf-8") as f:
            f.write(contenido)

        self.stdout.write(self.style.SUCCESS("Reporte generado en reporte_comunas.txt"))
