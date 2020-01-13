from django.db import models
from django.urls import reverse
from bison.core.models import Empleado, Unidad
from bison.contabilidad.models import Asiento
from bison.inventario.models import Salida, Producto

# Create your models here.


class Factura(models.Model):
	"""Modelo para Facturas"""
	fecha = models.DateField()
	no_documento = models.CharField(max_length=10, null=True)
	cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True)
	vendedor = models.ForeignKey('Vendedor', on_delete=models.SET_NULL, null=True)
	asiento = models.ForeignKey(Asiento, on_delete=models.SET_NULL, null=True)
	salida = models.ManyToManyField(Salida)
	tipo = models.CharField('Tipo de Factura', choices=[('cr', 'Credito'), ('ct', 'Contado'), ('pf', 'Proforma')], max_length=2)
	tipo_pago = models.CharField('Forma de Pago', choices=[('ef', 'Efectivo'), ('tr', 'Tarjeta'), ('ck', 'Cheque')])
	cancelada = models.BooleanField()
	entregado = models.BooleanField()
	anulada = models.BooleanField()
	impresa = models.BooleanField()
	descuento = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	subtotal = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	iva = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

	class Meta:
		ordering = ['no_documento', 'fecha']
		indexes = [
			models.Index(fields=['no_documento', 'tipo', 'vendedor'])
		]
		

class DetalleFactura(models.Model):
	"""Modelo DetalleFactura asociado al modelo Factura"""
	factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
	producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
	cantidad = models.DecimalField('Cant.', max_digits=6, decimal_places=2)
	unidad_medida = models.ForeignKey(Unidad, on_delete=PROTECT)
	precio_unit = models.DecimalField('P. Unit.',max_digits=6, decimal_places=2, default=0.00)
	total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	entregado = models.BooleanField(default=False)
	fecha_entregado = models.DateField(null=True)

	class Meta:
		ordering = ['factura', 'item']
		unique_together = ['factura', 'producto']
		verbose_name = 'Detalle de Factura'
		verbose_name_plural = 'Detalles de Factura'


class Proforma(models.Model):
	"""Modelo para Facturas"""
	fecha = models.DateField()
	cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True)
	vendedor = models.ForeignKey('Vendedor', on_delete=models.SET_NULL, null=True)
	impresa = models.BooleanField(default=False)
	anulado = models.BooleanField(default=False)
	anulado_por = models.ForeignKey(Empleado, on_delete=models.PROTECT, null=True)
	descuento = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	subtotal = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	iva = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

	class Meta:
		ordering = ['fecha']
		indexes = [
			models.Index(fields=['vendedor'])
		]

class DetalleProforma(models.Model):
	"""Modelo DetalleFactura asociado al modelo Factura"""
	proforma = models.ForeignKey(Proforma, on_delete=models.CASCADE)
	producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
	cantidad = models.DecimalField('Cant.', max_digits=6, decimal_places=2)
	unidad_medida = models.ForeignKey(Unidad, on_delete=PROTECT)
	precio_unit = models.DecimalField('P. Unit.',max_digits=6, decimal_places=2, default=0.00)
	total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

	class Meta:
		ordering = ['proforma', 'item']
		unique_together = ['proforma', 'producto']
		verbose_name = 'Detalle de Proforma'
		verbose_name_plural = 'Detalles de Proforma'



class Cliente(models.Model):
	"""Modelo de datos para Clientes"""
	id = models.CharField('Cedula/RUC', max_length=25, primary_key=True)
	nombre = models.CharField(max_length=50)
	direccion = models.CharField(max_length=200, null=True)
	telefono = models.CharField(max_length=9, null=True)
	correo = models.EmailField('Email', null=True)

	class Meta:
		ordering = ['nombre', 'correo']
		indexes = [
			models.Index(fields=['correo', 'nombre'])
		]

	def __str__(self):

		return self.nombre

class Ruta(models.Model):
	"""Modelo de datos para Ruta"""
	descripcion = models.CharField(max_length=100)
	especial = models.BooleanField(default=False)
	habilitado = models.BooleanField()
		

class Vendedor(models.Model):
	"""Modelo de datos para Vendedor"""
	empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
	ruta = modeld.ForeignKey(Ruta, null=True)
	activo = models.BooleanField()
	aplica_descuentos = models.BooleanField()

	def __str__(self):

		return '{0} {1}'.format(self.empleado.nombre, self.empleado.apellido)


class Camion(models.Model):
	"""Modelo de datos para Camion"""
	descripcion = models.CharField(max_length=45)
	tonelaje = models.IntegerField(default=2)
	anno = models.CharField(max_length=4, min_length=4)
	seguro_hasta = models.DateField()
	placa = models.CharField(max_length=10)
	habilitado = models.BooleanField()

	def __str__(self):

		return '{0} {1} Placa: {2}'.format(self.descripcion, self.anno, self.placa)
		

class OrdenRuta(models.Model):
	"""Modelo de datos para OrdenDeRuta"""
	camion = models.ForeignKey(Camion, on_delete=models.PROTECT)
	fecha = models.DateField()
	vendedor = models.ForeignKey(Vendedor, on_delete=models.PROTECT)
	ruta = models.ForeignKey(Ruta)
	digitador = models.ForeignKey(Empleado, on_delete=models.PROTECT)
	autorizado = models.BooleanField(default=False)
	autorizado_por = models.ForeignKey(Empleado, on_delete=models.PROTECT, null=True)
	liquidado = models.BooleanField(default=False)
	liquidado_por = models.ForeignKey(Empleado, on_delete=models.PROTECT, null=True)
	anulado = models.BooleanField(default=False)
	entregado = models.BooleanField(default=False)
	entregado_por = models.ForeignKey(Empleado, on_delete=models.PROTECT, null=True)
	recibido_por = models.ForeignKey(Empleado, on_delete=models.PROTECT, null=True)
	observaciones = models.CharField(max_length=400, null=True)

class DetalleOrdenRuta(models.Model):
	"""Modelo de datos para DetalleOrdenDeRuta"""
	orden = models.ForeignKey(OrdenRuta)
	producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
	unidad_medida = models.ForeignKey(Unidad, on_delete=models.PROTECT)
	cantidad_entregada = models.DecimalField(max_digits=4, decimal_places=2)
	total = models.DecimalField('Costo Total', max_digits=6, decimal_places=2, default=0.00)
	cantidad_vendida = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
	vendido = models.DecimalField('Venta', max_digits=6, decimal_places=2, default=0.00)
	cantidad_recibida = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
	faltante = models.DecimalField('Costo Faltante', max_digits=6, decimal_places=2, null=True)

		
						