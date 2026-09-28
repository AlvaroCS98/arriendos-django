"""
Requerimiento 3 del Hito 3:
Consultar listado de inmuebles para arriendo separado por regiones,
conectando a la DB tanto con el ORM de Django como con SQL directo,
guardando el resultado en un archivo de texto.

Uso:
    python manage.py reporte_regiones
"""
from django.core.management.base import BaseCommand
from django.db import connection

from inmuebles.models import Region


class Command(BaseCommand):
    help = "Genera un reporte de inmuebles agrupados por región (ORM y SQL)."

    def handle(self, *args, **options):
        lineas = []
        lineas.append("REPORTE DE INMUEBLES POR REGIÓN")
        lineas.append("=" * 60)

        # --- Parte 1: usando el ORM de Django ---
        lineas.append("")
        lineas.append("--- Consulta usando el ORM de Django ---")
        regiones = Region.objects.filter(comunas__inmuebles__isnull=False).distinct().order_by("nombre")
        for region in regiones:
            lineas.append("")
            lineas.append(f"Región: {region.nombre}")
            for comuna in region.comunas.filter(inmuebles__isnull=False).distinct().order_by("nombre"):
                for inmueble in comuna.inmuebles.all().order_by("nombre"):
                    lineas.append(f"  - [{comuna.nombre}] {inmueble.nombre}: {inmueble.descripcion}")

        # --- Parte 2: usando SQL directo ---
        lineas.append("")
        lineas.append("")
        lineas.append("--- Consulta usando SQL directo ---")
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT r.nombre AS region, c.nombre AS comuna,
                       i.nombre AS nombre, i.descripcion AS descripcion
                FROM inmuebles_inmueble i
                INNER JOIN inmuebles_comuna c ON i.comuna_id = c.id
                INNER JOIN inmuebles_region r ON c.region_id = r.id
                ORDER BY r.nombre, c.nombre, i.nombre
                """
            )
            filas = cursor.fetchall()

        region_actual = None
        for region_nombre, comuna_nombre, nombre, descripcion in filas:
            if region_nombre != region_actual:
                lineas.append("")
                lineas.append(f"Región: {region_nombre}")
                region_actual = region_nombre
            lineas.append(f"  - [{comuna_nombre}] {nombre}: {descripcion}")

        contenido = "\n".join(lineas)
        with open("reporte_regiones.txt", "w", encoding="utf-8") as f:
            f.write(contenido)

        self.stdout.write(self.style.SUCCESS("Reporte generado en reporte_regiones.txt"))
