from django.db import models
from django.urls import reverse
from bison.core.models import Empleado, Unidad, Producto
from bison.contabilidad.models import Cuenta, Asiento
from bison.inventario.models import Salida, Almacen

# Create your models here.


class Factura(models.Model):
	"""Modelo para Facturas"""
	fecha = models.DateField()
	no_documento = models.CharField(max_length=10)
	cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL)
	vendedor = models.ForeignKey('Vendedor', on_delete=models.SET_NULL)
	asiento = models.OneToOneField(Asiento, on_delete=models.PROTECT, null=True)
	salida = models.OneToOneField(Salida, on_delete=models.PROTECT, null=True)
	tipo = models.CharField(verbose_name='tipo de factura', choices=[('cr', 'Credito'), ('ct', 'Contado')], max_length=2)
	tipo_pago = models.CharField(verbose_name='forma de pago', choices=[('ef', 'Efectivo'), ('tr', 'Tarjeta'), ('ck', 'Cheque')], max_length=2)
	descuento = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	subtotal = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	iva = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	cancelada = models.BooleanField(default=False)
	entregada = models.BooleanField(default=False)
	fecha_entregada = models.DateTimeField(null=True)
	entregada_por = models.ForeignKey(Empleado, null=True)
	anulada = models.BooleanField(default=False)
	anulada_por = models.ForeignKey(Empleado, null=True)
	fecha_anulada = models.DateField(null=True)
	impresiones = models.IntegerField(default=0)
	observaciones = models.CharField(max_length=250, null=True)

	class Meta:
		ordering = ['no_documento', 'fecha']
		permissions = [
			('view_all_factura', 'Ver todas las facturas'),
			('anular_factura', 'Anular facturas'),
			('cancelar_factura', 'Cancelar facturas'),
			('asiento_factura', 'Asiento de facturas'),
		]
		indexes = [
			models.Index(fields=['no_documento', 'tipo', 'vendedor'])
		]
		

class DetalleFactura(models.Model):
	"""Modelo DetalleFactura asociado al modelo Factura"""
	factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
	producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
	cantidad = models.DecimalField(max_digits=6, decimal_places=2)
	unidad_medida = models.ForeignKey(Unidad, on_delete=PROTECT)
	precio_unit = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	#entregado = models.BooleanField(default=False)
	#fecha_entregado = models.DateField(null=True)

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
	vigente = models.BooleanField(default=True)
	anulado = models.BooleanField(default=False)
	anulado_por = models.ForeignKey(Empleado, on_delete=models.PROTECT, null=True)
	descuento = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	subtotal = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	iva = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)


	class Meta:
		ordering = ['fecha', 'cliente']
		permissions = [
			('view_all_proforma', 'Ver todas las proformas'),
			('anular_proforma', 'Anular proformas'),
			('imprimir_proforma', 'Imprimir proformas'),
		]
		indexes = [
			models.Index(fields=['vendedor'])
		]

class DetalleProforma(models.Model):
	"""Modelo DetalleFactura asociado al modelo Factura"""
	proforma = models.ForeignKey(Proforma, on_delete=models.CASCADE)
	producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
	cantidad = models.DecimalField(max_digits=6, decimal_places=2)
	unidad_medida = models.ForeignKey(Unidad, on_delete=PROTECT)
	precio_unit = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

	class Meta:
		ordering = ['proforma', 'item']
		unique_together = ['proforma', 'producto']
		verbose_name = 'Detalle de Proforma'
		verbose_name_plural = 'Detalles de Proforma'



class Cliente(models.Model):
	"""Modelo de datos para Clientes"""
	id = models.CharField(verbose_name='No. Identificación', max_length=25, primary_key=True)
	nombre = models.CharField(max_length=50)
	direccion = models.CharField(max_length=200, null=True)
	telefono = models.CharField(max_length=9, null=True)
	correo = models.EmailField(verbose_name='Email', null=True)

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
	almacen = models.ForeignKey(Almacen, on_delete=models.PROTECT)
	especial = models.BooleanField(default=False)
	habilitado = models.BooleanField(default=True)

	def __str__(self):
		return self.descripcion


class Camion(models.Model):
	"""Modelo de datos para Camion"""
	descripcion = models.CharField(max_length=45, verbose_name='descripción')
	tonelaje = models.IntegerField(default=2)
	anno = models.CharField(verbose_name='año', max_length=4, min_length=4)
	seguro_hasta = models.DateField(verbose_name='seguro vence')
	placa = models.CharField(max_length=10)
	ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)
	cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, on_update=models.CASCADE)
	habilitado = models.BooleanField()

	class Meta:

		constraints = [
			UniqueConstraint(fields=['cuenta'], name='unique_cuenta_camion')
		]

	def __str__(self):

		return '{0} {1} Placa: {2}'.format(self.descripcion, self.anno, self.placa)

		


class Vendedor(models.Model):
	"""Modelo de datos para Vendedor"""
	empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
	ruta = modeld.ForeignKey(Ruta, null=True)
	activo = models.BooleanField(default=True)
	aplica_descuentos = models.BooleanField(default=False)

	class Meta:

		permissions = [
			('desactivar_venedor', 'Desactiva Vendedores')
		]

	def __str__(self):

		return '{0} {1}'.format(self.empleado.nombre, self.empleado.apellido)



class OrdenRuta(models.Model):
	"""Modelo de datos para OrdenDeRuta"""
	camion = models.ForeignKey(Camion, on_delete=models.PROTECT)
	fecha = models.DateField()
	vendedor = models.ForeignKey(Vendedor, on_delete=models.PROTECT)
	ruta = models.ForeignKey(Ruta)
	digitador = models.ForeignKey(Empleado, on_delete=models.PROTECT)
	autorizado = models.BooleanField(default=False)
	autorizado_por = models.ForeignKey(Empleado, on_delete=models.PROTECT, null=True)
	anulado = models.BooleanField(default=False)
	anulado_por = models.ForeignKey(Empleado, null=True)
	entregado = models.BooleanField(default=False)
	entregado_por = models.ForeignKey(Empleado, on_delete=models.PROTECT, null=True)
	recibido_por = models.ForeignKey(Empleado, on_delete=models.PROTECT, null=True)
	liquidado = models.BooleanField(default=False)
	liquidado_por = models.ForeignKey(Empleado, on_delete=models.PROTECT, null=True)
	observaciones = models.CharField(max_length=400, null=True)

	class Meta:
		ordering = ['fecha', 'ruta']
		permissions = [
			('autorizar_ordenruta', 'Autoriza ordenes de ruta'),
			('despachar_ordenruta', 'Despacha ordenes de ruta'),
			('anular_ordenruta', 'Anular ordenes de ruta'),
			('facturar_ordenruta', 'Facturar ordenes de ruta'),
			('liquidar_ordenruta', 'Liquidar ordenes de ruta'),
		]

class DetalleOrdenRuta(models.Model):
	"""Modelo de datos para DetalleOrdenDeRuta"""
	orden = models.ForeignKey(OrdenRuta, on_delete=models.CASCADE)
	producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
	unidad_medida = models.ForeignKey(Unidad, on_delete=models.PROTECT)
	cantidad_entregada = models.DecimalField(max_digits=4, decimal_places=2)
	costo_total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
	cantidad_vendida = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
	costo_vendido = models.DecimalField(verbose_name='venta', max_digits=6, decimal_places=2, default=0.00)
	cantidad_recibida = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
	costo_faltante = models.DecimalField(max_digits=6, decimal_places=2, null=True)

