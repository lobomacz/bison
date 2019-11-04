from django.urls import path, include
from . import views

app_name = 'contabilidad'

urlpatterns = [
	path('', views.index, name='vIndexContabilidad'),
	path('cuentas/', include([
		path('', views.lista_cuentas, name='vListaCuentas'),
		path('nueva/', views.nueva_cuenta, name='vNuevaCuenta'),
		path('editar/<str:_id>/', views.editar_cuenta, name='vEditarCuenta'),
		path('cerrar/<str:_id>/', views.cerrar_cuenta, name='vCerrarCuenta'),
		path('eliminar/<str:_id>/', views.eliminar_cuenta, name='vEliminarCuenta'),
		])),
	path('asientos/', include([
		path('', views.indice_asientos, name='vIndexAsientos'),
		path('periodo/<int:id_periodo>/', views.indice_asientos, name='vAsientosPeriodo'),
		path('fechas/<str:inicio>/<str:final>/', views.indice_asientos, name='vAsientoPorFecha'),
		#path('lista/<str:inicio>/<str:final>/', views.listaAsientos, name='vListaAsientos'),
		path('anulados/<str:inicio>/<str:final>/', views.asientos_anulados, name='vAsientosAnulados'),
		path('ver/<int:id>/', views.ver_asiento, name='vDetalleAsiento'),
		path('nuevo/', views.nuevo_asiento, name='vNuevoAsiento'),
		path('editar/<int:_id>/', views.editar_asiento, name='vEditarAsiento'),
		path('eliminar/<int:_id>/', views.eliminar_asiento, name='vEliminarAsiento'),
		path('<int:_id>/detalle/nuevo/', views.editar_asiento, name='vNuevoDetalleAsiento'),
		#path('<int:id_asiento>/detalle/ver/', views.verDetalleAsiento, name='vVerDetalleAsiento'),
		#path('<int:id_asiento>/detalle/editar/', views.editarDetalleAsiento, name='vEditarDetalleAsiento'),
		path('detalle/<int:_id/eliminar/', views.eliminar_detalle_asiento, name='vEliminarDetalleAsiento'),
		#path('factura/', views.asientoDeFactura, name='vAsientoDeFactura'),
		])),
	#path('contabilizar/<str:inicio>/<str:final>/', views.contabilizar_asientos, name='vContabilizarAsientos'),
	path('contabilizar/periodo/<int:id>/', views.contabilizar_periodos, name='vContabilizarPeriodos'),
	path('reportes/<slug:slug>/<str:inicio>/<str:final>/', views.reportes_rango, name='vReportesRango'),
	path('reportes/<slug:slug>/<int:id_periodo>/', views.reportes_periodo, name='vReportesPeriodo'),
	path('ejercicios/', include([
			path('', views.lista_ejercicios, name='vListaEjercicios'),
			path('nuevo/', views.nuevo_ejercicio, name='vNuevoEjercicio'),
			path('<int:_id>/activar/', views.activar__id, name='vActivarEjercicio')
			path('<int:_id>/periodos/', views.lista_periodos, name='vListaPeriodos'),
			path('<int:_id>/periodos/crear', views.crear_periodos, name='vCrearPeriodos'),
		])),
	path('periodos/', include([
			path('<int:_id>/editar/', views.editar_periodo, name='vEditarPeriodo'),
			path('<int:_id>/eliminar/', views.eliminar_periodo, name='vEliminarPeriodo'),
			path('<int:_id>/activar/', views.activar_periodo, name='vActivarPeriodo'),
			path('<int:_id>/cerrar/', views.cerrar_periodo, name='vCerrarPeriodo'),
		])),
]