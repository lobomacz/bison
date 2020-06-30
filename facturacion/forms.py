from django import forms
from django.core.validators import RegexValidator
from . import models

class fFactura(forms.ModelForm):
	"""docstring for FacturaForm"""
	class Meta:
		model = models.Factura 
		exclude = [
		'asiento', 
		'salida', 
		'anulada', 
		'anulada_por',
		'fecha_anulada',
		'impresiones', 
		'subtotal', 
		'iva', 
		'total', 
		'vendedor', 
		'cancelada', 
		'entregada',
		'entregada_por',
		'fecha_entregada']
		widgets = {
			'id':forms.HiddenInput,
			'fecha':forms.TextInput(attrs={'readonly':True})
		}

class fFacturaEditar(forms.ModelForm):
	"""docstring para fFacturaEditar"""
	class Meta:
		model = models.Factura
		exclude = ['impresiones', 'subtotal', 'iva', 'total', 'vendedor', 'cancelada', 'anulada', 'entregado']
		widgets = {
			'id':forms.HiddenInput,
			'fecha':forms.TextInput(attrs={'readonly':True})
		}

class fDetalleFactura(forms.ModelForm):

	class Meta:
		model = models.DetalleFactura
		exclude = ['total', 'entregado', 'fecha_entregado']
		widgets = {
			'id':forms.HiddenInput
			'factura':forms.HiddenInput
		}

class fProforma(forms.ModelForm):
	"""docstring for ProformaForm"""
	class Meta:
		model = models.Proforma 
		exclude = ['vendedor', 'anulado', 'anulado_por', 'subtotal', 'iva', 'total']
		widgets = {
			'id':forms.HiddenInput,
			'fecha':forms.TextInput(attrs={'readonly':True})
		}

class fProformaEditar(forms.ModelForm):
	"""docstring for ProformaForm"""
	class Meta:
		model = models.Proforma 
		exclude = ['vendedor', 'impresa', 'anulado', 'anulado_por', 'subtotal', 'iva', 'total']
		widgets = {
			'id':forms.HiddenInput,
			'fecha':forms.TextInput(attrs={'readonly':True}),
			'cliente':forms.TextInput(attrs={'readonly':True})
		}

class fDetalleProforma(forms.ModelForm):
	"""docstring for DetalleProformaForm"""
	class Meta:
		model = models.DetalleProforma 
		exclude = ['total']
		widgets = {
			'id':forms.HiddenInput,
			'proforma':forms.HiddenInput
		}

class fCliente(forms.ModelForm):

	class Meta:
		model = models.Cliente
		fields = '__all__'
		widgets = {
			'id':forms.HiddenInput
		}


class fVendedor(forms.ModelForm):
	"""docstring for VendedorForm"""
	class Meta:
		model = models.Vendedor
		exclude = ['activo']
		#fields = '__all__'
		widgets = {
			'id':forms.HiddenInput
		}


class fRuta(forms.ModelForm):

	class Meta:
		model = models.Ruta 
		fields = '__all__'
		widgets = {
			'id':forms.HiddenInput
		}



class fOrdenRuta(forms.ModelForm):

	class Meta:
		model = models.OrdenRuta 
		exclude = [
			'digitador',
			'entregado', 
			'entregado_por',
			'autorizado',
			'autorizado_por',
			'anulado',
			'anulado_por',
			'liquidado',
			'liquidado_por',
			'recibido_por',
		]
		widgets = {
			'id':forms.HiddenInput
		}

class fEditOrdenRuta(forms.ModelForm):

	class Meta:
		fields = ['id', 'fecha', 'camion', 'vendedor', 'ruta', 'observaciones']
		widgets = {
		'id':forms.HiddenInput,
		'fecha':forms.TextInput(attrs={'readonly':True})
		}
		

class fDetalleOrdenRuta(forms.ModelForm):

	class Meta:
		model = models.DetalleOrdenRuta 
		exclude = [
			'costo_total', 
			'cantidad_vendida', 
			'costo_vendido', 
			'cantidad_recibida', 
			'costo_faltante', 
			]
		widgets = {
			'id':forms.HiddenInput,
			'orden':forms.HiddenInput
		}
		labels = {
			'cantidad_entregada':'Cantidad'
		}


class fLiquidaDetalleOrdenRuta(forms.ModelForm):

	class Meta:
		model = models.DetalleOrdenRuta
		exclude = ['costo_vendido', 'costo_faltante']
		widgets = {
			'id':forms.HiddenInput,
			'orden':forms.HiddenInput,
			'producto':forms.TextInput(attrs={'readonly':True}),
			'unidad_medida':forms.TextInput(attrs={'readonly':True}),
			'cantidad_entregada':forms.TextInput(attrs={'readonly':True}),
			'costo_total':forms.TextInput(attrs={'readonly':True}),
		}



		

