# Configuración
## Gestión de Usuarios
Como administrador, quiero crear un un usuario nuevo dentro del modulo configuración, en donde tendré que rellenar los siguientes campos:
- Nombre Completo
- Email
- Rol: (Administrador, Ventas, Producción y Operario)

Nota: por predeterminado una vez que se cree el usuario se creara una contraseña del 1 al 8 y deberá ser cambiado por el usuario en su primer inicio de sesión.

El usuario creado tendrá que verse en una tabla de gestión de usuarios con las siguientes columnas:
- Usuario
- Email:
- Rol
- Estado (Explicación de los frontend)
- Acciones (CRUD)
## Configuración del Negocio
Como administrador, quiero modificar los datos de mi empresa para mantenerlo siempre actualizado en caso de algún tipo de cambio, los campos que hay son:
- Nombre de Empresa
- Dirección
- Teléfono
- Email Corporativo
- RUC
- Tipo de Moneda (Soles, Dólar y Euro)
Teniendo un botón para actualizar todo estos campos.
## Roles y Permisos
Como administrador, tengo la opción de poder administrar los permisos de los roles (Administrador, Ventas, Producción y Operario) por modulo y Acciones sensible (consultar con frontend):
Accesos a Modulo que se pueden administrar:
- Dashboard
- Agenda
- Pedidos
- Clientes
- Inventario
- Activos 
- Gastos 
- Producción
- Contratos
- Reportes
Tener la opción de (Restablecer por defecto) los permisos por completo y botón para guardar los cambios

Dudas: 
- Estados para gestión de usuario
- Acciones sensibles en roles y permisos 
# Mi Perfil 
Como usuario, quiero ver mi perfil para consultar mis datos personales, mis estadísticas del mes y mi actividad reciente, y poder actualizar mi email, contraseña o información del perfil cuando lo necesite. 
Criterios de aceptación 
- Ver datos: nombre, email, teléfono, rol, dirección y biografía. 
- Estado de cuenta: indicador de “Cuenta Verificada” y fechas de registro/última conexión. 
- Estadísticas: pedidos procesados, clientes atendidos, sesiones realizadas y horas trabajadas del mes. 
- Actividad reciente: lista cronológica con eventos y marca de tiempo. 
- Acciones: botones para:
	-  Cambiar Email
		- Contraseña Actual
		- Nuevo Email
		- Confirmar Nuevo Email
	- Cambiar Contraseña
		- Contraseña Actual
		- Nueva Contraseña
		- Confirmar Nueva Contraseña
	- Editar Perfil
		- nombre
		- email
		- teléfono
		- rol
		- dirección
		- biografía. 
# Reportes
Exportar: 
- Excel
- PDF
Duda: se exporta todo lo que se encuentra en reportes o van agregar un opciones de que categoría se va a exportar?
Filtro:
- por fecha a fecha (personalizado)
- opciones por filtro
	- hoy
	- esta semana
	- este mes
	- este trimestre
	- es año
Categorías de Reportes: 
- Ventas:
	- 4 vistas de tarjetas Métricas: 
		- Ventas Totales: suma total de todo el monto de Ventas por tipo de producto
		- Pedidos Completados: sale del modulo de pedidos, en la tabla de la columna estados donde diga (completado) contara y sumara dentro de esta tarjeta.
		- Ticket Promedio (de donde jala esto?)
		- Crecimiento (no estoy seguro de como va esto, explicacion??)
	- 2 tablas:
		- Ventas por tipo de producto: columnas
			- tipo de producto: por predeterminado estará enmarcados, minilab, graduaciones, corte laser y (no falta accesorios?)
			- cantidad: (de cada tipo de producto)
			- monto: precio total de cantidad de cada tipo de producto
			- % del total: proporción del monto de ventas de cada tipo de producto en relación con el monto total de todas las ventas combinadas
		- Top (10) Clientes del periodo: campos
			- cliente: clientes con mas pedidos
			- pedidos: cantidad de mayor a menor 
			- monto total: la suma total de todos los pedidos del cliente
- Inventario: 
	- 3 vistas de tarjetas métricas:
		- valor total de inventario: suma total de todo el monto de Inventario por categoría
		- ítems bajo stock: la suma total de todo stock bajo de Inventario por categoría
		- sin movimiento: (no se como va esto, explicacion)
	- 2 tablas
		- Inventario por categoria: columnas
			- categoria: por predeterminado estará enmarcados, minilab, graduaciones, corte laser y (no falta accesorios?)
			- valor: suma total de todo lo que se encuentra en inventario dependiendo de la categoria si es enmarcados, minilab, graduaciones, corte laser y (no falta accesorios?)
			- items: suma total de inventario dependiendo de que tipo de categoria,  mas sumados las sub categorias 
			- stock bajo: no se como va esto, explicacion?
		- Alertas de reabastecimiento: columnas, todo sale del modulo de inventario
			- producto: solo se visualizara el producto que se encuentre igual o debajo del stock minimo
			- categoria: si es enmarcados, minilab, graduaciones, corte laser y (no falta accesorios?)
			- stock actual: muestra el stock actual del producto que se encuentre igual o debajo del stock minimo
			- stock minimo: muestra el stcok minimo que se halla registrado en el modulo de inventario
- Producción
- Clientes
- Financiado
- Contratos