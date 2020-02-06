from django import forms
from django.core.validators import RegexValidator
from . import models


class CuentaForm(forms.ModelForm):
	"""Formulario para  CuentaContable"""

	class Meta:
		model = models.Cuenta
		fields = '__all__'


class AsientoForm(forms.ModelForm):
	"""Formulario para Asiento"""
	
	class Meta:
		model = models.Asiento
		exclude = [
		 'contabilizado',
		 'fecha_contabilizado',
		 'anulado',
		 'fecha_anulado',
		 ]
		widgets = {
			'id':forms.HiddenInput
		}

class DetalleAsientoForm(forms.ModelForm):
	"""Formulario para DetalleAsiento"""

	class Meta:
		model = models.DetalleAsiento
		fields = '__all__'
		widgets = {
			'id':forms.HiddenInput,
			'asiento':forms.HiddenInput,
		}

class EjercicioForm(forms.ModelForm):
	""" Formulario para Ejercicio """

	class Meta:
		model = models.Ejercicio
		fields = '__all__'
		

class PeriodoForm(forms.ModelForm):
	"""Formulario para PeriodoContable"""

	class Meta:
		model = models.PeriodoContable
		fields = '__all__'
		widgets = {
			'id':forms.HiddenInput,
			'ejercicio':forms.HiddenInput,
		}
		




