from django.urls import path, include
from . import views

app_name = 'contabilidad'

urlpatterns = [
	path('', views.index, name='vIndexContabilidad'),
	path('cuentas/', include([
		path('', views.lista_cuentas, name='vCatalogoCuentas'),
		path('<str:_id>/ver/', views.detalle_cuenta, name='vVerCuenta'),
		path('nueva/', views.nueva_cuenta, name='vNuevaCuenta'),
		path('<str:_id>/editar/', views.editar_cuenta, name='vEditarCuenta'),
		path('<str:_id>/cerrar/', views.cerrar_cuenta, name='vCerrarCuenta'),
		path('<str:_id>/eliminar/', views.eliminar_cuenta, name='vEliminarCuenta'),
		])),
	path('asientos/', include([
		path('page/<int:page>/', views.lista_asientos, name='vListaAsientos'),
		path('page/<int:page>/periodo/<int:_id>/', views.lista_asientos_periodo, name='vListaAsientosPeriodo'),
		path('page/<int:page>/fechas/<str:inicio>/<str:final>/', views.lista_asientos_rango, name='vAsientoPorFecha'),
		path('<int:_id>/ver/', views.ver_asiento, name='vVerAsiento'),
		path('nuevo/', views.nuevo_asiento, name='vNuevoAsiento'),
		path('<int:_id>/editar/', views.editar_asiento, name='vEditarAsiento'),
		path('<int:_id>/eliminar/', views.eliminar_asiento, name='vEliminarAsiento'),
		path('<int:_id>/anular/', vews.anular_asiento, name='vAnularAsiento'),
		path('<int:_id>/type<int:tipo>/detalle/', views.detalle_asiento, name='vDetalleAsiento'),
		path('detalle-asiento/<int:_id>/eliminar/', views.eliminar_detalle_asiento, name='vEliminarDetalleAsiento'),
		#path('<int:_id/detalle/editar/', views.editar_detalle_asiento, name='vEditarDetalleAsiento'),
		])),
	#path('contabilizar/<str:inicio>/<str:final>/', views.contabilizar_asientos, name='vContabilizarAsientos'),
	#path('contabilizar/periodo/', views.contabilizar_periodo, name='vContabilizarPeriodo'),
	path('ejercicios/', include([
			path('page/<int:page>/', views.lista_ejercicios, name='vListaEjercicios'),
			path('nuevo/', views.nuevo_ejercicio, name='vNuevoEjercicio'),
			path('<int:_id>/editar/', views.editar_ejercicio, name='vEditarEjercicio'),
			path('<int:_id>/eliminar/', views.eliminar_ejercicio, name='vEliminarEjercicio'),
			path('<int:_id>/activar/', views.activar_ejercicio, name='vActivarEjercicio'),
			path('<int:_id>/periodos/', views.crear_periodos, name='vCrearPeriodos'),
			#path('<int:_id>/periodos/nuevo/', views.nuevo_periodo, 'vNuevoPeriodo'),
			path('<int:_id>/periodos/crear', views.crear_periodos, name='vCrearPeriodos'),
		])),
	path('periodos/', include([
			#path('<int:_id>/ver/', views.ver_periodo, name='vVerPeriodo'),
			#path('nuevo/', views.nuevo_periodo, 'vNuevoPeriodo'),
			#path('<int:_id>/editar/', views.editar_periodo, name='vEditarPeriodo'),
			#path('<int:_id>/eliminar/', views.eliminar_periodo, name='vEliminarPeriodo'),
			path('<int:_id>/activar/', views.activar_periodo, name='vActivarPeriodo'),
			#path('<int:_id>/cerrar/', views.cerrar_periodo, name='vCerrarPeriodo'),
			path('<int:_id>/contabilizar/', views.contabilizar_periodo, name='vContabilizarPeriodo'),
		])),
	path('reportes/<slug:slug>/<str:inicio>/<str:final>/', views.reportes_rango, name='vReportesRango'),
	path('reportes/<slug:slug>/<int:_id>/', views.reportes_periodo, name='vReportesPeriodo'),
]