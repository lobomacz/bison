from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.conf import settings
from django.forms import formset_factory, modelformset_factory, inlineformset_factory
from django.contrib import messages
from django.contrib.auth import login_required, permission_required
from django.db import transaction
from django.db.models import Q, Sum
from bison.core.models import Empleado
from bison.contabilidad.models import Asiento
#from bison.inventario.models import Producto
from . import models, forms
import datetime, calendar, logging



# Create your views here.

# La página inicial de la sección llevará a las páginas de facturas y ordenes de ruta

@login_required
def index(request):

	if not request.user.groups.filter(name='Ventas').count() > 0:
		
		messages.warning(request, "No tiene acceso a esta sección.")

		return redirect(reverse('core:bisonIndex'))

	empresa = settings.NOMBRE_EMPRESA

	periodo = models.Periodo.objects.get(activo=True)

	c = {'titulo':'Menú de Ventas', 'seccion':'Ventas', 'empresa':empresa, 'periodo':periodo}
	
	return render(request, 'indice.html', c)




@login_required
@permission_required('ventas.view_proforma')
def lista_proformas(request, page=1, inicio=None, final=None):

	dias_vigencia = settings.VIGENCIA_PROFORMA

	today = datetime.date.today()

	tiempo_vigencia = datetime.timedelta(days=dias_vigencia)

	expire = today - tiempo_vigencia
	
	empresa = settings.NOMBRE_EMPRESA

	limite = settings.LIMITE_FILAS

	proformas = None

	c = {'titulo':'Listado de Proformas', 'seccion':'Ventas', 'empresa':empresa, 'page':page}

	usuario = request.user

	validas = models.Proforma.objects.filter(valida=True)

	if validas != None and validas.count() > 0:
		
		for proforma in validas:

			if proforma.fecha <= expire:
				
				proforma.valida = False

				proforma.save()

	if inicio == None and final == None:

		if usuario.has_perm('ventas.view_all_proforma'):
			
			proformas = models.Proforma.objects.all()

		else:
		
			proformas = models.Proforma.objects.filter(vendedor_id=usuario.empleado.id)

	else:

		if usuario.has_perm('ventas.view_all_proforma'):

			proformas = models.Proforma.objects.filter(fecha__gte=inicio, fecha__lte=final)

		else:

			proformas = models.Proforma.objects.filter(fecha__gte=inicio, fecha__lte=final, vendedor_id=usuario.empleado.id)

		c['inicio'] = inicio
		c['final'] = final

	if proformas.count() > limite:
		
		paginador = Paginator(proformas, limite)

		proformas = paginador.get_page(page)

	c['proformas'] = proformas

	return render(request, 'ventas/lista_proformas.html', c)




@login_required
@permission_required('ventas.view_proforma')
def ver_proforma(request, _id):

	proforma = get_object_or_404(models.Proforma, pk=_id)

	if (proforma.vendedor == request.user.empleado) or request.user.has_perm('ventas.view_all_proforma'):
		
		dias_vigencia = settings.VIGENCIA_PROFORMA

		today = datetime.date.today()

		tiempo_vigencia = datetime.timedelta(days=dias_vigencia)

		expire = today - tiempo_vigencia

		if proforma.fecha <= expire:
			
			proforma.vigente = False

			proforma.save()

		empresa = settings.NOMBRE_EMPRESA

		ruta_edit = reverse('vEditarProforma', kwargs={'_id':_id})

		ruta_anular = reverse('vAnularProforma', kwargs={'_id':_id})

		ruta_reemitir = reverse('vReemitirProforma', kwargs={'_id':_id})

		c = {'titulo':'Detalle de Proforma', 'seccion':'Ventas', 'proforma':proforma, 'ruta_edit':ruta_edit, 'ruta_anular':ruta_anular, 'ruta_reemitir':ruta_reemitir}

		return render(request, 'ventas/ver_proforma.html', c)

	else:

		messages.warning(request, "No tiene autorización para ver esta proforma.")

		return redirect('lista_proformas')



@login_required
@permission_required(['ventas.add_proforma', 'ventas.change_proforma', 'ventas.add_detalleproforma', 'ventas.change_detalleproforma'])
def detalle_proforma(request, _id):

	proforma = get_object_or_404(models.Proforma, pk=_id)

	if proforma.vendedor == request.user.empleado:

		extra_row = 4 if proforma.detalleproforma_set.all() != None else 10

		DetalleFormset = inlineformset_factory(models.Proforma, models.DetalleProforma, form=forms.fDetalleProforma, extra=extra_row)

		if request.method == "GET":

			empresa = settings.NOMBRE_EMPRESA

			formset = DetalleFormset(instance=proforma)

			ruta = reverse('vDetalleProforma', kwargs={'_id':_id})

			c = {'titulo':'Detalle de Proforma', 'seccion':'Ventas', 'empresa':empresa, 'proforma':proforma, 'formset':formset, 'ruta':ruta}

			messages.info(request, "Los campos con '*' son obligatorios.")

			return render(request, 'core/forms/inline_formset_template.html', c)

		elif request.method == "POST":

			formset = DetalleFormset(request.POST, request.FILES, instance=proforma)

			if formset.is_valid():

				subtotal = 0.00

				for form in formset.forms:

					detalle = form.save(commit=False)

					if detalle.precio_unit <= 0.00:
						
						detalle.precio_unit = detalle.producto.precio_unit

					# Mejorar con conversión de unidad de medida para el cálculo del total

					detalle.total = detalle.cantidad * detalle.precio_unit

					subtotal += detalle.total

					detalle.save()

				proforma.subtotal = subtotal

				monto_iva = settings.MONTO_IVA

				proforma.iva = subtotal * monto_iva

				proforma.total = proforma.subtotal + proforma.iva

				proforma.save()

				messages.success(request, 'Los datos se registraron con éxito.')

				return redirect('ver_proforma', {'_id':_id})

	else:

		messages.warning(request, "No tiene autorización para crear/editar el detalle de proforma.")

		return redirect('lista_proformas')

		


@login_required
@permission_required('ventas.add_proforma')
def nueva_proforma(request):

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		hoy = datetime.date.today()

		proforma = models.Proforma()

		proforma.fecha = hoy

		form = forms.fProforma(proforma)

		ruta = reverse('vNuevaProforma')

		c = {'titulo':'Ingreso de Proforma', 'seccion':'Ventas', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":

		form = forms.fProforma(request.POST)

		if form.is_valid():

			empleado = request.user.usuario.empleado if request.user.usuario != None else None
			
			proforma = form.save(commit=False)

			proforma.vendedor = empleado

			proforma.save()

			messages.success(request, 'Datos registrados con éxito.')

			messages.info(request, 'Ingrese el detalle de la proforma.')

			return redirect('detalle_proforma', {'_id':proforma.id})
		
		


#REDEFINIR LA LOGICA DE EDICION DE PROFORMA
@login_required
@permission_required('ventas.change_proforma')
def editar_proforma(request, _id):

	proforma = get_object_or_404(models.Proforma, pk=_id)

	if proforma.vendedor == request.user.empleado:

		if proforma.anulado == True or proforma.vigente == False:
			
			messages.error(request, 'La proforma fue anulada o no está vigente. No es posible editar.')

			return redirect('ver_proforma', {'_id':_id})

		dias_vigencia = settings.VIGENCIA_PROFORMA

		today = datetime.date.today()

		tiempo_vigencia = datetime.timedelta(days=dias_vigencia)

		expire = today - tiempo_vigencia

		if proforma.fecha <= expire:

			proforma.vigente = False

			proforma.save()
			
			messages.error(request, 'La proforma pasó el período de vigencia. No se puede modificar.')

			return redirect('ver_proforma', {'_id':_id})


		if request.method == "GET":
			
			empresa = settings.NOMBRE_EMPRESA

			form = forms.fProforma(proforma)

			ruta = reverse('vEditarProforma', kwargs={'_id':_id})

			c = {'titulo':'Editar Proforma', 'seccion':'Ventas', 'empresa':empresa, 'form':form, 'ruta':ruta}

			messages.info(request, "Los campos con '*' son obligatorios.")

			return render(request, 'core/forms/form_template.html', c)

		elif request.method == "POST":
			
			form = forms.fProforma(request.POST, instance=proforma)

			if form.is_valid():
				
				form.save()

				messages.success(request, 'Los datos se actualizaron con éxito.')

				messages.info(request, 'A continuación, actualizar el detalle de la proforma.')

				return redirect('detalle_proforma', {'_id':_id})

	else:

		messages.warning(request, "No tiene autorización para editar la proforma.")

		return redirect('lista_proformas')

		


@login_required
@permission_required(['ventas.add_proforma', 'ventas.change_proforma'])
def re_proforma(request, _id):

	if request.method == 'POST':

		proforma = get_object_or_404(models.Proforma, pk=_id)

		if proforma.vendedor == request.user.empleado:

			hoy = datetime.datetime.today()

			proforma.fecha = hoy

			proforma.pk = None

			proforma = proforma.save()

			messages.success(request, 'La proforma se ha reemitido con éxito.')

			return redirect('ver_proforma', {'_id':proforma.pk})

		else:

			messages.warning(request, "No tiene autorización para reemitir esta proforma.")

			return redirect('lista_proformas')




@login_required
@permission_required('ventas.anular_proforma')
def anular_proforma(request, _id):

	if request.method == "POST":

		proforma = get_object_or_404(models.Proforma, pk=_id)

		empleado = request.user.usuario.empleado if request.user.usuario != None else None

		proforma.anulado = True

		proforma.anulado_por = empleado

		proforma.save()

		messages.success(request, "La proforma se anuló con éxito.")

		return redirect('ver_proforma', {'_id':_id})



@login_required
@permission_required('ventas.view_factura')
def lista_facturas(request, page=1, inicio=None, final=None):

	facturas = None

	empresa = settings.NOMBRE_EMPRESA

	c = {'empresa':empresa, 'seccion':'Ventas', 'titulo':'Lista de Facturas', 'page':page}

	limite = settings.LIMITE_FILAS

	if inicio == None and final == None:
		
		periodo = models.Periodo.objects.get(activo=True)

		facturas = models.Factura.objects.filter(fecha__gte=periodo.fecha_inicio, fecha__lte=periodo.fecha_final)

		c['periodo'] = periodo

	else:

		facturas = models.Factura.objects.filter(fecha__gte=inicio, fecha__lte=final)

	if facturas.count() > limite:
		
		paginador = Paginator(facturas, limite)

		facturas = paginador.get_page(page)

		c['fecha_inicio'] = inicio
		c['fecha_final'] = final

	
	c['facturas'] = facturas

	return render(request, 'ventas/lista_facturas.html', c)




@login_required
@permission_required('ventas.view_factura')
def ver_factura(request, _id):

	factura = get_object_or_404(forms.Factura, pk=_id)

	empresa = settings.NOMBRE_EMPRESA

	params = {'_id':_id}

	ruta_edit = reverse('vEditarFactura', kwargs=params)

	ruta_cancelar = reverse('vCancelarFactura', kwargs=params)

	ruta_anular = reverse('vAnularFactura', kwargs=params)

	ruta_entregar = reverse('vEntregarFactura',kwargs=params)

	c = {'titulo':'Factura', 'seccion':'Ventas', 'factura':factura, 'empresa':empresa, 'ruta_edit':ruta_edit, 'ruta_cancelar':ruta_cancelar, 'ruta_entregar':ruta_entregar, 'ruta_anular':ruta_anular}

	return render(request, 'ventas/ver_factura.html', c)




@login_required
@permission_required(['ventas.add_factura', 'ventas.change_factura', 'ventas.change_detallefactura', 'ventas.add_detallefactura'])
def detalle_factura(request, _id, _ido=None):

	factura = get_object_or_404(models.Factura, pk=_id)

	extra_row = 4 if factura.detallefactura_set.all() != None else 10
	
	DetalleFormset = inlineformset_factory(models.Factura, models.DetalleFactura, form=forms.fDetalleFactura, extra=extra_row)

	if request.method == "GET":

		formset = DetalleFormset(instance=factura)

		empresa = settings.NOMBRE_EMPRESA

		ruta = reverse('vDetalleFactura', kwargs={'_id':_id})

		messages.info(request, "Los campos con '*' son obligatorios.")

		c = {'titulo':'Detalle de Factura', 'seccion':'Ventas', 'empresa':empresa, 'formset':formset, 'factura':factura, 'ruta':ruta}

		return render(request, 'core/forms/inline_formset_template.html', c)

	elif request.method == "POST":
		
		formset = DetalleFormset(request.POST, request.FILES, instance=factura)

		if formset.is_valid():

			try:

				with transaction.atomic():

					ordenruta = get_object_or_404(models.OrdenRuta, pk=_ido) if not _ido == None else None

					subtotal = 0.00

					for form in formset.forms:

						detalle = form.save(commit=False)

						if not detalle.precio_unit > 0.00:

							detalle.precio_unit = detalle.producto.precio_unit

						# Mejorar con la conversión de unidad de medida para calcular el total.

						detalle.total = detalle.cantidad * detalle.precio_unit

						subtotal += detalle.total

						if ordenruta != None:
							
							detalleOrden = ordenruta.detalleordenruta_set.filter(producto_id=detalle.producto.id)

							detalleOrden.cantidad_vendida += detalle.cantidad

							detalleOrden.costo_vendido += detalle.total

							detalleOrden.save()

						detalle.save()

					monto_iva = settings.MONTO_IVA

					factura.subtotal = subtotal

					factura.iva = factura.subtotal * monto_iva

					factura.total = factura.iva + factura.subtotal

					factura.save()

					messages.success(request, 'Los datos se registraron con éxito.')

					return redirect('ver_factura', {'_id':_id})

			except DatabaseError:

				messages.error("Ocurrió un problema al ingresar los datos. Intentelo de nuevo.")

				ruta = reverse('vDetalleFacturaOR', kwargs={'_id':_id, '_ido':_ido}) if _ido != None else reverse('vDetalleFactura', kwargs={'_id':_id})

				return redirect(ruta)



@login_required
@permission_required('ventas.delete_detallefactura')
def eliminar_detalle_factura(request, _id, _idd):

	if request.method == "POST":

		factura = get_object_or_404(models.Factura, pk=_id)

		if factura.cancelada or factura.anulada:
			
			messages.error(request, "No puede hacer modificaciones a esta factura.")

			return redirect('ver_factura', {'_id':_id})

		detalle = factura.detallefactura_set.get(_idd)

		detalle.delete()

		messages.success(request, "La línea de detalle se eliminó con éxito.")

		return redirect('detalle_factura', {'_id':_id})



@login_required
@permission_required('ventas.add_factura')
def nueva_factura(request):

	if request.method == "GET":

		hoy = datetime.date.today()
		
		form = forms.fFactura(initial={'fecha':hoy})

		empresa = settings.NOMBRE_EMPRESA

		ruta = reverse('vNuevaFactura')

		c = {'titulo':'Nueva Factura', 'seccion':'Ventas', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":

		form = forms.fFactura(request.POST)

		if form.is_valid():

			empleado = request.user.empleado #if request.user.empleado != None else None
			
			factura = form.save(commit=False)

			factura.vendedor = empleado

			factura.save()

			messages.success(request, 'Los datos se registraron con éxito.')

			messages.info(request, 'Se registrará el detalle de la factura.')
			
			return redirect('detalle_factura', {'_id':factura.id})		



@login_required
@permission_required('ventas.change_factura')
def editar_factura(request, _id):

	factura = get_object_or_404(models.Factura, pk=_id)

	if factura.cancelada or factura.anulada:
		
		messages.error(request, "No puede editar datos del registro.")

		return redirect('ver_factura', {'_id':_id})

	if request.method == "GET":

		form = forms.fFacturaEditar(factura)

		empresa = settings.NOMBRE_EMPRESA

		ruta = reverse('vEditarFactura', kwargs={'_id':_id})

		c = {'titulo':'Edición de Factura', 'seccion':'Ventas', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.fFacturaEditar(request.POST, instance=factura)

		if form.is_valid():
			
			form.save()

			messages.success(request, "El registro se actualizó con éxito.")

			messages.info(request, "A continuación, actualizar el detalle de la factura.")

			return redirect('detalle_factura', {'_id':_id})


'''
@login_required
@permission_required('ventas.cancelar_factura')
def detalle_asiento_factura(request, _id, _ida):
	
	factura = get_object_or_404(models.Factura, pk=_id)

	asiento = get_object_or_404(models.Asiento, pk=_ida)



@login_required
@permission_required('ventas.cancelar_factura')
def asiento_factura(request, _id):
	
	factura = get_object_or_404(models.Factura, pk=_id)

	if request.method == 'GET':
		pass
	elif request.method == 'POST':
		pass
'''


# TODO: Como proceder para registrar el asiento al cancelar factura de contado
# y al ingresar factura al crédito?


@login_required
@permission_required('ventas.cancelar_factura')
def cancelar_factura(request, _id):

	if request.method == "POST":

		factura = get_object_or_404(models.Factura, pk=_id)

		if factura.asiento == None || factura.asiento.detalleasiento_set.all().count() == 0:

			asiento = None

			if factura.asiento == None:

				fecha = datetime.date.today()

				descripcion = "Venta de producto al contado" 

				asiento = Asiento()

				asiento.fecha = fecha 

				asiento.descripcion = descripcion

				asiento.referencia = "Factura No.{}".format(factura.id)

				asiento.observaciones = "Documento No. {}".format(factura.no_documento)

				with transaction.atomic():

					asiento.save()

					factura.asiento = asiento

					factura.save()

			else:

				asiento = factura.asiento

			messages.info(request, "Ingrese el detalle del asiento contable.")

			ruta = reverse('contabilidad:vDetalleAsiento', kwargs={'_id':asiento.id, 'tipo':2})

			return redirect(ruta) #redirect(reverse('vDetalleAsiento', kwargs={'_id':asiento.id, 'tipo':2}))

		else:

			factura.cancelada = True

			factura.save()

			messages.success(request, "Factura cancelada.")

			return redirect('ver_factura', {'_id':_id})



@login_required
@permission_required('ventas.asiento_factura')
def asiento_factura(request, _id):
	
	factura = get_object_or_404(models.Factura, pk=_id)

	if factura.tipo != 'cr':
		
		messages.info(request, "Debe proceder a cancelar la factura.")

		return redirect('ver_factura', {'_id':_id})

	asiento = None

	if factura.asiento == None:

		fecha = datetime.date.today()

		descripcion = "Venta de producto al crédito"

		asiento = Asiento()

		asiento.fecha = fecha 

		asiento.descripcion = descripcion

		asiento.referencia = "Factura No.{}".format(factura.id)

		asiento.observaciones = "Documento No. {}".format(factura.no_documento)

		with transaction.atomic():

			asiento.save()

			factura.asiento = asiento

			factura.save()

	else:

		asiento = factura.asiento

	messages.info(request, "Ingrese el detalle del asiento contable.")

	ruta = reverse('contabilidad:vDetalleAsiento', kwargs={'_id':asiento.id, 'tipo':3})

	return redirect(ruta)




@login_required
@permission_required('ventas.anular_factura')
def anular_factura(request, _id):
	
	if request.method == "POST":
		
		factura = get_object_or_404(models.Factura, pk=_id)

		if factura.cancelada:
			
			messages.error(request, "La factura está cancelada. No se puede anular.")

			return redirect('ver_factura', {'_id':_id})

		empleado = request.user.empleado

		fecha = datetime.date.today()

		factura.anulada_por = empleado

		factura.fecha_anulada = fecha

		factura.anulada = True

		factura.save()

		if factura.asiento != None:
			
			asiento = factura.asiento

			asiento.anulado = True

			asiento.anulado_por = request.user.empleado

			asiento.fecha_anulado = datetime.date.today()

			asiento.save()

		messages.success(request, "La factura ha sido anulada.")

		return redirect('ver_factura', {'_id':_id})



@login_required
@permission_required('ventas.view_cliente')
def clientes(request, page=1):

	empresa = settings.NOMBRE_EMPRESA

	ruta = reverse('vBuscarCliente')

	if request.method == "GET":
	
		clientes = models.Cliente.objects.all() #get_list_or_404(models.Cliente)

		limite = settings.LIMITE_FILAS

		if clientes.count() > limite:
			
			paginador = Paginator(clientes, limite)

			clientes = paginador.get_page(page)

		c = {'titulo':'Lista de Clientes', 'seccion':'Ventas', 'empresa':empresa, 'clientes':clientes, 'page':page, 'ruta':ruta}

		return render(request, 'ventas/lista_clientes.html', c)

	elif request.method == "POST":

		cliente_id = request.POST['cliente_id']

		return redirect('ver_cliente', {'_id':cliente_id})




@login_required
@permission_required('ventas.view_cliente')
def ver_cliente(request, _id):

	cliente = get_object_or_404(models.Cliente, pk=cliente_id)

	ruta_edit = reverse('vEditarCliente', kwargs={'_id':cliente_id})

	c = {'titulo':'Datos de Cliente', 'seccion':'Ventas', 'empresa':empresa, 'cliente':cliente, 'ruta_edit':ruta_edit}

	return render('ventas/ver_cliente.html', c)




@login_required
@permission_required('ventas.add_cliente')
def nuevo_cliente(request):

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		form = forms.fCliente()

		ruta = reverse('vNuevoCliente')

		c = {'titulo':'Ingreso de Clientes', 'seccion':'Ventas', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.fCliente(request.POST)

		if form.is_valid():
			
			cliente = form.save(commit=False)

			cliente.save()

			messages.success(request, "El cliente se registró con éxito.")

			return redirect('ver_cliente', {'_id':cliente.id})



@login_required
@permission_required('ventas.change_cliente')
def editar_cliente(request, _id):

	cliente = get_object_or_404(_id)

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		form = forms.fCliente(cliente)

		ruta = reverse('vEditarCliente', kwargs={'_id':cliente.id})

		c = {'titulo':'Editar Datos de Cliente', 'seccion':'Ventas', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.fCliente(request.POST, instance=cliente)

		if form.is_valid():
			
			form.save()

			messages.success(request, "Los datos se actualizaron con éxito.")

			return redirect('ver_cliente', {'_id':cliente.id})




@login_required
@permission_required('ventas.view_ordenruta')
def lista_ordenes_ruta(request, page=1):

	limite = settings.LIMITE_FILAS
	
	ordenes = models.OrdenRuta.objects.filter(liquidado=False, anulado=False)

	if ordenes.count() > limite:
		
		paginador = Paginator(ordenes, limite)

		ordenes = paginador.get_page(page)

	empresa = settings.NOMBRE_EMPRESA

	c = {
	'titulo':'Lista de Ordenes de Ruta', 
	'seccion':'Ventas', 
	'empresa':empresa, 
	'ordenes':ordenes, 
	'page':page
	}

	return render(request, 'ventas/lista_ordenes_ruta.html', c)
	



@login_required
@permission_required('ventas.view_ordenruta')
def ver_orden_ruta(request, _id):

	orden = get_object_or_404(models.OrdenRuta, pk=_id)

	empresa = settings.NOMBRE_EMPRESA

	params = {'_id':_id}

	ruta_edit = reverse('vEditarOrdenRuta', kwargs=params)

	ruta_anular = reverse('vAnularOrdenRuta', kwargs=params)

	ruta_entregar = reverse('vEntregarOrdenRuta', kwargs=params)

	ruta_autorizar = reverse('vAutorizarOrdenRuta', kwargs=params)

	ruta_liquidar = reverse('vLiquidarOrdenRuta', kwargs=params)

	c = {
	'titulo':'Orden de Ruta', 
	'seccion':'Ventas', 
	'empresa':empresa, 
	'orden':orden, 
	'ruta_edit':ruta_edit, 
	'ruta_anular':ruta_anular, 
	'ruta_autorizar':ruta_autorizar, 
	'ruta_liquidar':ruta_liquidar,
	'ruta_entregar':ruta_entregar
	}

	return render(request, 'ventas/ver_orden_ruta.html', c)



@login_required
@permission_required(['ventas.add_detalleordenruta', 'ventas.change_detalleordenruta'])
def detalle_orden_ruta(request, _id):
	
	orden = get_object_or_404(models.OrdenRuta, pk=_id)

	if orden.autorizado or orden.anulado or orden.liquidado:

		ruta = reverse('vVerOrdenRuta', kwargs={'_id':_id})

		messages.error(request, 'No se puede modificar el detalle de la orden de ruta.')
		
		return redirect(ruta) #render(request, 'error.html', {'titulo':'Error de Acceso', 'seccion':'Ventas', 'empresa':settings.NOMBRE_EMPRESA, 'mensaje':'La orden de ruta no puede ser modificada.', 'view':'vListaOrdenesRuta'})

	extra_row = 4 if orden.detalleordenruta_set.count() > 0 else 10

	DetalleFormset = inlineformset_factory(models.OrdenRuta, models.DetalleOrdenRuta, form=forms.fDetalleOrdenRuta, extra=extra_row)

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		formset = DetalleFormset(instance=orden)

		ruta = reverse('vDetalleOrdenRuta', kwargs={'_id':_id})

		c = {'titulo':'Detalle de Orden de Ruta', 'seccion':'Ventas', 'empresa':empresa, 'formset':formset, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/inline_formset_template.html', c)

	elif request.method == "POST":
		
		formset = DetalleFormset(request.POST, request.FILES, instance=orden)

		if formset.is_valid():

			for form in formset.forms:
				
				detalle = form.save(commit=False)

				detalle.total = detalle.producto.precio_unit * detalle.cantidad_entregada

				detalle.save()

			messages.success(request, "Los datos se registraron con éxito.")

			return redirect('ver_orden_ruta', {'_id':_id})
		



@login_required
@permission_required('ventas.add_ordenruta')
def nueva_orden_ruta(request):

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		fecha_actual = datetime.date.today()

		form = forms.fOrdenRuta(initial={'fecha':fecha_actual})

		ruta = reverse('vNuevaOrdenRuta')

		c = {'titulo':'Nueva Orden de Ruta', 'seccion':'Ventas', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.fOrdenRuta(request.POST)

		if form.is_valid():
			
			orden = form.save(commit=False)

			orden.digitador = request.user.empleado

			orden.save()

			messages.success(request, "Los datos se registraron con éxito.")

			messages.info(request, "A continuación, ingresar el detalle de la orden.")

			return redirect('detalle_orden_ruta', {'_id':orden.id})

		


@login_required
@permission_required('ventas.change_ordenruta')
def editar_orden_ruta(request, _id):

	orden = get_object_or_404(models.OrdenRuta, pk=_id)

	if request.method == "GET":

		form = forms.fEditOrdenRuta(orden)

		empresa = settings.NOMBRE_EMPRESA

		ruta = reverse('vEditarOrdenRuta', kwargs={'_id':_id})

		c = {'titulo':'Editar Orden de Ruta', 'seccion':'Ventas', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.fOrdenRuta(request.POST, instance=orden)

		if form.is_valid():
			
			form.save()

			messages.success(request, "Orden modificada con éxito.")

			messages.info(request, "A continuación editar detalle de la orden.")

			return redirect('detalle_orden_ruta', {'_id':orden.id})

		


@login_required
@permission_required('ventas.autorizar_ordenruta')
def autorizar_orden_ruta(request, _id):

	if request.method == "POST":
	
		orden = get_object_or_404(models.OrdenRuta, pk=_id)

		if orden.anulado:
			
			messages.error(request, "La orden está anulada. No se puede autorizar.")

			return redirect('ver_orden_ruta', {'_id':_id})


		if not orden.autorizado:

			orden.autorizado = True

			orden.autorizado_por = request.user.empleado

			orden.save()

			messages.success(request, "Orden autorizada con éxito.")

		else:

			messages.warning(request, "La orden ya ha sido autorizada.")

		return redirect('ver_orden_ruta', {'_id':_id})



@login_required
@permission_required('ventas.facturar_ordenruta')
def facturar_or_detalle(request, _id):
	pass



@login_required
@permission_required('ventas.facturar_ordenruta')
def facturar_orden_ruta(request, _id):

	ordenruta = get_object_or_404(models.OrdenRuta, pk=_id)

	if request.method == 'GET':

		vendedor = ordenruta.vendedor

		form = forms.fFacturaOrdenRuta(initial={
				'vendedor':vendedor.empleado,
			})

		ruta = reverse('vFacturarOrdenRuta', kwargs={'_id':_id})

		empresa = settings.NOMBRE_EMPRESA

		c = {'titulo':'Factura de Orden de Ruta', 'seccion':'Ordenes de Ruta', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == 'POST':

		form = forms.fFacturaOrdenRuta(request.POST)

		if form.is_valid():
			
			datosOrden = form.cleaned_data

			cliente = models.Cliente.objects.get(id=datosOrden.cliente)

			factura = models.Factura()

			factura.fecha = datosOrden['fecha']
			factura.cliente = cliente
			factura.no_documento = datosOrden['no_documento']
			factura.vendedor = ordenruta.vendedor
			factura.tipo = datosOrden['tipo']
			factura.tipo_pago = datosOrden['tipo_pago']
			factura.descuento = datosOrden['descuento']

			factura.save()

			messages.info(request, "A continuación, ingrese el detalle de la factura.")

			return redirect('detalle_factura', {'_id':factura.id, '_ido':_id})


	


@login_required
@permission_required('ventas.delete_ordenruta')
def eliminar_orden_ruta(request, _id):

	if request.method == "POST":
	
		orden = get_object_or_404(models.OrdenRuta, pk=_id)

		if orden.autorizado or orden.entregado:

			messages.error(request, "La orden ya fue autorizada/entregada. No puede se puede eliminar hasta ser liquidada.")
			
			return redirect('ver_orden_ruta', {'_id':_id}) 

		else:

			orden.delete()

			messages.error(request, "La orden se eliminó con éxito.")

			return redirect('lista_ordenes_ruta')




@login_required
@permission_required('ventas.delete_detalleordenruta')
def eliminar_detalle_orden_ruta(request, _id, _idd):
	
	orden = get_object_or_404(models.OrdenRuta, pk=_id)

	if orden.autorizado or orden.anulado:

		messages.error(request, "Orden autorizada o anulada. No puede eliminar el detalle.")
		
		return redirect('ver_orden_ruta', {'_id':_id})#render(request, 'error.html', {'titulo':'Error!', 'seccion':'Ventas', 'mensaje':'No se puede eliminar la línea de detalle.', 'view':'vListaOrdenesRuta'})

	else:
			
		detalle = orden.detalleordenruta_set.filter(_idd)

		detalle.delete()

		messages.success(request, "Detalle eliminado con éxito.")

		return redirect('ver_orden_ruta', {'_id':_id})



@login_required
@permission_required('ventas.view_vendedor')
def lista_vendedores(request, page=1):

	empresa = settings.NOMBRE_EMPRESA

	vendedores = models.Vendedor.objects.all() #get_list_or_404(models.Vendedor)

	limite = settings.LIMITE_FILAS

	if vendedores.count() > limite:
		
		paginador = Paginator(vendedores, limite)

		vendedores = paginador.get_page(page)

	c = {'titulo':'Lista de Vendedores', 'seccion':'Ventas', 'vendedores':vendedores, 'empresa':empresa, 'page':page}

	return render(request, 'ventas/lista_vendedores.html', c)



@login_required
@permission_required('ventas.view_vendedor')
def ver_vendedor(request, _id):

	vendedor = get_object_or_404(models.Vendedor, pk=_id)

	empresa = settings.NOMBRE_EMPRESA

	params = {'_id':_id}

	ruta_edit = reverse('vEditarVendedor', kwargs=params)

	ruta_desactivar = reverse('vDesactivarVendedor', kwargs=params)

	c = {'titulo':'Datos de Vendedor', 'seccion':'Ventas', 'vendedor':vendedor, 'empresa':empresa, 'ruta_edit':ruta_edit, 'ruta_desactivar':ruta_desactivar}

	return render(request, 'ventas/ver_vendedor.html', c)


@login_required
@permission_required('ventas.add_vendedor')
def nuevo_vendedor(request):

	if request.method == "GET":
		
		ruta = reverse('vNuevoVendedor')

		empresa = settings.NOMBRE_EMPRESA

		form = forms.fVendedor()

		c = {'titulo':'Ingreso de Vendedor', 'seccion':'Ventas', 'empresa':empresa, 'form':form, 'ruta':ruta}

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.fVendedor(request.POST)

		if form.is_valid():

			vendedor = form.save(commit=False)

			vendedor.save()

			messages.success(request, "Los datos se registraron con éxito.")

			return redirect('ver_vendedor', {'_id':_id})



@login_required
@permission_required('ventas.change_vendedor')
def editar_vendedor(request, _id):

	vendedor = get_object_or_404(models.Vendedor, pk=_id)

	if vendedor.desactivado:
		
		messages.error(request, "El registro ha sido desactivado. No puede modificarse.")

		return redirect('ver_vendedor', {'_id':_id})

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		form = forms.fVendedor(vendedor)

		ruta = reverse('vEditarVendedor', kwargs={'_id':_id})

		c = {'titulo':'Editar Datos de Vendedor', 'seccion':'Ventas', 'form':form, 'empresa':empresa, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.fVendedor(request.POST, instance=vendedor)

		if form.is_valid():
			
			form.save()

			messages.success(request, "Los datos se actualizaron con éxito.")

			return redirect('ver_vendedor', {'_id':_id})



@login_required
@permission_required('ventas.desactivar_vendedor')
def desactivar_vendedor(request, _id):

	if request.method == "POST":
		
		vendedor = get_object_or_404(models.Vendedor, pk=_id)

		if not vendedor.activo:
			
			messages.warning(request, "El vendedor ya no es activo.")

			return redirect('ver_vendedor',{'_id':_id})

		vendedor.activo = False

		'''

		user = vendedor.empleado.user

		if user != None:
			
			user.is_active = False

			user.save()

		'''

		vendedor.save()

		messages.success(request, "El vendedor se ha desactivado.")

		return redirect('ver_vendedor', {'_id':_id})




@login_required
@permission_required('ventas.view_ruta')
def lista_rutas(request):

	rutas = models.Ruta.objects.all() #get_list_or_404(models.Ruta)

	empresa = settings.NOMBRE_EMPRESA

	c = {'titulo':'Listado de Rutas', 'seccion':'Ventas', 'empresa':empresa, 'rutas':rutas}

	return render(request, 'ventas/lista_rutas.html', c)



@login_required
@permission_required('ventas.view_ruta')
def ver_ruta(request, _id):

	ruta = get_object_or_404(models.Ruta, pk=_id)

	empresa = settings.NOMBRE_EMPRESA

	params = {'_id':_id}

	ruta_edit = reverse('vEditarRuta', kwargs=params)

	ruta_delete = reverse('vEliminarRuta', kwargs=params)

	c = {'titulo':'Datos de la Ruta', 'seccion':'Ventas', 'empresa':empresa, 'ruta':ruta, 'ruta_edit':ruta_edit, 'ruta_delete':ruta_delete}

	return render(request, 'ventas/ver_ruta.html', c)



@login_required
@permission_required('ventas.add_ruta')
def nueva_ruta(request):

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		form = forms.fRuta()

		ruta = reverse('vNuevaRuta')

		c = {'titulo':'Ingreso de Ruta', 'seccion':'Ventas', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":

		form = forms.fRuta(request.POST)

		if form.is_valid():
			
			ruta = form.save(commit=False)

			ruta.save()

			messages.success(request, "Los datos se registraron con éxito.")

			return redirect('ver_ruta', {'_id':ruta.id})
		



@login_required
@permission_required('ventas.change_ruta')
def editar_ruta(request, _id):

	registro = get_object_or_404(models.Ruta, pk=_id)

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		form = forms.fRuta(registro)

		ruta = reverse('vEditarRuta', kwargs={'_id':_id})

		c = {'titulo':'Editar Datos de Ruta', 'seccion':'Ventas', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":

		form = forms.fRuta(request.POST, instance=registro)

		if form.is_valid():
			
			ruta = form.save(commit=False)

			messages.success(request, "Los datos se actualizaron con éxito.")

			return redirect('ver_ruta', {'_id':_id})




@login_required
@permission_required('ventas.delete_ruta')
def eliminar_ruta(request, _id):

	ruta = get_object_or_404(models.Ruta, pk=_id)

	ruta.delete()

	messages.success(request, "El registro se eliminó con éxito.")

	return redirect('lista_rutas')



@login_required
@permission_required('core.view_camion')
def lista_camiones(request):

	camiones = models.Camion.objects.all()

	empresa = settings.NOMBRE_EMPRESA

	c = {'titulo':'Lista de Camiones', 'seccion':'Camiones' 'empresa':empresa, 'camiones':camiones}

	return render(request, 'core/lista_camiones.html', c)



@login_required
@permission_required('core.view_camion')
def ver_camion(request, _id):

	camion = get_object_or_404(models.Camion, pk=_id)

	empresa = settings.NOMBRE_EMPRESA

	params = {'_id':_id}

	ruta_edit = reverse('vEditarCamion', kwargs=params)

	ruta_delete = reverse('vEliminarCamion', kwargs=params)

	c = {'titulo':'Datos de Camión', 'seccion':'Camiones', 'empresa':empresa, 'camion':camion, 'ruta_edit':ruta_edit, 'ruta_delete':ruta_delete}

	return render(request, 'ver_camion.html', c)


@login_required
@permission_required('core.add_camion')
def nuevo_camion(request):

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		form = forms.fCamion()

		ruta = reverse('vNuevoCamion')

		c = {'titulo':'Ingreso de Camion', 'seccion':'Camiones', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.fCamion(request.POST)

		if form.is_valid():
			
			camion = form.save(commit=False)

			camion.save()

			messages.success(request, "Los datos se registraron con éxito.")

			return redirect('ver_camion', {'_id':camion.id})


@login_required
@permission_required('core.change_camion')
def editar_camion(request, _id):

	camion = get_object_or_404(models.Camion, pk=_id)

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		form = forms.fCamion(camion)

		ruta = reverse('vEditarCamion', kwargs={'_id':_id})

		c = {'titulo':'Editar Datos de Camion', 'seccion':'Camiones', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.fCamion(request.POST, instance=camion)

		if form.is_valid():
			
			form.save()

			messages.success(request, "Los datos se actualizaron con éxito.")

			return redirect('ver_camion', {'_id':_id})



@login_required
@permission_required('core.delete_camion')
def eliminar_camion(request, _id):

	if request.method == "POST":
		
		camion = get_object_or_404(models.Camion, pk=_id)

		camion.delete()

		messages.success(request, "El registro se eliminó con éxito.")

		return redirect('lista_camiones')





'''

@login_required
def error(request):

	return render(request, 'core/error.html')


'''





















