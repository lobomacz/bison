from django.db import models
from bison.core.models import Empleado
from bison.contabilidad.models import Asiento
from bison.inventario import SalidaAlmacen, EntradaAlmacen

# Create your models here.


class Factura(models.Model):
	"""Modelo para Facturas"""
	fecha = models.DateField()
	no_documento = models.CharField(max_length=10)
	cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True)
	asiento = models.ForeignKey(Asiento, on_delete=models.PROTECT)
	tipo = models.CharField('Tipo de Factura', choices=[('cr', 'Credito'), ('ct', 'Contado'), ('pf', 'Proforma')], max_length=2)
	tipo_pago = models.CharField('Forma de Pago', choices=[('ef', 'Efectivo'), ('tr', 'Tarjeta'), ('ck', 'Cheque')])
	cancelada = models.BooleanField()
	entregado = models.BooleanField()
	anulada = models.BooleanField()
	impresa = models.BooleanField()
	vendedor = models.ForeignKey('Vendedor')
	descuento = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

class DetalleFactura(models.Model):
	"""Modelo DetalleFactura asociado al modelo Factura"""
	factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
	producto = models.ForeignKey(Producto)
	cantidad = models.DecimalField('Cant.', max_digits=6, decimal_places=2)
	precio_unit = models.DecimalField('P. Unit.',max_digits=6, decimal_places=2)
	entregado = models.BooleanField()
	total = models.DecimalField(max_digits=6, decimal_places=2)

class Cliente(models.Model):
	"""Modelo de datos para Clientes"""
	id = models.CharField(max_length=25, primary_key=True)
	nombre = models.CharField(max_length=50)
	direccion = models.CharField(max_length=200, null=True)
	telefono = models.CharField(max_length=9, null=True)
	correo = models.EmailField('Email', null=True)

class Vendedor(models.Model):
	"""Modelo de datos para Vendedor"""
	empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
	ruta = modeld.CharField(max_length=25, null=True)
	activo = models.BooleanField()

class Camion(models.Model):
	"""Modelo de datos para Camion"""
	vendedor = models.ForeignKey(Vendedor)
	placa = models.CharField(max_length=10)
	habilitado = models.BooleanField()

class OrdenDeRuta(models.Model):
	"""Modelo de datos para OrdenDeRuta"""
	camion = models.ForeignKey(Camion, on_delete=models.SET_NULL)
	fecha = models.DateField()
	empleado = models.ForeignKey(Empleado)
	autorizado = models.BooleanField(default=False)
	autorizado_por = models.ForeignKey(Empleado)
	anulado = models.BooleanField(default=False)
	entregado = models.BooleanField(default=False)
	salida = models.ForeignKey(SalidaAlmacen, null=True)
	entrada = models.ForeignKey(EntradaAlmacen, null=True)
	facturas = models.ManyToManyField(Factura, null=True)
	liquidado = models.BooleanField(default=False)

class DetalleOrdenDeRuta(models.Model):
	"""Modelo de datos para DetalleOrdenDeRuta"""
	orden = models.ForeignKey(OrdenDeRuta)
	producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
	unidad_medida = models.ForeignKey(UnidadMedida)
	cantidad = models.DecimalField(max_digits=6, decimal_places=2)
		
						