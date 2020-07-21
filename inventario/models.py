from django.db import models
from bison.contabilidad.models import Cuenta, Asiento
from bison.core.models import Categoria, Unidad, Empleado, Producto
from bison.facturacion.models import Vendedor

# Create your models here.


class Almacen(models.Model):
	"""Modelo de datos para Almacenes"""
	cuenta = models.ForeignKey(Cuenta, on_delete=models.SET_NULL, null=True)
	descripcion = models.CharField(max_length=400)
	ubicacion = models.CharField(max_length=250)
	tipo_almacen = models.CharField(choices=[('temp', 'temporal'), ('perm', 'permanente')])
	metodo = models.CharField(choices=[('u', 'ueps'), ('p', 'peps'), ('pp', 'ponderado')])
	monto_total = models.DecimalField(max_digits=9, decimal_places=2)
	habilitado = models.BooleanField()
	almacen_padre = models.ForeignKey('self', null=True, on_delete=models.CASCADE, verbose_name='almacen superior')

	class Meta:
		ordering = ['id', 'cuenta']


class Entrada(models.Model):
	"""Modelo de datos para EntradaAlmacen"""
	fecha = models.DateField()
	almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
	asiento = models.ManyToManyField(Asiento, null=True)
	digitador = models.ForeignKey(Empleado)
	descripcion = models.CharField(max_length=400)
	referencia = models.CharField(max_length=45)
	observaciones = models.CharField(max_length=1000, null=True)

	class Meta:
		ordering = ['almacen', 'fecha']
	
	
class DetalleEntrada(models.Model):
	"""Modelo de datos para DetalleEntradaAlmacen"""
	entrada = models.ForeignKey(EntradaAlmacen, on_delete=models.CASCADE)
	producto = models.ForeignKey(Producto)
	unidad_medida = models.ForeignKey(Unidad)
	cantidad = models.DecimalField(max_digits=6, decimal_places=2)
	costo_unit = models.DecimalField(max_digits=6, decimal_places=2)
	total = models.DecimalField(max_digits=6, decimal_places=2)
	
class Salida(models.Model):
	"""Modelo de datos para SalidaAlmacen"""
	fecha = models.DateField()
	almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
	asiento = models.ManyToManyField(Asiento)
	digitador = models.ForeignKey(Empleado)
	descripcion = models.CharField(max_length=400)
	referencia = models.CharField(max_length=45)
	observaciones = models.CharField(max_length=1000, null=True)

	class Meta:
		ordering = ['fecha']
	

class DetalleSalida(models.Model):
	"""Modelo de datos para DetalleSalidaAlmacen"""
	salida = models.ForeignKey(SalidaAlmacen, on_delete=models.CASCADE)
	producto = models.ForeignKey(Producto)
	unidad_medida = models.ForeignKey(Unidad)
	cantidad = models.DecimalField(max_digits=6, decimal_places=2)
	costo_unit = models.DecimalField(max_digits=6, decimal_places=2)
	total = models.DecimalField(max_digits=6, decimal_places=2)


class Traslado(models.Model):
	"""Modelo de datos para Traslado"""
	fecha = models.DateField()
	origen = models.ForeignKey(Almacen, on_delete=models.PROTECT)
	destino = models.ForeignKey(Almacen, on_delete=models.PROTECT)
	asiento = models.ForeignKey(Asiento, on_delete.PROTECT)
	digitador = models.ForeignKey(Empleado)
	descripcion = models.CharField(max_length=400)
	referencia = models.CharField(max_length=45)
	observaciones = models.CharField(max_length=1000, null=True)

	class Meta:
		ordering = ['fecha']

class DetalleTraslado(models.Model):
	"""docstring for DetalleTraslado"""
	traslado = models.ForeignKey(Traslado, on_delete=models.CASCADE)
	producto = models.ForeignKey(Producto)
	unidad_medida = models.ForeignKey(Unidad)
	cantidad = models.DecimalField(max_digits=6, decimal_places=2)
	costo_unit = models.DecimalField(max_digits=6, decimal_places=2)
	total = models.DecimalField(max_digits=6, decimal_places=2)
		


		


		
						