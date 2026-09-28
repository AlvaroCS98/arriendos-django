from django import forms

from .models import Comuna, Inmueble


class InmuebleForm(forms.ModelForm):
    """
    Objeto de formulario basado en el modelo Inmueble (requerimientos 1.b y 2.b del Hito 4).
    El campo "propietario" NO se incluye aquí: se asigna automáticamente
    en la vista con el usuario (Arrendador) que tiene la sesión iniciada,
    para que un usuario no pueda crear/editar inmuebles a nombre de otro.
    Tampoco se incluye "disponible": lo controla el flujo de arriendo (Hito 5).
    """

    class Meta:
        model = Inmueble
        fields = ["nombre", "descripcion", "comuna", "tipo"]
        labels = {
            "nombre": "Nombre del inmueble",
            "descripcion": "Descripción",
            "comuna": "Comuna",
            "tipo": "Tipo de inmueble",
        }
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hay más de 300 comunas: se ordenan por región y se muestra la región
        # entre paréntesis para que sea fácil encontrar la correcta.
        self.fields["comuna"].queryset = Comuna.objects.select_related("region").order_by(
            "region__nombre", "nombre"
        )
        self.fields["comuna"].label_from_instance = lambda comuna: f"{comuna.nombre} ({comuna.region.nombre})"
