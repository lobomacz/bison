from django.urls import path, include
from . import views

app_name = 'inventario'

urlspatterns = [
	path('', views.index, name='vIndexInventario'),
	path('almacen/', include([
		path('', views.almacenes, name='vListaAlmacen'),
		path('<int:_id>/ver/', views.almacen, name='vDetalleAlmacen'),
		path('nuevo/', views.nuevo_almacen, name='vNuevoAlmacen'),
		path('<int:_id>/editar/', views.editar_almacen, name='vEditarAlmacen'),
		path('<int:_id>/eliminar/', views.eliminar_almacen, name='vEliminarAlmacen'),
		])),
	path('entradas/', include([
		path('page/<int:page>/', views.entradas, name='vListaEntradas'),
		path('almacen/page/<int:page>/', views.entradas, name='vListaEntradasAlmacen'),
		path('nueva/', views.form_entrada, name='vNuevaEntrada'),
		path('<int:id>/ver/', views.entrada, name='vVerEntrada'),
		path('<int:_id>/editar/', views.form_entrada, name='vEditarEntrada'),
		path('<int:_id>/eliminar/', views.eliminar_entrada, name='vEliminarEntrada'),
		path('<int:_id>/asiento/<str:tipo>/', views.asiento, name='vAsientoEntrada'),
		path('<int:_id>/detalle/', views.detalle_entrada, name='vDetalleEntrada'),
		path('filtro/page/<int:page>/', views.entradas_filtro, name='vEntradasFiltro'),
		])),
	path('detalle-entrada/<int:_id>/eliminar/', views.eliminar_detalleEntrada, name='vEliminarDetalleEntrada'),
	path('salidas/', include([
		path('page/<int:page>/', views.salidas, name='vListaSalidas'),
		path('almacen/<int:_id>/page/<int:page>/', views.salidas, name='vListaSalidasAlmacen'),
		path('<int:_id>/ver/', views.listaSalidasAlmacen, name='vListaSalidasAlmacen'),
		path('nueva/', views.form_salida, name='vNuevaSalida'),
		path('<int:_id>/ver/', views.salida, name='vVerSalida'),
		path('<int:_id>/editar/', views.form_salida, name='vEditarSalida'),
		path('<int:_id>/eliminar/', views.eliminar_salida, name='vEliminarSalida'),
		path('<int:_id>/asiento/<str:tipo>/', views.asiento, name='vAsientoSalida'),
		path('<int:_id>/detalle/', views.detalle_salida, name='vDetalleSalida'),
		path('almacen/<int:id>/fecha/', views.salidas_por_fecha, name='vSalidasPorFecha'),
		path('almacen/<int:id>/rango/', views.salidas_por_rango, name='vSalidasPorRango'),
		])),
	path('detalle-salida/<int:_id>/eliminar/', views.eliminar_detalleSalida, name='vEliminarDetalleSalida'),
	path('traslados/', include([
		path('page/<int:page>/', views.traslados, name='vListaTraslados'),
		path('nuevo/', views.form_traslado, name='vNuevoTraslado'),
		path('<int:_id>/ver/', views.traslado, name='vVerTraslado'),
		path('<int:_id>/editar/', views.form_traslado, name='vEditarTraslado'),
		path('<int:_id>/eliminar/', views.eliminar_traslado, name='vEliminarTraslado'),
		path('<int:_id>/asiento/<str:tipo>/', views.asiento, name='vAsientoTraslado'),
		path('<int:_id>/detalle/', views.detalle_traslado, name='vDetalleTraslado'),
		])),
	path('detalle-traslado/<int:_id>/eliminar/', views.eliminar_detalleTraslado, name='vEliminarDetalleTraslado'),
]