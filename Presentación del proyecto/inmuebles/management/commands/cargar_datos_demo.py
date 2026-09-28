"""
Carga datos de demostración para el Hito 5 (se puede ejecutar varias veces sin duplicar):

  - Regiones, comunas y tipos de inmueble (fixtures del Hito 4).
  - Usuarios de prueba con contraseña conocida (2 arrendadores y 2 arrendatarios).
  - Un superusuario para entrar a /admin.
  - 10 inmuebles publicados por los arrendadores, repartidos en varias regiones.

Uso:
    python manage.py cargar_datos_demo
"""
import os

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

from cuentas.models import Perfil
from inmuebles.models import Inmueble

PASSWORD_DEMO = "Demo12345!"

# (usuario, nombre, apellido, correo, teléfono, rol)
USUARIOS_DEMO = [
    ("arrendador1", "Ana", "Rojas", "ana.rojas@example.com", "+56 9 1111 1111", Perfil.ARRENDADOR),
    ("arrendador2", "Luis", "Soto", "luis.soto@example.com", "+56 9 2222 2222", Perfil.ARRENDADOR),
    ("arrendatario1", "Carla", "Mena", "carla.mena@example.com", "+56 9 3333 3333", Perfil.ARRENDATARIO),
    ("arrendatario2", "Diego", "Pino", "diego.pino@example.com", "+56 9 4444 4444", Perfil.ARRENDATARIO),
]

# (nombre, descripción, id_comuna, id_tipo, usuario propietario)
# Los ids de comuna y tipo vienen de los fixtures regiones_comunas.json y tipos_inmueble.json.
INMUEBLES_DEMO = [
    ("Casa Los Aromos", "Casa de 3 dormitorios con patio amplio, cerca del centro.", 131, 1, "arrendador1"),  # Santiago
    ("Depto Torre Central", "Departamento de 2 dormitorios, edificio con piscina y gimnasio.", 131, 2, "arrendador2"),  # Santiago
    ("Oficina Providencia Norte", "Oficina amoblada, ideal para equipos pequeños, cerca del metro.", 118, 3, "arrendador1"),  # Providencia
    ("Local Ñuñoa Plaza", "Local comercial en esquina de alto tránsito peatonal.", 111, 4, "arrendador2"),  # Ñuñoa
    ("Depto Las Condes Vista", "Departamento con vista a la cordillera, 1 dormitorio.", 103, 2, "arrendador2"),  # Las Condes
    ("Casa Cerro Alegre", "Casa patrimonial remodelada, cerca de los ascensores.", 79, 1, "arrendador1"),  # Valparaíso
    ("Depto Frente al Mar", "Departamento con vista al mar, 2 dormitorios, estacionamiento.", 81, 2, "arrendador2"),  # Viña del Mar
    ("Parcela Valle Verde", "Parcela de agrado con casa principal y quincho.", 36, 5, "arrendador2"),  # La Serena
    ("Casa Barrio Universitario", "Casa de 4 dormitorios cerca de universidades, ideal grupo.", 225, 1, "arrendador2"),  # Concepción
    ("Oficina Centro Concepción", "Oficina en edificio corporativo, sala de reuniones incluida.", 225, 3, "arrendador1"),  # Concepción
]


class Command(BaseCommand):
    help = "Carga regiones/comunas, usuarios de prueba e inmuebles de demostración."

    def handle(self, *args, **options):
        call_command("loaddata", "regiones_comunas", "tipos_inmueble", verbosity=0)

        User = get_user_model()

        usuarios = {}
        for username, nombre, apellido, correo, telefono, rol in USUARIOS_DEMO:
            usuario, creado = User.objects.get_or_create(
                username=username,
                defaults={"first_name": nombre, "last_name": apellido, "email": correo},
            )
            if creado:
                usuario.set_password(PASSWORD_DEMO)
                usuario.save()
            Perfil.objects.get_or_create(
                usuario=usuario,
                defaults={"tipo_usuario": rol, "telefono": telefono},
            )
            usuarios[username] = usuario

        admin_usuario = os.getenv("DEMO_ADMIN_USER", "admin")
        admin_clave = os.getenv("DEMO_ADMIN_PASSWORD", "admin12345")
        if not User.objects.filter(username=admin_usuario).exists():
            User.objects.create_superuser(
                username=admin_usuario,
                email="admin@example.com",
                password=admin_clave,
            )

        creados = 0
        for nombre, descripcion, comuna_id, tipo_id, username in INMUEBLES_DEMO:
            _inmueble, creado = Inmueble.objects.get_or_create(
                nombre=nombre,
                propietario=usuarios[username],
                defaults={"descripcion": descripcion, "comuna_id": comuna_id, "tipo_id": tipo_id},
            )
            if creado:
                creados += 1

        self.stdout.write(self.style.SUCCESS(f"Datos de demo listos ({creados} inmuebles nuevos)."))
        self.stdout.write(f"  Arrendadores:   arrendador1 / arrendador2   (clave: {PASSWORD_DEMO})")
        self.stdout.write(f"  Arrendatarios:  arrendatario1 / arrendatario2   (clave: {PASSWORD_DEMO})")
        self.stdout.write(f"  Administrador:  {admin_usuario} / {admin_clave}   (solo para /admin)")
