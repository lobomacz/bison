from django.db import models
from django.urls import reverse

# Create your models here.
class Cuenta(models.Model):
	"""Modelo de datos para Cuentas"""
	cuenta = models.CharField(max_length=25, primary_key=True)
	descripcion = models.CharField(max_length=200)
	cuenta_padre = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
	nivel = models.CharField(choices=[('C', 'Cuenta'), ('S', 'Subcuenta'), ('D', 'Detalle')])
	resumen = models.BooleanField()
	cerrada = models.BooleanField()

	class Meta:
		ordering = ['cuenta', 'cuenta_padre']
		verbose_name = 'Cuenta Contable'
		verbose_name_plural = 'Cuentas Contables'
		permissions = [
			('cerrar_cuenta', 'Cerrar cuentas contables'),
		]
		indexes = [
			models.Index(fields=['cuenta_padre'])
		]

	def __str__(self):
		return self.cuenta

	def get_absolute_url(self):
		return reverse('vDetalleCuenta', {'_id':self.cuenta})

class Asiento(models.Model):
	"""Modelo de datos para Asientos"""
	fecha = models.DateField()
	descripcion = models.CharField(max_length=200)
	referencia = models.CharField(max_length=25)
	contabilizado = models.BooleanField()
	fecha_contabilizado = models.DateTimeField(null=True)
	anulado = models.BooleanField()
	fecha_anulado = models.DateTimeField(null=True)
	observaciones = models.CharField(max_length=400)

	class Meta:
		ordering = ['id', 'fecha']
		verbose_name = 'Asiento Contable'
		verbose_name_plural = 'Asientos Contables'
		indexes = [
			models.Index(fields=['referencia'])
		]
		permissions = [
			('contabilizar_asiento', 'Contabilizar Asientos'),
			('anular_asiento', 'Anular Asiento Contable'),
		]

	def __str__(self):
		return "%s - %s" % (self.id, self.descripcion)

	def get_absolute_url(self):
		return reverse('vVerAsiento', {'_id':self.id})


class DetalleAsiento(models.Model):
	"""Modelo de datos para DetalleAsiento"""
	asiento = models.ForeignKey(Asiento, on_delete=models.CASCADE)
	cuenta = models.ForeignKey(Cuenta, on_delete=models.PROTECT)
	movimiento = models.CharField(choices=[('db', 'Débito'), ('cr', 'Crédito')], max_length=2)
	monto = models.DecimalField(max_digits=6, decimal_places=2)

	class Meta:
		ordering = ['cuenta', 'movimiento']
		verbose_name = 'Detalle de Asiento'
		unique_together = ['asiento', 'cuenta']
		index_together = ['asiento', 'cuenta']


class Ejercicio(models.Model):
	""" Modelo de datos para Ejercicios Contables """
	ejercicio = models.CharField(max_length=4, min_length=4, primary_key=True)
	descripcion = models.CharField(max_length=200)
	activo = models.BooleanField(default=False)

	class Meta:
		ordering = ['ejercicio']
		verbose_name = 'Ejercicio Contable'
		verbose_name_plural = 'Ejercicios Contables'

	def get_absolute_url(self):
		return reverse('vDetalleEjercicio', {'_id':self.ejercicio})

	def __str__(self):
		return self.ejercicio


class Periodo(models.Model):
	"""Modelo de datos para PeriodoContable"""
	ejercicio = models.ForeignKey(Ejercicio, on_delete=models.PROTECT, on_update=models.CASCADE)
	nombre = models.CharField(max_length=15)
	nombre_corto = models.CharField(max_length=3, min_length=3)
	fecha_inicio = models.DateField('Fecha de Inicio')
	fecha_final = models.DateField('Fecha Final')
	activo = models.BooleanField(default=False)
	cerrado = models.BooleanField(default=False)

	class Meta:
		ordering = ['ejercicio', 'fecha_inicio', 'activo']
		verbose_name = 'Período Contable'
		verbose_name_plural = 'Períodos Contables'
		permissions = [
			('activar_periodo', 'Activar períodos contables'),
			('cerrar_periodo', 'Cerrar períodos contables'),
		]

	def get_absolute_url(self):
		return reverse('vDetallePeriodo', {'_id':self.id})

	def __str__(self):
		return self.nombre