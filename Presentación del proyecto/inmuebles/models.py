from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Region(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Comuna(models.Model):
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="comunas")

    def __str__(self):
        return self.nombre


class TipoInmueble(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class Inmueble(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE, related_name="inmuebles")
    tipo = models.ForeignKey(TipoInmueble, on_delete=models.CASCADE, related_name="inmuebles")
    propietario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inmuebles")
    # Hito 5: pasa a False cuando un Arrendatario lo arrienda y vuelve a True
    # cuando el arriendo termina. No se edita a mano en el formulario.
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Arriendo(models.Model):
    """
    Hito 5: registro de que un Arrendatario arrienda un Inmueble.
    Mientras el arriendo está VIGENTE, el inmueble queda como no disponible.
    """

    class Estado(models.TextChoices):
        VIGENTE = "VIGENTE", "Vigente"
        TERMINADO = "TERMINADO", "Terminado"

    inmueble = models.ForeignKey(Inmueble, on_delete=models.PROTECT, related_name="arriendos")
    arrendatario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="arriendos")
    fecha_inicio = models.DateField(default=timezone.localdate)
    fecha_termino = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.VIGENTE)

    class Meta:
        ordering = ["-fecha_inicio", "-id"]
        constraints = [
            # A nivel de base de datos: un inmueble no puede tener dos arriendos vigentes.
            models.UniqueConstraint(
                fields=["inmueble"],
                condition=Q(estado="VIGENTE"),
                name="un_arriendo_vigente_por_inmueble",
            ),
        ]

    def __str__(self):
        return f"{self.arrendatario.username} → {self.inmueble.nombre} ({self.get_estado_display()})"
