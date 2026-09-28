from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Perfil


class RegistroForm(UserCreationForm):
    """
    Formulario de registro (requerimiento 1.2).
    Extiende el formulario base de Django (usuario/clave/clave2) agregando
    los campos necesarios para crear también el Perfil (rol y telefono)
    y algunos datos personales del usuario (nombre, apellido, correo).
    """

    first_name = forms.CharField(label="Nombre", max_length=150, required=True)
    last_name = forms.CharField(label="Apellido", max_length=150, required=True)
    email = forms.EmailField(label="Correo electrónico", required=True)
    telefono = forms.CharField(label="Teléfono", max_length=20, required=False)
    tipo_usuario = forms.ChoiceField(
        label="Quiero registrarme como",
        choices=Perfil.TIPO_USUARIO_CHOICES,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "tipo_usuario",
            "telefono",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.first_name = self.cleaned_data["first_name"]
        usuario.last_name = self.cleaned_data["last_name"]
        usuario.email = self.cleaned_data["email"]
        if commit:
            usuario.save()
            Perfil.objects.create(
                usuario=usuario,
                tipo_usuario=self.cleaned_data["tipo_usuario"],
                telefono=self.cleaned_data["telefono"],
            )
        return usuario


class PerfilUsuarioForm(forms.ModelForm):
    """Datos del modelo User que el usuario puede modificar (requerimiento 2)."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
        }


class PerfilDatosForm(forms.ModelForm):
    """Datos del modelo Perfil que el usuario puede modificar (requerimiento 2)."""

    class Meta:
        model = Perfil
        fields = ["tipo_usuario", "telefono"]
        labels = {
            "tipo_usuario": "Tipo de usuario",
            "telefono": "Teléfono",
        }
