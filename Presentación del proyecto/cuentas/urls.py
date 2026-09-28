from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "cuentas"

urlpatterns = [
    # Requerimiento 1.1: vista de login (se usa la vista genérica de Django,
    # solo se personaliza el template).
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="cuentas/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="cuentas:login"),
        name="logout",
    ),
    # Requerimiento 1.2: vista de registro.
    path("registro/", views.registro_view, name="registro"),
    # Requerimiento 1.4: página personal de perfil.
    path("perfil/", views.perfil_view, name="perfil"),
    # Requerimiento 2: modificar datos personales.
    path("perfil/editar/", views.perfil_editar_view, name="perfil_editar"),
]
