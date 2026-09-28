from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from inmuebles.models import Inmueble

from .forms import PerfilDatosForm, PerfilUsuarioForm, RegistroForm
from .models import Perfil


def registro_view(request):
    """
    Requerimiento 1.2: vista de registro.
    Crea el User y su Perfil (Arrendador/Arrendatario), inicia sesion
    automaticamente y redirige a la pagina personal (requerimiento 1.3).
    """
    if request.user.is_authenticated:
        return redirect("cuentas:perfil")

    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            auth_login(request, usuario)
            messages.success(request, "¡Cuenta creada con éxito! Bienvenido/a.")
            return redirect("cuentas:perfil")
    else:
        form = RegistroForm()

    return render(request, "cuentas/registro.html", {"form": form})


@login_required(login_url="cuentas:login")
def perfil_view(request):
    """
    Requerimientos 1.1/1.4: pagina personal de perfil para Arrendatarios y
    Arrendadores, desplegando los datos del usuario. Si es Arrendador,
    ademas se listan los inmuebles que administra.
    """
    perfil, _creado = Perfil.objects.get_or_create(usuario=request.user)

    inmuebles = None
    if perfil.tipo_usuario == Perfil.ARRENDADOR:
        inmuebles = (
            Inmueble.objects.filter(propietario=request.user)
            .select_related("comuna", "comuna__region", "tipo")
            .order_by("nombre")
        )

    contexto = {
        "perfil": perfil,
        "inmuebles": inmuebles,
    }
    return render(request, "cuentas/perfil.html", contexto)


@login_required(login_url="cuentas:login")
def perfil_editar_view(request):
    """
    Requerimiento 2: permite a un Arrendatario o Arrendador modificar sus
    datos personales (nombre, apellido, correo, telefono y tipo de usuario).
    """
    perfil, _creado = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == "POST":
        usuario_form = PerfilUsuarioForm(request.POST, instance=request.user)
        perfil_form = PerfilDatosForm(request.POST, instance=perfil)
        if usuario_form.is_valid() and perfil_form.is_valid():
            usuario_form.save()
            perfil_form.save()
            messages.success(request, "Tus datos se actualizaron correctamente.")
            return redirect("cuentas:perfil")
    else:
        usuario_form = PerfilUsuarioForm(instance=request.user)
        perfil_form = PerfilDatosForm(instance=perfil)

    contexto = {
        "usuario_form": usuario_form,
        "perfil_form": perfil_form,
    }
    return render(request, "cuentas/perfil_editar.html", contexto)
