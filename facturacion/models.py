from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Categoria(models.Model):
	nombre = models.CharField(max_length=45)

class UnidadMedida(models.Model):
	nombre = models.CharField(max_length=25)
	simbolo = models.CharField(max_length=8)
		

class Producto(models.Model):
	"""Modelo para registro de productos"""
	codigo = models.CharField(max_length=50, primary_key=True)
	nombre = models.CharField(max_length=100)
	categoria = models.ForeignKey(Categoria)
	unidad_base = models.ForeignKey(UnidadMedida)
	precio_unit = models.DecimalField('Precio', max_digits=6, decimal_places=2)
	minimo = models.DecimalField(max_digits=6, decimal_places=2)
	maximo = models.DecimalField(max_digits=6, decimal_places=2)

class Factura(models.Model):
	"""Modelo para Facturas"""
	fecha = models.DateField()
	no_documento = models.CharField(max_length=10)
	cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True)
	asientos = models.ManyToManyField('Asiento')
	tipo = models.CharField('Tipo de Factura', choices=[('cr', 'Credito'), ('ct', 'Contado'), ('pf', 'Proforma')], max_length=2)
	tipo_pago = models.CharField('Forma de Pago', choices=[('ef', 'Efectivo'), ('tr', 'Tarjeta'), ('ck', 'Cheque')])
	cancelado = models.BooleanField()
	entregado = models.BooleanField()
	anulada = models.BooleanField()
	vendedor = models.ForeignKey('Empleado')
	descuento = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

class DetalleFactura(models.Model):
	"""Modelo DetalleFactura asociado al modelo Factura"""
	factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
	producto = models.ForeignKey(Producto)
	cantidad = models.DecimalField('Cant.', max_digits=6, decimal_places=2)
	precio_unit = models.DecimalField('P. Unit.',max_digits=6, decimal_places=2)
	total = models.DecimalField(max_digits=6, decimal_places=2)

class Cliente(models.Model):
	"""Modelo de datos para Clientes"""
	id = models.CharField(max_length=25, primary_key=True)
	nombre = models.CharField(max_length=50)
	direccion = models.CharField(max_length=200, null=True)
	telefono = models.CharField(max_length=9, null=True)
	correo = models.EmailField('Email', null=True)

class Empleado(models.Model):
	"""Modelo de datos para Empleados"""
	cedula = models.CharField(primary_key=True, max_length=16)
	nombre = models.CharField(max_length=15)
	segundo_nombre  = models.CharField(max_length=15, null=True)
	apellido = models.CharField(max_length=15)
	segundo_apellido = models.CharField(max_length=15, null=True)
	direccion = models.CharField(max_length=200)
	correo = models.EmailField('Email', unique=True)
	usuario = models.OneToOneField('Usuario', null=True, on_delete=models.SET_NULL)
	
class Almacen(models.Model):
	"""Modelo de datos para Almacenes"""
	cuenta = models.ForeignKey("CuentaContable", on_delete=models.SET_NULL, null=True)
	ubicacion = models.CharField(max_length=15)
	habilitado = models.BooleanField()
	tipo_almacen = models.CharField(choices=[('temp', 'temporal'), ('perm', 'permanente')])

class CuentaContable(models.Model):
	"""Modelo de datos para Cuentas"""
	cuenta = models.CharField(max_length=25, primary_key=True)
	descripcion = models.CharField(max_length=100)
	cuenta_padre = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
	nivel = models.CharField(choices=[('C', 'Cuenta'), ('S', 'Subcuenta'), ('D', 'Detalle')])
	resumen = models.BooleanField()
	cerrada = models.BooleanField()

class Asiento(models.Model):
	"""Modelo de datos para Asientos"""
	fecha = models.DateField()
	descripcion = models.CharField(max_length=200)
	referencia = models.CharField(max_length=25)
	contabilizado = models.BooleanField()
	fecha_contabilizado = models.DateTimeField(null=True)
	anulado = models.BooleanField()
	fecha_anulado = models.DateTimeField(null=True)

class DetalleAsiento(models.Model):
	"""Modelo de datos para DetalleAsiento"""
	asiento = models.ForeignKey(Asiento, on_delete=models.CASCADE)
	cuenta = models.ForeignKey(CuentaContable, on_delete=models.PROTECT)
	movimiento = models.CharField(choices=[('db', 'Débito'), ('cr', 'Crédito')], max_length=2)
	monto = models.DecimalField(max_digits=6, decimal_places=2)

class EntradaAlmacen(models.Model):
	"""Modelo de datos para EntradaAlmacen"""
	almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
	asiento = models.ManyToManyField(Asiento)
	fecha = models.DateField()
	empleado = models.ForeignKey(Empleado)
	descripcion = models.CharField(max_length=200)
	referencia = models.CharField(max_length=25)
	#factura = models.CharField(max_length=15)
	
class DetalleEntradaAlmacen(models.Model):
	"""Modelo de datos para DetalleEntradaAlmacen"""
	entrada = models.ForeignKey(EntradaAlmacen, on_delete=models.CASCADE)
	producto = models.ForeignKey(Producto)
	unidad_medida = models.ForeignKey(UnidadMedida)
	cantidad = models.DecimalField(max_digits=6, decimal_places=2)
	costo_unit = models.DecimalField(max_digits=6, decimal_places=2)
	total = models.DecimalField(max_digits=6, decimal_places=2)
	
class SalidaAlmacen(models.Model):
	"""Modelo de datos para SalidaAlmacen"""
	almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
	asiento = models.ManyToManyField(Asiento)
	fecha = models.DateField()
	empleado = models.ForeignKey(Empleado)
	descripcion = models.CharField(max_length=200)
	referencia = models.CharField(max_length=25)
	#factura = models.ForeignKey(Factura, on_delete=models.CASCADE)

class DetalleSalidaAlmacen(models.Model):
	"""Modelo de datos para DetalleSalidaAlmacen"""
	salida = models.ForeignKey(SalidaAlmacen, on_delete=models.CASCADE)
	producto = models.ForeignKey(Producto)
	unidad_medida = models.ForeignKey(UnidadMedida)
	cantidad = models.DecimalField(max_digits=6, decimal_places=2)
	costo_unit = models.DecimalField(max_digits=6, decimal_places=2)
	total = models.DecimalField(max_digits=6, decimal_places=2)

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
	camion = models.ForeignKey(Camion)
	fecha = models.DateField()
	empleado = models.ForeignKey(Empleado)
	autorizado = models.BooleanField(default=False)
	autorizado_por = models.ForeignKey(Empleado)
	entregado = models.BooleanField(default=False)
	salida = models.ForeignKey(SalidaAlmacen, null=True)
	entrada = models.ForeignKey(EntradaAlmacen, null=True)
	facturas = models.ManyToManyField(Factura)
	liquidado = models.BooleanField(default=False)


class DetalleOrdenDeRuta(models.Model):
	"""Modelo de datos para DetalleOrdenDeRuta"""
	orden = models.ForeignKey(OrdenDeRuta)
	producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
	unidad_medida = models.ForeignKey(UnidadMedida)
	cantidad = models.DecimalField(max_digits=6, decimal_places=2)

		
class Usuario(models.Model):
	"""Modelo de datos para Usuario"""
	usuario = models.ForeignKey(User)

		
		
						