from django import forms
from django.core.validators import RegexValidator
from . import models

class fFactura(forms.ModelForm):
	"""docstring for FacturaForm"""
	class Meta:
		model = models.Factura 
		exclude = ['asiento', 'salida', 'anulada', 'impresa', 'subtotal', 'iva', 'total', 'vendedor', 'cancelada', 'entregado']
		widgets = {
			'id':forms.HiddenInput
		}

class fFacturaEditar(forms.ModelForm):
	"""docstring para fFacturaEditar"""
	class Meta:
		model = models.Factura
		exclude = ['impresa', 'subtotal', 'iva', 'total', 'vendedor', 'cancelada', 'anulada', 'entregado']
		widgets = {
			'id':forms.HiddenInput
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
		exclude = ['vendedor', 'impresa', 'anulado', 'anulado_por', 'subtotal', 'iva', 'total']
		widgets = {
			'id':forms.HiddenInput
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


class fVendedor(forms.ModelForm):
	"""docstring for VendedorForm"""
	class Meta:
		model = models.Vendedor
		fields = '__all__'

class fCamion(forms.ModelForm):

	class Meta:
		model = models.Camion
		fields = '__all__'

class fRuta(forms.ModelForm):

	class Meta:
		model = models.Ruta 
		fields = '__all__'


class fOrdenRuta(forms.ModelForm):

	class Meta:
		model = models.OrdenRuta 
		exclude = [
			'entregado', 
			'entregado_por',
			'autorizado',
			'autorizado_por',
			'anulado',
			'liquidado',
			'liquidado_por',
			'digitador',
			'recibido_por',
		]
		widgets = {
			'id':forms.HiddenInput
		}

class fEntregaOrdenRuta(forms.ModelForm):

	class Meta:
		model = models.OrdenRuta
		fields = ['id', 'recibido_por']
		widgets = {
			'id':forms.HiddenInput
		}
		

class fDetalleOrdenRuta(forms.ModelForm):

	class Meta:
		model = models.DetalleOrdenRuta 
		exclude = [
			'total', 
			'cantidad_vendida', 
			'vendido', 
			'cantidad_recibida', 
			'faltante', 
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
		exclude = ['vendido', 'faltante']
		widgets = {
			'id':forms.HiddenInput,
			'orden':forms.HiddenInput,
			'producto':forms.TextInput(attrs={'readonly':True}),
			'unidad_medida':forms.TextInput(attrs={'readonly':True}),
			'cantidad_entregada':forms.TextInput(attrs={'readonly':True}),
			'total':forms.TextInput(attrs={'readonly':True}),
		}



		

