from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cuentas.models import Perfil

from .models import Arriendo, Comuna, Inmueble, Region, TipoInmueble

User = get_user_model()
CLAVE = "clave-de-prueba-123"


def crear_usuario(username, rol):
    usuario = User.objects.create_user(username=username, password=CLAVE)
    Perfil.objects.create(usuario=usuario, tipo_usuario=rol)
    return usuario


class DatosBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rm = Region.objects.create(nombre="Metropolitana de Santiago")
        cls.valpo = Region.objects.create(nombre="Valparaiso")
        cls.santiago = Comuna.objects.create(nombre="Santiago", region=cls.rm)
        cls.providencia = Comuna.objects.create(nombre="Providencia", region=cls.rm)
        cls.vina = Comuna.objects.create(nombre="Vina del Mar", region=cls.valpo)
        cls.casa = TipoInmueble.objects.create(nombre="Casa")

        cls.dueno = crear_usuario("dueno", Perfil.ARRENDADOR)
        cls.cliente = crear_usuario("cliente", Perfil.ARRENDATARIO)
        cls.otro = crear_usuario("otro", Perfil.ARRENDATARIO)

        cls.en_santiago = cls._inmueble("Casa Santiago", cls.santiago)
        cls.en_providencia = cls._inmueble("Casa Providencia", cls.providencia)
        cls.en_vina = cls._inmueble("Casa Vina", cls.vina)

    @classmethod
    def _inmueble(cls, nombre, comuna):
        return Inmueble.objects.create(
            nombre=nombre,
            descripcion="descripcion",
            comuna=comuna,
            tipo=cls.casa,
            propietario=cls.dueno,
        )


class FiltrosTests(DatosBase):
    def setUp(self):
        self.client.force_login(self.cliente)

    def nombres(self, **params):
        respuesta = self.client.get(reverse("inmuebles:listar"), params)
        self.assertEqual(respuesta.status_code, 200)
        return sorted(i.nombre for i in respuesta.context["inmuebles"])

    def test_sin_filtros_muestra_todo(self):
        self.assertEqual(self.nombres(), ["Casa Providencia", "Casa Santiago", "Casa Vina"])

    def test_filtra_por_region(self):
        self.assertEqual(self.nombres(region=self.valpo.pk), ["Casa Vina"])

    def test_filtra_por_comuna(self):
        self.assertEqual(self.nombres(comuna=self.providencia.pk), ["Casa Providencia"])

    def test_filtra_por_region_y_comuna(self):
        self.assertEqual(self.nombres(region=self.rm.pk, comuna=self.santiago.pk), ["Casa Santiago"])

    def test_comuna_de_otra_region_se_ignora(self):
        # Viña del Mar no pertenece a la región Metropolitana: solo cuenta la región.
        self.assertEqual(
            self.nombres(region=self.rm.pk, comuna=self.vina.pk),
            ["Casa Providencia", "Casa Santiago"],
        )

    def test_parametros_invalidos_no_rompen(self):
        self.assertEqual(len(self.nombres(region="abc", comuna="xyz")), 3)

    def test_anonimo_es_enviado_al_login(self):
        self.client.logout()
        respuesta = self.client.get(reverse("inmuebles:listar"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("cuentas:login"), respuesta["Location"])


class ArriendoTests(DatosBase):
    def test_arrendatario_puede_arrendar(self):
        self.client.force_login(self.cliente)
        respuesta = self.client.post(reverse("inmuebles:arrendar", args=[self.en_santiago.pk]))
        self.assertRedirects(respuesta, reverse("inmuebles:mis_arriendos"))

        self.en_santiago.refresh_from_db()
        self.assertFalse(self.en_santiago.disponible)
        arriendo = Arriendo.objects.get(inmueble=self.en_santiago)
        self.assertEqual(arriendo.arrendatario, self.cliente)
        self.assertEqual(arriendo.estado, Arriendo.Estado.VIGENTE)

    def test_no_se_puede_arrendar_dos_veces(self):
        self.client.force_login(self.cliente)
        self.client.post(reverse("inmuebles:arrendar", args=[self.en_santiago.pk]))
        self.client.force_login(self.otro)
        self.client.post(reverse("inmuebles:arrendar", args=[self.en_santiago.pk]))
        self.assertEqual(Arriendo.objects.filter(inmueble=self.en_santiago).count(), 1)

    def test_arrendador_no_puede_arrendar(self):
        self.client.force_login(self.dueno)
        self.client.post(reverse("inmuebles:arrendar", args=[self.en_santiago.pk]))
        self.assertFalse(Arriendo.objects.exists())

    def test_arrendar_requiere_post(self):
        self.client.force_login(self.cliente)
        respuesta = self.client.get(reverse("inmuebles:arrendar", args=[self.en_santiago.pk]))
        self.assertEqual(respuesta.status_code, 405)

    def test_terminar_arriendo_libera_el_inmueble(self):
        self.client.force_login(self.cliente)
        self.client.post(reverse("inmuebles:arrendar", args=[self.en_santiago.pk]))
        arriendo = Arriendo.objects.get(inmueble=self.en_santiago)

        self.client.post(reverse("inmuebles:terminar_arriendo", args=[arriendo.pk]))

        arriendo.refresh_from_db()
        self.en_santiago.refresh_from_db()
        self.assertEqual(arriendo.estado, Arriendo.Estado.TERMINADO)
        self.assertIsNotNone(arriendo.fecha_termino)
        self.assertTrue(self.en_santiago.disponible)

    def test_tercero_no_puede_terminar_un_arriendo_ajeno(self):
        self.client.force_login(self.cliente)
        self.client.post(reverse("inmuebles:arrendar", args=[self.en_santiago.pk]))
        arriendo = Arriendo.objects.get(inmueble=self.en_santiago)

        self.client.force_login(self.otro)
        respuesta = self.client.post(reverse("inmuebles:terminar_arriendo", args=[arriendo.pk]))
        self.assertEqual(respuesta.status_code, 404)
        arriendo.refresh_from_db()
        self.assertEqual(arriendo.estado, Arriendo.Estado.VIGENTE)

    def test_arrendador_ve_quien_arrienda_sus_inmuebles(self):
        self.client.force_login(self.cliente)
        self.client.post(reverse("inmuebles:arrendar", args=[self.en_santiago.pk]))

        self.client.force_login(self.dueno)
        respuesta = self.client.get(reverse("inmuebles:mis_arriendos"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "cliente")

    def test_no_se_puede_eliminar_inmueble_con_arriendos(self):
        self.client.force_login(self.cliente)
        self.client.post(reverse("inmuebles:arrendar", args=[self.en_santiago.pk]))

        self.client.force_login(self.dueno)
        self.client.post(reverse("inmuebles:eliminar", args=[self.en_santiago.pk]))
        self.assertTrue(Inmueble.objects.filter(pk=self.en_santiago.pk).exists())


class CrudArrendadorTests(DatosBase):
    def test_arrendador_publica_un_inmueble(self):
        self.client.force_login(self.dueno)
        respuesta = self.client.post(
            reverse("inmuebles:crear"),
            {"nombre": "Nuevo", "descripcion": "algo", "comuna": self.santiago.pk, "tipo": self.casa.pk},
        )
        self.assertRedirects(respuesta, reverse("cuentas:perfil"))
        nuevo = Inmueble.objects.get(nombre="Nuevo")
        self.assertEqual(nuevo.propietario, self.dueno)
        self.assertTrue(nuevo.disponible)

    def test_arrendatario_no_puede_publicar(self):
        self.client.force_login(self.cliente)
        self.client.post(
            reverse("inmuebles:crear"),
            {"nombre": "Nuevo", "descripcion": "algo", "comuna": self.santiago.pk, "tipo": self.casa.pk},
        )
        self.assertFalse(Inmueble.objects.filter(nombre="Nuevo").exists())
