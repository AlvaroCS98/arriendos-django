from django.urls import path

from . import views

app_name = "inmuebles"

urlpatterns = [
    # Listado de inmuebles con filtros por región y comuna.
    path("", views.inmueble_listar, name="listar"),
    # Hito 4, req. 1.a: agregar un nuevo inmueble.
    path("nuevo/", views.inmueble_crear, name="crear"),
    # Hito 4, req. 2.a: actualizar / eliminar un inmueble existente.
    path("<int:pk>/editar/", views.inmueble_editar, name="editar"),
    path("<int:pk>/eliminar/", views.inmueble_eliminar, name="eliminar"),
    # Hito 5: funcionalidad de arriendo.
    path("<int:pk>/arrendar/", views.inmueble_arrendar, name="arrendar"),
    path("arriendos/", views.mis_arriendos, name="mis_arriendos"),
    path("arriendos/<int:pk>/terminar/", views.arriendo_terminar, name="terminar_arriendo"),
]
