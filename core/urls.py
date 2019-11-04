from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'core'

urlpatterns = [
	path('', views.index, name='Index'),
	path('login/', views.bison_login, name='Blogin'),
	path('logout/', views.bison_logout, name='Blogout'),
	path('empleados/', include([
		path('', views.lista_empleados, name='vListaEmpleados'),
		path('todos/', views.lista_empleados, {'todos':True}, name='vTodosEmpleados'),
		path('ver/<str:id_emp>/', views.ver_empleado, name='vVerEmpleado'),
		path('nuevo/', views.nuevo_empleado, name='vNuevoEmpleado'),
		path('nuevo/usuario/', views.nuevo_empleado_usuario, name='vNuevoEmpleadoUsuario'),
		path('editar/<str:id_emp>/', views.editar_empleado, name='vEditarEmpleado'),
		path('eliminar/<str:_id>/', views.eliminar_empleado, name='vEliminarEmpleado'),
		path('desactivar/<str:_id>/', views.desactiva_empleado, name='vDesactivarEmpleado'),
		path('<str:id_emp>/asignar-usuario/', views.asignar_usuario, name='vAsignarUsuario'),
		])),
	path('usuarios/', include([
		path('', views.lista_usuarios, name='vListaUsuarios'),
		path('todos/', views.lista_usuarios, {'todos':True}, name='vTodosUsuarios'),
		path('nuevo/', views.nuevo_usuario, name = 'vNuevoUsuario'),
		path('ver/<int:id_usuario>/', views.ver_usuario, name='vVerUsuario'),
		path('password/change/<int:id_usuario>/', views.password_user_change, name='vCambiarPassword'),
		path('eliminar/<int:_id>/', views.eliminar_usuario, name='vEliminarUsuario'),
		path('desactivar/<int:_id>/', views.desactivar_usuario, name='vDesactivaUsuario'),
		])),
	path('categorias/', include([
		path('', views.lista_categorias, name='vListaCategorias'),
		path('nuevo/', views.nueva_categoria, name='vNuevaCategoria'),
		path('editar/<int:_id>/', views.editar_categoria, name='vEditarCategoria'),
		path('eliminar/<int:_id>/', views.eliminar_categoria, name='vEliminarCategoria'),
		])),
	path('medidas/', include([
		path('', views.lista_medidas, name='vListaMedidas'),
		path('nuevo/', views.nueva_medida, name='vNuevaMedida'),
		path('editar/<int:_id>/', views.editar_medida, name='vEditarMedida'),
		path('eliminar/<int:_id>/', views.eliminar_medida, name='vEliminarMedida'),
		])),
]