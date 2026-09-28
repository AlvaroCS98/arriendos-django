from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("cuentas/", include("cuentas.urls")),
    path("inmuebles/", include("inmuebles.urls")),
    # Requerimiento 1.3: redireccionamiento de urls.
    # La raíz del sitio redirige a la página personal de perfil; si el
    # usuario no ha iniciado sesión, @login_required lo redirige a /cuentas/login/.
    path(
        "",
        login_required(RedirectView.as_view(pattern_name="cuentas:perfil"), login_url="cuentas:login"),
        name="inicio",
    ),
]
