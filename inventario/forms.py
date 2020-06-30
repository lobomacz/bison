from django import forms
from bison.facturacion.models import OrdenRuta
from . import models



class fEntregaOrdenRuta(forms.ModelForm):

	class Meta:
		model = OrdenRuta
		fields = ['id', 'recibido_por', 'observaciones']
		widgets = {
			'id':forms.HiddenInput
		}