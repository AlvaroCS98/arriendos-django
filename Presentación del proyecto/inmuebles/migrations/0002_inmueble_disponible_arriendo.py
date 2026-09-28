import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inmuebles", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="inmueble",
            name="disponible",
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name="Arriendo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha_inicio", models.DateField(default=django.utils.timezone.localdate)),
                ("fecha_termino", models.DateField(blank=True, null=True)),
                (
                    "estado",
                    models.CharField(
                        choices=[("VIGENTE", "Vigente"), ("TERMINADO", "Terminado")],
                        default="VIGENTE",
                        max_length=10,
                    ),
                ),
                (
                    "arrendatario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="arriendos",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inmueble",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="arriendos",
                        to="inmuebles.inmueble",
                    ),
                ),
            ],
            options={
                "ordering": ["-fecha_inicio", "-id"],
            },
        ),
        migrations.AddConstraint(
            model_name="arriendo",
            constraint=models.UniqueConstraint(
                condition=models.Q(("estado", "VIGENTE")),
                fields=("inmueble",),
                name="un_arriendo_vigente_por_inmueble",
            ),
        ),
    ]
