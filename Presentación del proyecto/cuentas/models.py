from django.conf import settings
from django.db import models


class Perfil(models.Model):
    """
    Datos adicionales del usuario que no vienen en auth.User:
    el rol dentro de la plataforma (Arrendador / Arrendatario) y el
    telefono de contacto. Se relaciona 1 a 1 con el usuario de Django.
    """

    ARRENDADOR = "arrendador"
    ARRENDATARIO = "arrendatario"
    TIPO_USUARIO_CHOICES = [
        (ARRENDADOR, "Arrendador"),
        (ARRENDATARIO, "Arrendatario"),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default=ARRENDATARIO,
    )
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.usuario.username} ({self.get_tipo_usuario_display()})"
