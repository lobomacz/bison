from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.conf import settings
from django.forms import formset_factory, modelformset_factory, inlineformset_factory
from . import models, forms
import datetime, calendar

# Create your views here.
@login_required
@permission_required(['contabilidad.view_asiento', 'contabilidad.view_cuenta', 'contabilidad.view_periodo'])
def index(request):
	empresa = settings.NOMBRE_EMPRESA
	c = {'titulo':'Panel de Contabilidad', 'seccion':'Contabilidad', 'empresa':empresa}
	return render(request, 'indice.html', c)

#Vista que despliega el catálogo de cuentas contables
@login_required
@permission_required(['contabilidad.view_cuenta', 'contabilidad.change_cuenta'])
def lista_cuentas(request):
	empresa = settings.NOMBRE_EMPRESA
	cuentas = models.Cuenta.objects.all()
	c = {'titulo':'Catálogo de Cuentas', 'seccion':'Contabilidad', 'empresa':empresa, 'cuentas':cuentas}
	return render(request, 'catalogo.html' c)

#Vista para ingreso de nueva cuenta contable
@login_required
@permission_required('contabilidad.add_cuenta')
def nueva_cuenta(request):

	if request.method == "GET":

		empresa = settings.NOMBRE_EMPRESA
		form = forms.CuentaForm()
		c = {'titulo':'Ingreso de Cuentas Contables', 'seccion':'Contabilidad', 'empresa':empresa, 'form':form, 'view':'vNuevaCuenta'}
		return render(request, 'cuenta_form.html', c)
	
	elif request.method == "POST":
		
		formCuenta = forms.CuentaForm(request.POST)
		if formCuenta.is_valid():
			formCuenta.save()
			return redirect('lista_cuentas')
		else:
			return render(request, 'error.html', {'titulo':'Error de Datos', 'mensaje':'Los datos ingresados no son correctos. Revise y vuelva a intentarlo.', 'view':'vListaCuentas'})

#Vista de edición de cuentas contables
@login_required
@permission_required(['contabilidad.view_cuenta', 'contabilidad.change_cuenta'])
def editar_cuenta(request, _id):

	if request.method == "GET":

		cuenta = get_object_or_404(models.Cuenta, pk=_id)
		empresa = settings.NOMBRE_EMPRESA
		form = forms.CuentaForm(cuenta)
		c = {'titulo':'Edición de datos de cuenta contable', 'seccion':'Contabilidad', 'form':form, 'id':_id, 'view':'vEditarCuenta', 'empresa':empresa}
		return render(request, 'cuenta_form.html', c)

	elif request.method == "POST":
		
		cuenta = get_object_or_404(models.Cuenta, pk=_id)
		cuentaForm = forms.CuentaForm(request.POST, instance=cuenta)

		if cuentaForm.is_valid():
			cuentaForm.save()
			return redirect('lista_cuentas')
		else:
			return render(request, 'error.html', {'titulo':'Error de Datos', 'mensaje':'Los datos ingresados no son correctos. Revise y vuelva a intentarlo.'})


#Vista para cerrar una cuenta
@login_required
@permission_required('contabilidad.change_cuenta')
def cerrar_cuenta(request, _id):

	if request.method == "GET":

		empresa = settings.NOMBRE_EMPRESA
		return render(request, 'warning_template.html', {'empresa':empresa, 'seccion':'Contabilidad', 'titulo':'Cerrar Cuenta Contable', 'mensaje':'Al cerrar la cuenta contable, no podrá ser utilizada para registrar movimientos.', 'view':'vCerrarCuenta', 'id':_id})

	elif request.method == "POST":
		cuenta = get_object_or_404(models.Cuenta, pk=_id)

		cuenta.cerrada = True
		cuenta.save()

		return redirect('lista_cuentas')


@login_required
@permission_required('contabilidad.delete_cuenta')
def eliminar_cuenta(request, _id):

	if request.method == "GET":

		empresa = settings.NOMBRE_EMPRESA
		return render(request, 'warning_template.html', {'empresa':empresa, 'seccion':'Contabilidad', 'titulo':'Eliminar Cuenta Contable', 'mensaje':'Se borrará el registro de la base de datos. Si existen asientos con esta cuenta, no podrá ser eliminada.', 'view':'vEliminarCuenta', 'id':_id})

	elif request.method == "POST":
		cuenta = get_object_or_404(models.Cuenta, pk=_id)

		cuenta.delete()

		return redirect('lista_cuentas')


@login_required
@permission_required('contabilidad.view_asiento')
def indice_asientos(request, id_periodo=None, inicio=None, final=None):

	periodo = None
	c = None

	if id_periodo is None:
	
		periodo = models.Periodo.objects.get(activo=True)

	else:

		periodo = models.Periodo.objects.get(pk=id_periodo)


	if inicio is None and final is None:

		asientos = models.Asiento.objects.filter(fecha__gte=periodo.fecha_inicio, fecha__lte=periodo.fecha_final)
		periodos = models.Periodo.objects.all()
		empresa = settings.NOMBRE_EMPRESA
		c = {'titulo':'Lista de Asientos Contables', 'seccion':'Asientos Contables', 'empresa':empresa, 'periodos':periodos, 'asientos':asientos}

	else:

		asientos = models.Asiento.objects.filter(fecha__gte=inicio, fecha__lte=final)
	
		empresa = settings.NOMBRE_EMPRESA
		c = {'titulo':'Lista de Asientos Contables Por Rango De Fecha', 'seccion':'Asientos Contables', 'empresa':empresa, 'asientos':asientos, 'fecha_inicio':inicio, 'fecha_final':final}

	return render(request, 'indice_asientos.html', c)

@login_required
@permission_required('contabilidad.view_asiento')
def asientos_anulados(request):

	asientos = models.Asiento.objects.filter(anulado=True)

	empresa = settings.NOMBRE_EMPRESA

	c = {'titulo':'Lista de Asientos Contables Anulados', 'seccion':'Asientos Contables', 'empresa':empresa, 'asientos':asientos, 'anulados':True}

	return render(request, 'indice_asientos.html', c)


@login_required
@permission_required('contabilidad.change_asiento')
def ver_asiento(request, _id):

	asiento = get_object_or_404(models.Asiento, pk=_id)

	empresa = settings.NOMBRE_EMPRESA

	c = {'titulo':'Detalle de Asiento Contable', 'seccion':'Asientos Contables', 'asiento':asiento, 'empresa':empresa}

	return render(request, 'detalle_asiento.html', c)


@login_required
@permission_required('contabilidad.add_asiento')
def nuevo_asiento(request, _id):

	if request.method == 'GET':
		
		asientoForm = forms.AsientoForm()

		empresa = settings.NOMBRE_EMPRESA

		c = {'titulo':'Ingreso de Nuevo Asiento', 'seccion':'Asientos Contables', 'empresa':empresa, 'form':asientoForm, 'view':'vNuevoAsiento'}

		return render(request, 'form_asiento.html', c)

	elif request.method == 'POST':

		asientoForm = forms.AsientoForm(request.POST)

		if asientoForm.is_valid():

			asientoForm.save()

			return redirect('indice_asientos')

		else:

			return render(request, 'error.html', {'titulo':'Error de Datos', 'mensaje':'Los datos ingresados no son correctos. Revise y vuelva a intentarlo.'})

@login_required
@permission_required('contabilidad.change_asiento')
def editar_asiento(request, _id):

	AsientoFormSet = inlineformset_factory(models.Asiento, models.DetalleAsiento, extra=6)

	if request.method == 'GET':

		asiento = get_object_or_404(models.Asiento, pk=_id)

		formset = AsientoFormSet(instance=asiento)

		empresa = settings.NOMBRE_EMPRESA

		c = {'titulo':'Modificar Datos de Asiento Contable', 'seccion':'Asientos Contables', 'empresa':empresa, 'formset':formset, 'view':'vEditarAsiento'}

		return render(request, 'form_asiento.html', c)

	elif request.method == 'POST':
		
		asiento = get_object_or_404(models.Asiento, pk=_id)

		formset = AsientoFormSet(request.POST, instance=asiento)

		if formset.is_valid():

			debe = 0.00

			haber = 0.00

			for form in formset:

				detalle = form.save(commit=False)

				if detalle.movimiento == "db":
					debe += detalle.monto
				else:
					haber += detalle.monto

			if not (debe - haber) == 0.00:

				return render(request, 'error.html', {'titulo':'Error en la suma', 'mensaje':'La suma de los montos no cuadra. Revise y vuelva a intentarlo.'})
			
			formset.save()

			return redirect('indice_asientos')

		else:

			return render(request, 'error.html', {'titulo':'Error de Datos', 'mensaje':'Los datos ingresados no son correctos. Revise y vuelva a intentarlo.'})
	
"""

@login_required
@permission_required(['contabilidad.change_asiento', 'contabilidad.add_detalleasiento'])
def nuevo_detalle_asiento(request, _id):

"""

@login_required
@permission_required('contabilidad.delete_detalleasiento')
def eliminar_detalle_asiento(request, _id):

	if request.method == 'GET':
		
		empresa = settings.NOMBRE_EMPRESA

		c = {'titulo':'Eliminar Detalle de Asiento', 'seccion':'Asientos Contables', 'mensaje':'Se eliminará el detalle de asiento.', 'view':'vEliminarDetalleAsiento', 'id':_id}

		return render(request, 'warning_template.html', c)

	elif request.method == 'POST':
		
		detalle = get_object_or_404(models.DetalleAsiento, pk=_id)
		id_asiento = detalle.asiento.id

		detalle.delete()

		return redirect('editar_asiento', {'_id':asiento.id_asiento})


@login_required
@permission_required('contabilidad.contabilizar_asiento')
def contabilizar_periodo(request, id=None):

	empresa = settings.NOMBRE_EMPRESA

	if request.method == "GET":
		
		periodos = get_list_or_404(models.Periodo)

		c = {'titulo':'Contabilizar Asientos Por Período', 'seccion':'Contabilidad', 'empresa':empresa, 'periodos':periodos}

		return render(request, 'contabilizar.html', c)


	elif request.method == "POST":

		periodo = get_object_or_404(models.Periodo, pk=id)

		asientos = get_list_or_404(models.Asiento, fecha__gte=periodo.fecha_inicial, fecha__lte=periodo.fecha_final)

		for asiento in asientos:

			asiento.contabilizado = True

			asiento.save()

		c = {'empresa':empresa, 'titulo':'Asientos Contabilizados', 'mensaje':'Asientos Contabilizados' 'seccion':'Contabilidad', 'view':'vIndexContabilidad'}

		return render(request, 'warning_template.html', c)


@login_required
@permission_required('contabilidad.view_ejercicio')
def lista_ejercicios(request):

	empresa = settings.NOMBRE_EMPRESA

	ejercicios = models.Ejercicio.objects.all()

	if ejercicios == None:
		
		fecha = datetime.datetime.today()
		anio = "{0}".format(fecha.year)

		ejercicio = models.Ejercicio()

		ejercicio.ejercicio = anio
		ejercicio.descripcion = "Ejercicio contable " + anio
		ejercicio.activo = True

		ejercicio.save()

		ejercicios = models.Ejercicio.objects.all()

	c = {'titulo':'Ejercicios Contables', 'empresa':empresa, 'ejercicios':ejercicios, 'seccion':'Ejercicios'}

	return render(request, 'indice_ejercicios.html', c)




@login_required
@permission_required('contabilidad.add_ejercicio')
def nuevo_ejercicio(request):
	
	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		ejercicio = models.Ejercicio()
		form = forms.EjercicioForm()

		c = {'titulo':'Nuevo Ejercicio', 'seccion':'Ejercicios', 'empresa':empresa, 'form':form}

		return render(request, 'form_ejercicio.html', c)

	elif request.method == "POST":
		
		if request.POST:
			
			form = forms.EjercicioForm(request.POST)

			if form.is_valid():
				
				ejercicio = form.save(commit=False)

				if ejercicio.activo:
					activo = models.Ejercicio.objects.get(activo=True)
					activo.activo = False
					activo.save()

				ejercicio.save()

				return redirect('lista_ejercicios')

			else:

				return render(request, 'error.html', {'titulo':'Error de Datos', 'seccion':'Ejercicios', 'mensaje':'Los datos del Ejercicio son inconsistentes. Revise y vuelva a intentarlo', 'view':'vListaEjercicios'})

		else:

			return render(request, 'error.html', {'titulo':'Error de Datos', 'seccion':'Ejercicios', 'mensaje':'Los datos del Ejercicio son inconsistentes. Revise y vuelva a intentarlo', 'view':'vListaEjercicios'})

@login_required
@permission_required('contabilidad.change_ejercicio')
def activar_ejercicio(request, _id):

	ejercicio = get_object_or_404(models.Ejercicio, pk=_id)

	activo = models.Ejercicio.objects.get(activo=True)
	periodos_abiertos = activo.periodo_set.filter(cerrado=False)

	if periodos_abiertos != None:
		return render(request, 'warning_template.html', {'titulo':'Ejercicio con Períodos Abiertos', 'seccion':'Ejercicios', 'mensaje':'El ejercicio presenta períodos sin cierre contable. No se puede activar otro ejercicio.', 'view':'vListaEjercicios'})

	activo.activo = False
	activo.save()

	ejercicio.activo = True
	ejercicio.save()

	return redirect('lista_ejercicios')

@login_required
@permission_required('contabilidad.view_periodo')
def lista_periodos(request, _id):

	ejercicio = get_object_or_404(models.Ejercicio, pk=_id)

	empresa = settings.NOMBRE_EMPRESA

	periodos = ejercicio.periodo_set.all()

	c = {'empresa':empresa, 'titulo':'Lista de Períodos Contables', 'seccion':'Períodos Contables', 'periodos':periodos, 'ejercicio':ejercicio}

	return render(request, 'indice_periodos.html', c)


@login_required
@permission_required('contabilidad.add_periodo')
def crear_periodos(request, _id):

	ejercicio = get_object_or_404(models.Ejercicio, pk=_id)

	anio = int(ejercicio.ejercicio)

	meses = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
	
	for mes in range(1, 13):

		rangomes = calendar.monthrange(anio, mes)

		primerdia = datetime.date(anio, mes, 1)
		ultimodia = datetime.date(anio, mes, rangomes[1])

		periodo = models.Periodo()
		periodo.ejercicio = ejercicio
		periodo.nombre = meses[mes-1]
		periodo.fecha_inicio = primerdia
		periodo.fecha_final = ultimodia

		periodo.save()

	return redirect('lista_periodos', {'_id':_id})


@login_required
@permission_required('contabilidad.change_periodo')
def editar_periodo(request, _id):

	periodo = get_object_or_404(models.Periodo, pk=_id)

	if request.method == "GET":
		
		form = forms.PeriodoForm(periodo)

		empresa = settings.NOMBRE_EMPRESA

		c = {'empresa':empresa, 'form':form, '_id':_id, 'titulo':'Editar Período Contable', 'seccion':'Contabilidad'}

		return render(request, 'form_periodo.html', c)

	elif request.method == "POST":
		
		if not request.POST:

			c = {'titulo':'Error de Datos', 'mensaje':'Los datos no son válidos. Revise y vuelva a intentarlo.', 'view':'vIndexContabilidad', 'seccion':'Contabilidad'}
			
			return render(request, 'error.html', c)

		else:

			form = forms.PeriodoForm(request.POST, instance=periodo)

			if form.is_valid():
				
				form.save()

				return redirect('lista_periodos')

			else:

				c = {'titulo':'Error de Datos', 'mensaje':'No se recibieron datos. Revise y vuelva a intentarlo.', 'view':'vIndexContabilidad', 'seccion':'Contabilidad'}
			
				return render(request, 'error.html', c)


@login_required
@permission_required('contabilidad.delete_periodo')
def eliminar_periodo(request, _id):

	if request.method == "GET":

		empresa = settings.NOMBRE_EMPRESA

		c = {'empresa':empresa, 'titulo':'Eliminar Período', 'mensaje':'Se eliminará el registro de la base de datos.', 'view':'vEliminarPeriodo', '_id':_id, 'seccion':'Contabilidad'}
		
		return render(request, 'warning_template.html', c)

	elif request.method == "POST":
		
		periodo = get_object_or_404(models.Periodo, pk=id)

		periodo.delete()

		return redirect('lista_periodos')

@login_required
@permission_required('contabilidad.change_periodo')
def activar_periodo(request, _id):

	periodo_ant = modeld.Periodo.objects.get(activo=True)

	if request.method == "GET":

		empresa = settings.NOMBRE_EMPRESA
		
		periodo_ant = modeld.Periodo.objects.get(activo=True)

		if not periodo_ant.cerrado:
			
			c = {'empresa':empresa, 'titulo':'Acción Denegada', 'mensaje':'No se ha cerrado el período anterior. Revise y vuelva a intentarlo.', 'view':'vListaPeriodos', '_id':periodo_ant.ejercicio.id, 'seccion':'Contabilidad'}
			
			return render(request, 'error.html', c)

		else:

			c = {'titulo':'Activar Periodo Contable', 'mensaje':'Se cerrará el período anterior y todos los demás permanecerán cerrados.', 'view':'vActivarPeriodo', '_id':_id, 'seccion':'Contabilidad'}

			return render(request, 'warning_template.html', c)

	elif request.method == "POST":

		periodo = get_object_or_404(models.Periodo, pk=_id)
		
		periodo_ant.activo = False

		periodo.activo = True

		try:

			periodo_ant.save()

			periodo.save()

			return redirect('lista_periodos', {'_id':periodo.ejercicio.id})
		
		except Exception as e:
			
			c = {'titulo':'Error al Guardar', 'mensaje':e, 'view':'vListaPeriodos', '_id':periodo_ant.ejercicio.id, 'seccion':'Contabilidad'}
			
			return render(request, 'error.html', c)


@login_required
@permission_required('contabilidad.change_periodo')
def cerrar_periodo(request, _id):

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		c = {'titulo':'Cierre de Período Contable', 'seccion':'Contabilidad', 'empresa':empresa, 'view':'vCerrarPeriodo', '_id':_id, 'mensaje':'Se contabilizarán todos los asientos del período.'}

		return render(request, 'warning_template.html', c)

	elif request.method == "POST":

		periodo = get_object_or_404(models.Periodo, pk=_id)

		asientos = get_list_or_404(models.Asiento, fecha__gte=periodo.fecha_inicio, fecha__lte=periodo.fecha_final)

		for asiento in asientos:
			
			try:

				asiento.contabilizado = True
				asiento.fecha_contabilizado = datetime.today()
				asiento.save()

			except Exception as e:
				
				c = {'titulo':'Error al Contabilizar', 'mensaje':e, 'view':'vListaPeriodos', '_id':periodo.ejercicio.id, 'seccion':'Contabilidad'}
			
				return render(request, 'error.html', c)

		empresa = settings.NOMBRE_EMPRESA

		c = {'titulo':'Período Cerrado con Exito', 'seccion':'Contabilidad', 'empresa':empresa, 'view':'vIndexContabilidad'}

		return render(request, 'periodo_cerrado.html', c)






	





	







