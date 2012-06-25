from proyeccion.models import Empresa
from proyeccion.models import Producto
from proyeccion.models import Sucursal
from proyeccion.models import Venta
from proyeccion.models import Usuario
from proyeccion.models import Proveedor
from proyeccion.models import Pedido
from django.contrib import admin

class SucursalInLine(admin.TabularInline):
    model = Sucursal
    extra = 2
    
class EmpresaAdmin(admin.ModelAdmin):
    inlines = [SucursalInLine]
    list_display = ('nombre', 'rut')
    
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_manager', 'fecha','cantidad')

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id','tipo', 'nombre', 'numero', 'direccion')
    
    
admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Producto)
#admin.site.register(Sucursal)
admin.site.register(Venta)
admin.site.register(Usuario)
admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(Pedido,PedidoAdmin)