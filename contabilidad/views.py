from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.conf import settings
from django.urls import reverse
from django.forms import formset_factory, modelformset_factory, inlineformset_factory
from django.contrib import messages
from django.contrib.auth import login_required, permission_required
from django.db.models import Q, Sum
from bison.core.models import Empleado
from . import models, forms
import datetime, calendar, logging

# Create your views here.

def getNombreEmpresa():
	return settings.NOMBRE_EMPRESA


@login_required
@permission_required(['contabilidad.view_asiento', 'contabilidad.view_cuenta', 'contabilidad.view_periodo'])
def index(request):
	empresa = getNombreEmpresa()
	c = {'titulo':'Panel de Contabilidad', 'seccion':'Contabilidad', 'empresa':empresa}
	return render(request, 'contabilidad/indice.html', c)


#Vista que despliega el catálogo de cuentas contables
@login_required
@permission_required('contabilidad.view_cuenta')
def lista_cuentas(request, page):

	empresa = getNombreEmpresa()
	cuentas = models.Cuenta.objects.all()
	limite = settings.LIMITE_FILAS

	if cuentas.count() > 0:
		paginador = Paginator(cuentas, limite)
		cuentas = paginador.get_page(page)

	c = {'titulo':'Catálogo de Cuentas', 'seccion':'Contabilidad', 'empresa':empresa, 'cuentas':cuentas}

	return render(request, 'contabilidad/catalogo.html' c)



@login_required
@permission_required('contabilidad.view_cuenta')
def ver_cuenta(request, _id):

	cuenta = get_object_or_404(models.Cuenta, pk=_id)
	empresa = getNombreEmpresa()
	ruta_delete = reverse('vEliminarCuenta',{'_id':_id})
	ruta_edit = reverse('vEditarCuenta', {'_id':_id})
	ruta_cerrar = reverse('vCerrarCuenta', {'_id':_id})

	c = {'seccion':'Contabilidad', 'empresa':empresa, 'cuenta':cuenta, 'titulo':'Cuenta contable', 'ruta_delete':ruta_delete, 'ruta_edit':ruta_edit, 'ruta_cerrar':ruta_cerrar}

	return render(request, 'contabilidad/ver_cuenta.html', c)


#Vista para ingreso de nueva cuenta contable
@login_required
@permission_required('contabilidad.add_cuenta')
def nueva_cuenta(request):

	if request.method == "GET":

		empresa = getNombreEmpresa()
		form = forms.CuentaForm()
		ruta = reverse('vNuevaCuenta')
		c = {'titulo':'Ingreso de Cuentas Contables', 'seccion':'Contabilidad', 'empresa':empresa, 'form':form, 'ruta':ruta}
		
		return render(request, 'core/forms/form_template.html', c)
	
	elif request.method == "POST":
		
		form = forms.CuentaForm(request.POST)

		if form.is_valid():

			cuenta = None

			try:
				
				cuenta = form.save(commit=False)
				cuenta.save()

			except Exception as e:
				
				messages.error(request,"Excepción al registrar cuenta contable.")

				logging.error(e)

				return redirect(reverse('vError'))

			messages.success(request, 'La cuenta se registró con éxito')

			return redirect('ver_cuenta', {'_id':cuenta.id})
		

#Vista de edición de cuentas contables
@login_required
@permission_required('contabilidad.change_cuenta')
def editar_cuenta(request, _id):

	cuenta = get_object_or_404(models.Cuenta, pk=_id)

	if request.method == "GET":
		
		empresa = getNombreEmpresa()
		form = forms.EditCuentaForm(cuenta)
		ruta = reverse('vEditarCuenta', {'_id':_id})

		c = {'titulo':'Edición de Cuenta Contable', 'seccion':'Contabilidad', 'form':form, 'ruta':ruta, 'empresa':empresa}
		
		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.EditCuentaForm(request.POST, instance=cuenta)

		if form.is_valid():

			try:
				
				form.save()

			except Exception as e:
				
				messages.error(request,"Excepción al editar cuenta contable.")

				logging.error(e)

				return redirect(reverse('vError'))

			messages.success(request, 'El registro se actualizó con éxito')

			return redirect('vVerCuenta', {'_id':_id})
		


#Vista para cerrar una cuenta
@login_required
@permission_required('contabilidad.cerrar_cuenta')
def cerrar_cuenta(request, _id):

	if request.method == "POST":
		cuenta = get_object_or_404(models.Cuenta, pk=_id)

		cuenta.cerrada = True
		cuenta.save()

		return redirect('ver_cuenta', {'_id':_id})


@login_required
@permission_required('contabilidad.delete_cuenta')
def eliminar_cuenta(request, _id):

	if request.method == "POST":
		cuenta = get_object_or_404(models.Cuenta, pk=_id)

		cuenta.delete()

		return redirect('lista_cuentas', {'page':1})


@login_required
@permission_required('contabilidad.view_asiento')
def lista_asientos(request, page=1):

	'''
	periodo = None

	if _id is None:
		periodo = models.Periodo.objects.filter(activo=True)
	else:
		periodo = get_object_or_404(models.Periodo, pk=_id)

	asientos = models.Asiento.objects.filter(fecha__gte=periodo.fecha_inicio, fecha__lte=periodo.fecha_final)
	'''
	limite = settings.LIMITE_FILAS

	asientos = models.Asiento.objects.all()

	periodos = models.Periodo.objects.all()

	if asientos.count() > limite:
		
		paginador = Paginator(asientos)

		asientos = paginador.get_page(page)

	empresa = getNombreEmpresa()

	c = {'titulo':'Asientos Contables', 'seccion':'Contabilidad', 'empresa':empresa, 'asientos':asientos, 'periodos':periodos}

	return render(request, 'contabilidad/lista_asientos.html', c)


@login_required
@permission_required('contabilidad.view_asiento')
def lista_asientos_periodo(request, page, _id=None):

	limite = settings.LIMITE_FILAS

	periodo = models.Periodo.objects.find(activo=True) if _id == None else get_object_or_404(models.Periodo, pk=_id)

	asientos = get_list_or_404(models.Asiento, fecha__gte=periodo.fecha_inicio, fecha__lte=periodo.fecha_final)

	if asientos.count() > limite:
		
		paginador = Paginator(asientos)

		asientos = paginador.get_page(page)

	c = {'titulo':'Asientos Contables', 'seccion':'Contabilidad','periodo':periodo, 'asientos':asientos,'_id':_id}

	return render(request, 'lista_asientos_periodo.html', c)



@login_required
@permission_required('contabilidad.view_asiento')
def lista_asientos_fecha(request, page=1, inicio, final):

	empresa = getNombreEmpresa()

	if request.method == "GET":

		limite = settings.LIMITE_FILAS

		asientos = get_list_or_404(models.Asiento, fecha__gte=inicio, fecha__lte=final)

		if asientos.count() > limite:

			paginador = Paginator(asientos)

			asientos = paginador.get_page(page)
	
		c = {'titulo':'Asientos Por Rango De Fecha', 'seccion':'Asientos Contables', 'empresa':empresa, 'asientos':asientos, 'fecha_inicio':inicio, 'fecha_final':final}

		return render(request, 'contabilidad/lista_asientos.html', c)
		
		

@login_required
@permission_required('contabilidad.view_asiento')
def ver_asiento(request, _id):

	asiento = get_object_or_404(models.Asiento, pk=_id)

	empresa = getNombreEmpresa()

	ruta_edit = reverse('vEditarAsiento', {'_id':asiento.id})

	ruta_anular = reverse('vAnularAsiento', {'_id':asiento.id})

	ruta_delete = reverse('vEliminarAsiento', {'_id':asiento.id})

	ruta_detalle = reverse('vDetalleAsiento', {'_id':asiento.id})

	debito = 0.00
	credito = 0.00

	if asiento.detalleasiento_set != None:
		
		for detalle in asiento.detalleasiento_set:

			if detalle.movimiento == 'db':
				
				debito += detalle.monto

			elif detalle.movimiento == 'cr':

				credito += detalle.monto
			
	diferencia = debito - credito

	saldo = '(%.2f)' % (abs(diferencia)) if diferencia < 0 else '%.2f' % (diferencia)

	c = {
	'titulo':'Asiento Contable', 
	'seccion':'Contabilidad', 
	'asiento':asiento, 
	'empresa':empresa, 
	'ruta_edit':ruta_edit,
	'ruta_anular':ruta_anular,
	'ruta_delete':ruta_delete,
	'ruta_detalle':ruta_detalle,
	'debito':debito,
	'credito':credito,
	'saldo':saldo,
	}

	return render(request, 'contabilidad/ver_asiento.html', c)


@login_required
@permission_required(['contabilidad.change_asiento', 'contabilidad.anular_asiento'])
def anular_asiento(request, _id):

	if request.method == "POST":

		asiento = get_object_or_404(models.Asiento, pk=_id)

		if not asiento.contabilizado:

			asiento.anulado = True

			asiento.fecha_anulado = datetime.datetime.today()

			asiento.save()

			messages.success(request, 'El asiento contable fue anulado.')

		else:

			messages.warning(request, 'Asiento contabilizado. No se puede anular.')

		return redirect('ver_asiento', {'_id':_id})



@login_required
@permission_required('contabilidad.delete_asiento')
def eliminar_asiento(request, _id):

	if request.method == 'POST':
		
		asiento = get_object_or_404(models.Asiento, pk=_id)

		if not asiento.contabilizado:

			try:
				
				asiento.delete()

			except Exception as e:

				messages.error(request,"Excepción al eliminar asiento contable.")

				logging.error(e)

				return redirect(reverse('vError'))

			messages.success(request, 'El registro se eliminó con éxito.')

			return redirect('lista_asientos', {'page':1})

		else:
			
			messages.warning(request, 'Asiento contabilizado. No puede ser eliminado.')

			return redirect('ver_asiento', {'_id':_id})




@login_required
@permission_required(['contabilidad.add_asiento', 'contabilidad.add_detalleasiento'])
def detalle_asiento(request, _id):

	asiento = get_object_or_404(models.Asiento, pk=_id)

	extra = settings.EXTRA_ROWS

	extra_rows = extra if asiento.detalleasiento_set.all() != None else 4

	DetalleFormSet = inlineformset_factory(models.Asiento, models.DetalleAsiento, form=DetalleAsientoForm, extra=extra_rows)

	if request.method == "GET":
		
		empresa = getNombreEmpresa()

		formset = DetalleFormSet(instance=asiento)

		messages.info(request, 'Los campos con * son obligatorios.')

		c = {'titulo':'Detalle de Asiento Contable', 'seccion':'Contabilidad', 'empresa':empresa, 'formset':formset}

		return render(request, 'core/forms/inline_formset_template.html', c)

	elif request.method == "POST":
		
		formset = DetalleFormSet(request.POST, request.FILES, instance=asiento)

		if formset.is_valid():
			
			debito = 0.00
			credito = 0.00
			

			for form in formset.forms:

				detalle = form.save(commit=False)

				if detalle.movimiento == 'cr':
					credito += detalle.monto
				elif detalle.movimiento == 'db':
					debito += detalle.monto

			if credito < debito or debito < credito:
				
				messages.warning(request, 'Los montos del asiento no cuadran. {0:.2f}:{1:.2f}'.format(debito,credito))

				return redirect('detalle_asiento', {'_id':_id})

			else:

				messages.success(request, 'Los datos se registraron con éxito.')
				
				formset.save()



@login_required
@permission_required('contabilidad.add_asiento')
def nuevo_asiento(request):

	if request.method == 'GET':
		
		form = forms.AsientoForm()

		empresa = getNombreEmpresa()

		ruta = reverse('vNuevoAsiento')

		c = {'titulo':'Nuevo Asiento Contable', 'seccion':'Contabilidad', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, 'Los campos con * son obligatorios.')

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == 'POST':

		form = forms.AsientoForm(request.POST)

		if form.is_valid():

			asiento = form.save(commit=False)

			asiento.save()

			messages.success(request, 'Los datos se ingresaron con éxito.')

			return redirect('detalle_asiento', {'_id':asiento.id})

		

@login_required
@permission_required('contabilidad.change_asiento')
def editar_asiento(request, _id):

	asiento = get_object_or_404(models.Asiento, pk=_id)

	if request.method == 'GET':

		form = forms.AsientoForm(asiento)

		empresa = getNombreEmpresa()

		ruta = reverse('vEditarAsiento', {'_id':asiento.id})

		c = {'titulo':'Modificar Asiento Contable', 'seccion':'Contabilidad', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, 'Los campos con * son obligatorios.')

		return render(request, 'form_asiento.html', c)

	elif request.method == 'POST':

		form = forms.AsientoForm(request.POST, instance=asiento)

		if form.is_valid():

			form.save()

			messages.success(request, 'Los datos se actualizaron con éxito.')

			return redirect('detalle_asiento', {'_id':asiento.id})

		


@login_required
@permission_required('contabilidad.delete_detalleasiento')
def eliminar_detalle_asiento(request, _id):

	if request.method == 'POST':
		
		detalle = get_object_or_404(models.DetalleAsiento, pk=_id)
		
		id_asiento = detalle.asiento.id

		detalle.delete()

		messages.success(request, 'El registro se eliminó con éxito.')

		return redirect('ver_asiento', {'_id':id_asiento})





@login_required
@permission_required('contabilidad.view_ejercicio')
def lista_ejercicios(request, page=1):

	empresa = getNombreEmpresa()

	ejercicios = models.Ejercicio.objects.all()

	limite = settings.LIMITE_FILAS

	if ejercicios != None and ejercicios.count() > 0:

		paginador = Paginator(ejercicios)

		ejercicios = paginador.get_page(page)
		
		'''
		fecha = datetime.datetime.today()
		anio = "{0}".format(fecha.year)

		ejercicio = models.Ejercicio()

		ejercicio.ejercicio = anio
		ejercicio.descripcion = "Ejercicio contable " + anio
		ejercicio.activo = True

		ejercicio.save()

		ejercicios = models.Ejercicio.objects.all()'''

	c = {'titulo':'Ejercicios Contables', 'empresa':empresa, 'ejercicios':ejercicios, 'seccion':'Contabilidad'}

	return render(request, 'contabilidad/lista_ejercicios.html', c)




@login_required
@permission_required('contabilidad.add_ejercicio')
def nuevo_ejercicio(request):
	
	if request.method == "GET":
		
		empresa = getNombreEmpresa()

		ejercicio = models.Ejercicio()

		form = forms.EjercicioForm()

		ruta = reverse('vNuevoEjercicio')

		c = {'titulo':'Nuevo Ejercicio', 'seccion':'Ejercicios', 'empresa':empresa, 'form':form, 'ruta':ruta}

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":

		form = forms.EjercicioForm(request.POST)

		if form.is_valid():
			
			ejercicio = form.save(commit=False)

			'''
			if ejercicio.activo:
				activo = models.Ejercicio.objects.get(activo=True)
				activo.activo = False
				activo.save()
			'''

			ejercicio.save()

			return redirect('lista_ejercicios')



@login_required
@permission_required('contabilidad.view_ejercicio')
def ver_ejercicio(request, _id):

	ejercicio = get_object_or_404(models.Ejercicio, pk=_id)

	empresa = getNombreEmpresa()

	ruta_activar = reverse('vActivarEjercicio', {'_id':_id})

	ruta_edit = reverse('vEditarEjercicio', {'_id':_id})

	ruta_delete = reverse('vEliminarEjercicio', {'_id':_id})

	ruta_periodos = reverse('vCrearPeriodos', {'_id':_id})

	c = {'titulo':'Ejercicio Contable', 'seccion':'Contabilidad', 'empresa':empresa, 'ejercicio':ejercicio, 'ruta_activar':ruta_activar, 'ruta_edit':ruta_edit, 'ruta_periodos':ruta_periodos, 'ruta_delete':ruta_delete}

	return render(request, 'contabilidad/ver_ejercicio.html', c)


		
		
@login_required
@permission_required('contabilidad.change_ejercicio')
def activar_ejercicio(request, _id):

	ejercicio = get_object_or_404(models.Ejercicio, pk=_id)

	activo = models.Ejercicio.objects.get(activo=True)
	periodos_abiertos = activo.periodo_set.filter(cerrado=False)

	if periodos_abiertos.count() > 0:

		messages.error(request, 'Existen períodos contables abiertos en el ejercicio activo.')

		return redirect(reverse('vError'))

	activo.activo = False
	activo.save()

	ejercicio.activo = True
	ejercicio.save()

	return redirect('lista_ejercicios')



@login_required
@permission_required('contabilidad.add_periodo')
def crear_periodos(request, _id):

	ejercicio = get_object_or_404(models.Ejercicio, pk=_id)

	if not ejercicio.activo:
		
		messages.error(request, 'El ejercicio no ha sido activado.')

		return redirect(reverse('vError'))

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

	messages.success(request, 'Períodos generados con ésito.')

	return redirect('ver_ejercicio', {'_id':_id})


'''
@login_required
@permission_required('contabilidad.change_periodo')
def editar_periodo(request, _id):

	periodo = get_object_or_404(models.Periodo, pk=_id)

	if request.method == "GET":
		
		form = forms.PeriodoForm(periodo)

		empresa = getNombreEmpresa()

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


'''

'''

@login_required
@permission_required('contabilidad.delete_periodo')
def eliminar_periodo(request, _id):

	if request.method == "GET":

		empresa = getNombreEmpresa()

		c = {'empresa':empresa, 'titulo':'Eliminar Período', 'mensaje':'Se eliminará el registro de la base de datos.', 'view':'vEliminarPeriodo', '_id':_id, 'seccion':'Contabilidad'}
		
		return render(request, 'warning_template.html', c)

	elif request.method == "POST":
		
		periodo = get_object_or_404(models.Periodo, pk=id)

		periodo.delete()

		return redirect('lista_periodos')
'''



# Al activar un nuevo período, el período anterior es desactivado evitando que se registren transacciones
# con fechas que correspondan al período.

@login_required
@permission_required('contabilidad.change_periodo')
def activar_periodo(request, _id):

	if request.method == 'POST':

		periodo = get_object_or_404(models.Periodo, pk=_id)

		if periodo.activo:
			
			messages.info(request, 'El período ya se encuentra activo.')

			return redirect('ver_ejercicio', {'_id':periodo.ejercicio.id})

		periodo_ant = models.Periodo.objects.get(activo=True)

		periodo_ant.activo = False

		periodo.activo = True

		try:

			periodo_ant.save()

			periodo.save()

		
		except Exception as e:

			messages.error(request, 'Error al activar el período.')

			logging.error(e)

			return redirect(reverse('vError'))


		return redirect('ver_ejercicio', {'_id':periodo.ejercicio.id})

		




@login_required
@permission_required('contabilidad.contabilizar_asiento')
def contabilizar_periodo(request, _id):

	periodo = get_object_or_404(models.Periodo, pk=_id)

	if periodo.cerrado :
		
		messages.error(request, 'El periodo está cerrado. No se puede contabilizar.')

		return redirect(reverse('vError'))


	if request.method == "GET":
		
		empresa = getNombreEmpresa()

		cantidad_asientos = get_list_or_404(models.Asiento, fecha__gte=periodo.fecha_inicial, fecha__lte=periodo.fecha_final).count()

		ruta = reverse('vContabilizarPeriodo')

		c = {'titulo':'Contabilizar Asientos Por Período', 'seccion':'Contabilidad', 'empresa':empresa, 'periodo':periodo, 'ruta':ruta, 'cantidad_asientos':cantidad_asientos}

		messages.info(request, 'Los asientos con irregularidades o anulados no se contabilizarán.')

		return render(request, 'contabilidad/contabilizar.html', c)


	elif request.method == "POST":

		periodo = get_object_or_404(models.Periodo, pk=id)

		asientos = get_list_or_404(models.Asiento, fecha__gte=periodo.fecha_inicial, fecha__lte=periodo.fecha_final)

		contabilizados = 0

		no_contabilizados = 0

		for asiento in asientos:

			debitos = asiento.detalleasiento_set.filter(movimiento='db').aggregate(Sum('monto'))
			creditos = asiento.detalleasiento_set.filter(movimiento='cr').aggregate(Sum('monto'))

			if (debitos['monto_sum'] - creditos['monto_sum']) == 0.00:

				asiento.contabilizado = True

				asiento.save()

				contabilizados += 1

			else:

				no_contabilizados += 1


		if contabilizados > 0:
			
			messages.success(request, '{} asientos contabilizados y {} asientos no contabilizados'.format(contabilizados, no_contabilizados))

			if contabilizados == asientos.count():
				
				periodo.cerrado = True

				periodo.save()

				messages.success(request, 'Periodo de contabilidad cerrado con éxito.')
		
		else:

			messages.info(request, '{} asientos no fueron contabilizados.'.format(no_contabilizados))


		return redirect('index')



@login_required
@permission_required(['contabilidad.view_asiento','contabilidad.reporte_periodo'])
def reportes_rango(request, slug, inicio, final):
	return render(request, 'contabilidad/reporte_rango.html')


@login_required
@permission_required(['contabilidad.view_asiento','contabilidad.reporte_periodo'])
def reportes_periodo(request, slug, _id):
	return render(request, 'contabilidad/reporte_periodo.html')




'''
@login_required
@permission_required('contabilidad.change_periodo')
def cerrar_periodo(request, _id):

	if request.method == "GET":
		
		empresa = getNombreEmpresa()

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

		empresa = getNombreEmpresa()

		c = {'titulo':'Período Cerrado con Exito', 'seccion':'Contabilidad', 'empresa':empresa, 'view':'vIndexContabilidad'}

		return render(request, 'periodo_cerrado.html', c)

'''




	





	







