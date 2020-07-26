from django import forms 
from bison.ventas.models import OrdenRuta
from . import models



class fAlmacen(forms.ModelForm):

	class Meta:
		model = models.Almacen
		exclude = ['id']


class fEditAlmacen(forms.ModelForm):

	class Meta:
		model = models.Almacen
		exclude = ['id', 'cuenta']


class fEntrada(forms.ModelForm):

	class Meta:
		model = models.Entrada 
		exclude = ['id']



class fDetalleEntrada(forms.ModelForm):

	class Meta:
		model = models.DetalleEntrada 
		exclude = ['id']
		widgets = {'entrada':forms.HiddenInput}



class fSalida(forms.ModelForm):

	class Meta:
		model = models.Salida 
		exclude = ['id']


class fDetalleSalida(forms.ModelForm):

	class Meta:
		model = models.DetalleSalida 
		exclude = ['id']
		widgets = {'salida':forms.HiddenInput}


class fTraslado(forms.ModelForm):

	class Meta:
		model = models.Traslado 
		exclude = ['id']


class fDetalleTraslado(forms.ModelForm):

	class Meta:
		model = models.DetalleTraslado 
		exclude = ['id']
		widgets = {'traslado':forms.HiddenInput}



class fEntregaOrdenRuta(forms.ModelForm):

	class Meta:
		model = OrdenRuta
		fields = ['id', 'recibido_por', 'observaciones']
		widgets = {
			'id':forms.HiddenInput
		}