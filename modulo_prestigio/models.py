from django.db import models

from modulo_usuarios.models import PerfilEstudiante


class HitoSuscripcionOtorgado(models.Model):
	publicador = models.ForeignKey(
		PerfilEstudiante,
		on_delete=models.CASCADE,
		related_name="hitos_suscripcion_otorgados",
	)
	hito = models.PositiveIntegerField()
	puntos_otorgados = models.PositiveIntegerField()
	otorgado_en = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=["publicador", "hito"],
				name="unique_hito_suscripcion_por_publicador",
			)
		]

	def __str__(self):
		return f"{self.publicador.usuario.username}: hito {self.hito} (+{self.puntos_otorgados})"
