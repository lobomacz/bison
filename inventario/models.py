from django.db import models
from bison.contabilidad.models import CuentaContable
from bison.core.models import Categoria, UnidadMedida, Empleado
from bison.facturacion.models import Vendedor

# Create your models here.

class Producto(models.Model):
	"""Modelo para registro de productos"""
	#codigo = models.CharField(max_length=50, primary_key=True)
	nombre = models.CharField(max_length=100)
	categoria = models.ForeignKey(Categoria)
	unidad_base = models.ForeignKey(UnidadMedida)
	costo_unit = models.DecimalField('Costo', max_digits=6, decimal_places=2)
	precio_unit = models.DecimalField('Precio', max_digits=6, decimal_places=2)
	minimo = models.DecimalField(max_digits=6, decimal_places=2)
	maximo = models.DecimalField(max_digits=6, decimal_places=2)

class Almacen(models.Model):
	"""Modelo de datos para Almacenes"""
	cuenta = models.ForeignKey(CuentaContable, on_delete=models.SET_NULL, null=True)
	ubicacion = models.CharField(max_length=15)
	habilitado = models.BooleanField()
	tipo_almacen = models.CharField(choices=[('temp', 'temporal'), ('perm', 'permanente')])

class Entrada(models.Model):
	"""Modelo de datos para EntradaAlmacen"""
	almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
	asiento = models.ManyToManyField(Asiento)
	fecha = models.DateField()
	empleado = models.ForeignKey(Empleado)
	descripcion = models.CharField(max_length=200)
	referencia = models.CharField(max_length=25)
	orden = models.ForeignKey('OrdenEntradaMateriales', null=True)
	#factura = models.CharField(max_length=15)
	
class DetalleEntrada(models.Model):
	"""Modelo de datos para DetalleEntradaAlmacen"""
	entrada = models.ForeignKey(EntradaAlmacen, on_delete=models.CASCADE)
	producto = models.ForeignKey(Producto)
	unidad_medida = models.ForeignKey(UnidadMedida)
	cantidad = models.DecimalField(max_digits=6, decimal_places=2)
	costo_unit = models.DecimalField(max_digits=6, decimal_places=2)
	total = models.DecimalField(max_digits=6, decimal_places=2)
	
class Salida(models.Model):
	"""Modelo de datos para SalidaAlmacen"""
	almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
	asiento = models.ManyToManyField(Asiento)
	fecha = models.DateField()
	empleado = models.ForeignKey(Empleado)
	descripcion = models.CharField(max_length=200)
	referencia = models.CharField(max_length=25)
	orden = models.ForeignKey('OrdenSalidaMateriales', null=True)
	#factura = models.ForeignKey(Factura, on_delete=models.CASCADE)

class DetalleSalida(models.Model):
	"""Modelo de datos para DetalleSalidaAlmacen"""
	salida = models.ForeignKey(SalidaAlmacen, on_delete=models.CASCADE)
	producto = models.ForeignKey(Producto)
	unidad_medida = models.ForeignKey(UnidadMedida)
	cantidad = models.DecimalField(max_digits=6, decimal_places=2)
	costo_unit = models.DecimalField(max_digits=6, decimal_places=2)
	total = models.DecimalField(max_digits=6, decimal_places=2)

class OrdenSalida(models.Model):
	"""Modelo de datos para OrdenSalidaMateriales"""
	fecha = models.DateField()
	concepto = models.CharField(max_length=200)
	empleado = models.ForeignKey(Empleado)
	autorizado = models.BooleanField(default=False)
	autorizado_por = models.ForeignKey(Empleado)
	anulado = models.BooleanField(default=False)
	entregado = models.BooleanField(default=False)
		
class DetalleOrden_Salida(models.Model):
	"""Modelo de datos para DetalleOrdenDeRuta"""
	orden = models.ForeignKey(OrdenSalidaMateriales)
	producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
	unidad_medida = models.ForeignKey(UnidadMedida)
	cantidad = models.DecimalField(max_digits=6, decimal_places=2)

class OrdenEntrada(models.Model):
	"""Modelo de datos para OrdenEntradaMateriales"""
	fecha = models.DateField()
	concepto = models.CharField(max_length=200)
	empleado = models.ForeignKey(Empleado)
	autorizado = models.BooleanField(default=False)
	autorizado_por = models.ForeignKey(Empleado)
	anulado = models.BooleanField(default=False)
	entregado = models.BooleanField(default=False)
		
class DetalleOrdenEntrada(models.Model):
	"""Modelo de datos para DetalleOrdenDeRuta"""
	orden = models.ForeignKey(OrdenEntradaMateriales)
	producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
	unidad_medida = models.ForeignKey(UnidadMedida)
	cantidad = models.DecimalField(max_digits=6, decimal_places=2)

class OrdenCarga(models.Model):
	"""Modelo de datos para Orden de Carga"""
	fecha = models.DateField()
	vendedor = models.ForeignKey(Vendedor)
	autorizado_por = models.ForeignKey(Empleado)
	entregado = models.BooleanField()
	liquidado = models.BooleanField()
	observaciones = models.CharField(max_length=400)

	class Meta:
		ordering = ['fecha', 'vendedor']
		permissions = [
			('autorizar_orden_carga', 'Autorizar Ordenes de Carga'),
			('liqueidar_orden_carga', 'Liquidar Ordenes de Carga'),
		]
		