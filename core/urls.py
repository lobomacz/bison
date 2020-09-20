from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'core'

urlpatterns = [
	path('', views.index, name='bisonIndex'),
	path('login/', views.bison_login, name='bisonLogin'),
	path('logout/', views.bison_logout, name='bisonLogout'),
	path('empleados/', include([
		path('page/<int:page>/', views.lista_empleados, name='vListaEmpleados'),
		path('page/<int:page>/todos/', views.lista_empleados, {'todos':True}, name='vTodosEmpleados'),
		path('<str:_id>/ver/', views.ver_empleado, name='vVerEmpleado'),
		path('nuevo/', views.nuevo_empleado, name='vNuevoEmpleado'),
		path('nuevo/usuario/', views.nuevo_empleado_usuario, name='vNuevoEmpleadoUsuario'),
		path('<str:_id>/editar/', views.editar_empleado, name='vEditarEmpleado'),
		path('<str:_id>/eliminar/', views.eliminar_empleado, name='vEliminarEmpleado'),
		path('<str:_id>/desactivar/', views.desactiva_empleado, name='vDesactivarEmpleado'),
		path('<str:_id>/asignar-usuario/', views.asignar_usuario, name='vAsignarUsuario'),
		])),
	path('usuarios/', include([
		path('page/<int:page>/', views.lista_usuarios, name='vListaUsuarios'),
		path('nuevo/', views.nuevo_usuario, name = 'vNuevoUsuario'),
		path('<int:_id>/editar/', views.editar_usuario, name='vEditarUsuario'),
		path('password/change/', views.password_user_change, name='vCambiarPassword'),
		path('<int:_id>/eliminar/', views.eliminar_usuario, name='vEliminarUsuario'),
		path('<int:_id>/desactivar/', views.desactivar_usuario, name='vDesactivaUsuario'),
		])),
	path('tablas/', include([
		path('', views.tablas, name='vTablas'),
		path('nuevo/', views.nueva_tabla, name='vNuevaTabla'),
		path('<int:_id>/editar/', views.tablas, name='vEditarTabla'),
		path('<int:_id>/actualizar/', views.update_tabla, name='vUpdateTabla'),
		path('<int:_id>/eliminar/', views.eliminar_tabla, name='vEliminarTabla'),
		])),
	path('detalle-tabla/', include([
		path('<int:_id>/nuevo/', views.nuevo_detalle_tabla, name='vNuevoDetalleTabla'),
		path('<int:_idd>/editar/', views.tablas, name='vEditarDetalleTabla'),
		path('<int:_id>/actualizar/', views.update_detalle_tabla, name='vUpdateDetalleTable'),
		path('<int:_id>/eliminar/', views.eliminar_detalle_tabla, name='vEliminarDetalleTabla'),
		])),
	path('productos/', include([
		path('page/<int:page>/', views.lista_productos, name='vListaProductos'),
		path('<int:_id>/ver/', views.ver_producto, name='vVerProducto'),
		path('nuevo/', views.nuevo_producto, name='vNuevoProducto'),
		path('<int:_id>/editar/', views.editar_producto, name='vEditarProducto'),
		path('<int:_id>/eliminar/', views.eliminar_producto, name='vEliminarProducto'),
		])),
	#path('error/', views.error, name='vError'),
]