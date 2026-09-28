from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import ProtectedError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from cuentas.models import Perfil

from .forms import InmuebleForm
from .models import Arriendo, Comuna, Inmueble, Region


def _perfil(request):
    perfil, _creado = Perfil.objects.get_or_create(usuario=request.user)
    return perfil


def _es_arrendador(request):
    """Solo los usuarios con Perfil.tipo_usuario == 'arrendador' pueden
    crear, editar o eliminar inmuebles."""
    return _perfil(request).tipo_usuario == Perfil.ARRENDADOR


def _es_arrendatario(request):
    """Solo los usuarios con Perfil.tipo_usuario == 'arrendatario' pueden arrendar."""
    return _perfil(request).tipo_usuario == Perfil.ARRENDATARIO


def _entero(valor):
    """Convierte un parámetro GET a int; si viene vacío o inválido devuelve None."""
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Hito 4: CRUD de inmuebles para el Arrendador
# ---------------------------------------------------------------------------
@login_required(login_url="cuentas:login")
def inmueble_crear(request):
    """
    Requerimiento 1 (Hito 4): página para que un Arrendador agregue un nuevo inmueble.
    1.a Ruta: 'inmuebles/nuevo/' (ver inmuebles/urls.py)
    1.b Objeto de formulario: InmuebleForm
    1.c Función para guardar el objeto: se asigna el propietario (usuario
        logueado) y se guarda con form.save().
    """
    if not _es_arrendador(request):
        messages.error(request, "Solo los Arrendadores pueden publicar inmuebles.")
        return redirect("cuentas:perfil")

    if request.method == "POST":
        form = InmuebleForm(request.POST)
        if form.is_valid():
            inmueble = form.save(commit=False)
            inmueble.propietario = request.user
            inmueble.save()
            messages.success(request, f'Inmueble "{inmueble.nombre}" publicado con éxito.')
            return redirect("cuentas:perfil")
    else:
        form = InmuebleForm()

    return render(request, "inmuebles/inmueble_form.html", {"form": form, "modo": "crear"})


@login_required(login_url="cuentas:login")
def inmueble_editar(request, pk):
    """
    Requerimiento 2 (Hito 4): página para que un Arrendador actualice un inmueble
    existente que le pertenece.
    2.a Ruta: 'inmuebles/<pk>/editar/'
    2.b Objeto de formulario en base al modelo: InmuebleForm(instance=inmueble)
    2.c Función para actualizar el objeto: form.save()
    """
    inmueble = get_object_or_404(Inmueble, pk=pk, propietario=request.user)

    if request.method == "POST":
        form = InmuebleForm(request.POST, instance=inmueble)
        if form.is_valid():
            form.save()
            messages.success(request, f'Inmueble "{inmueble.nombre}" actualizado con éxito.')
            return redirect("cuentas:perfil")
    else:
        form = InmuebleForm(instance=inmueble)

    return render(
        request,
        "inmuebles/inmueble_form.html",
        {"form": form, "modo": "editar", "inmueble": inmueble},
    )


@login_required(login_url="cuentas:login")
def inmueble_eliminar(request, pk):
    """
    Requerimiento 2 (Hito 4): permite además borrar un inmueble existente del
    Arrendador dueño. Se pide confirmación antes de eliminar.
    Hito 5: si el inmueble tiene arriendos registrados no se puede eliminar
    (el historial de arriendos se conserva).
    """
    inmueble = get_object_or_404(Inmueble, pk=pk, propietario=request.user)

    if request.method == "POST":
        nombre = inmueble.nombre
        try:
            inmueble.delete()
        except ProtectedError:
            messages.error(
                request,
                f'No se puede eliminar "{nombre}" porque tiene arriendos registrados.',
            )
            return redirect("cuentas:perfil")
        messages.success(request, f'Inmueble "{nombre}" eliminado.')
        return redirect("cuentas:perfil")

    return render(request, "inmuebles/inmueble_confirm_delete.html", {"inmueble": inmueble})


# ---------------------------------------------------------------------------
# Listado con filtros por región y comuna (Hito 4 req. 3 + Hito 5 req. 2)
# ---------------------------------------------------------------------------
@login_required(login_url="cuentas:login")
def inmueble_listar(request):
    """
    Página donde los Arrendatarios ven la oferta de inmuebles (todos los
    publicados por todos los Arrendadores).

    Hito 5, requerimiento 2: se puede filtrar por REGIÓN y por COMUNA.
      - ?region=<id>            -> inmuebles de esa región
      - ?comuna=<id>            -> inmuebles de esa comuna
      - ?region=<id>&comuna=<id> -> ambos filtros a la vez
    Cuando hay una región seleccionada, el selector de comunas muestra solo las
    comunas de esa región. Si la comuna recibida no pertenece a la región
    elegida, se ignora (así nunca queda un filtro contradictorio).
    """
    region_id = _entero(request.GET.get("region"))
    comuna_id = _entero(request.GET.get("comuna"))

    regiones = Region.objects.order_by("nombre")
    comunas = Comuna.objects.order_by("nombre")
    if region_id:
        comunas = comunas.filter(region_id=region_id)
        if comuna_id and not comunas.filter(pk=comuna_id).exists():
            comuna_id = None

    inmuebles = Inmueble.objects.select_related("comuna", "comuna__region", "tipo", "propietario").order_by(
        "comuna__region__nombre", "comuna__nombre", "nombre"
    )
    if region_id:
        inmuebles = inmuebles.filter(comuna__region_id=region_id)
    if comuna_id:
        inmuebles = inmuebles.filter(comuna_id=comuna_id)

    contexto = {
        "inmuebles": inmuebles,
        "regiones": regiones,
        "comunas": comunas,
        "region_seleccionada": region_id,
        "comuna_seleccionada": comuna_id,
        "puede_arrendar": _es_arrendatario(request),
    }
    return render(request, "inmuebles/inmueble_list.html", contexto)


# ---------------------------------------------------------------------------
# Hito 5: funcionalidad de arriendo
# ---------------------------------------------------------------------------
@login_required(login_url="cuentas:login")
@require_POST
def inmueble_arrendar(request, pk):
    """
    Un Arrendatario arrienda un inmueble disponible: se crea un Arriendo
    VIGENTE y el inmueble queda como no disponible.
    """
    if not _es_arrendatario(request):
        messages.error(request, "Solo los Arrendatarios pueden arrendar inmuebles.")
        return redirect("inmuebles:listar")

    with transaction.atomic():
        # select_for_update bloquea la fila para que dos personas no arrienden
        # el mismo inmueble al mismo tiempo.
        inmueble = get_object_or_404(Inmueble.objects.select_for_update(), pk=pk)
        if not inmueble.disponible:
            messages.error(request, f'"{inmueble.nombre}" ya no está disponible.')
            return redirect("inmuebles:listar")

        Arriendo.objects.create(inmueble=inmueble, arrendatario=request.user)
        inmueble.disponible = False
        inmueble.save(update_fields=["disponible"])

    messages.success(request, f'Arrendaste "{inmueble.nombre}" con éxito.')
    return redirect("inmuebles:mis_arriendos")


@login_required(login_url="cuentas:login")
def mis_arriendos(request):
    """
    Muestra los arriendos del usuario:
      - Arrendatario: los inmuebles que él arrienda (o arrendó).
      - Arrendador: los arriendos de sus inmuebles, con los datos de quien arrienda.
    """
    es_arrendador = _es_arrendador(request)

    if es_arrendador:
        arriendos = Arriendo.objects.filter(inmueble__propietario=request.user)
    else:
        arriendos = Arriendo.objects.filter(arrendatario=request.user)

    arriendos = arriendos.select_related(
        "inmueble",
        "inmueble__comuna",
        "inmueble__comuna__region",
        "inmueble__propietario",
        "arrendatario",
    )

    return render(
        request,
        "inmuebles/mis_arriendos.html",
        {"arriendos": arriendos, "es_arrendador": es_arrendador},
    )


@login_required(login_url="cuentas:login")
@require_POST
def arriendo_terminar(request, pk):
    """
    Termina un arriendo vigente. Pueden hacerlo el Arrendatario que arrienda
    o el Arrendador dueño del inmueble. El inmueble vuelve a estar disponible.
    """
    with transaction.atomic():
        arriendo = get_object_or_404(
            Arriendo.objects.select_for_update(),
            pk=pk,
            estado=Arriendo.Estado.VIGENTE,
        )
        inmueble = Inmueble.objects.select_for_update().get(pk=arriendo.inmueble_id)

        if request.user.pk not in (arriendo.arrendatario_id, inmueble.propietario_id):
            raise Http404("Arriendo no encontrado.")

        arriendo.estado = Arriendo.Estado.TERMINADO
        arriendo.fecha_termino = timezone.localdate()
        arriendo.save(update_fields=["estado", "fecha_termino"])

        inmueble.disponible = True
        inmueble.save(update_fields=["disponible"])

    messages.success(request, f'El arriendo de "{inmueble.nombre}" fue terminado.')
    return redirect("inmuebles:mis_arriendos")
