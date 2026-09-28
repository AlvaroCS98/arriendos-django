from django.contrib import admin

from .models import Arriendo, Comuna, Inmueble, Region, TipoInmueble

admin.site.register(Region)
admin.site.register(Comuna)
admin.site.register(TipoInmueble)


@admin.register(Inmueble)
class InmuebleAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "comuna", "propietario", "disponible")
    list_filter = ("disponible", "tipo", "comuna__region")
    search_fields = ("nombre", "descripcion", "comuna__nombre")


@admin.register(Arriendo)
class ArriendoAdmin(admin.ModelAdmin):
    list_display = ("inmueble", "arrendatario", "fecha_inicio", "fecha_termino", "estado")
    list_filter = ("estado",)
    search_fields = ("inmueble__nombre", "arrendatario__username")
