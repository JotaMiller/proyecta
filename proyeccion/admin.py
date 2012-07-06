from proyeccion.models import Empresa
from proyeccion.models import Producto
from proyeccion.models import TipoProducto
from proyeccion.models import Sucursal
from proyeccion.models import Venta
from proyeccion.models import Usuario
from proyeccion.models import Proveedor
from proyeccion.models import Pedido
from django.contrib import admin

class SucursalInLine(admin.TabularInline):
    model = Sucursal
    extra = 2
    
class TipoProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'precio', 'stock')
    
class EmpresaAdmin(admin.ModelAdmin):
    inlines = [SucursalInLine]
    list_display = ('nombre', 'rut')
    
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_manager', 'fecha','cantidad')

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id','tipo', 'nombre', 'numero', 'direccion')
    
class VentaAdmin(admin.ModelAdmin):
    list_display = ('sucursal', 'fecha')
     
admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(TipoProducto, TipoProductoAdmin)
admin.site.register(Producto, ProductoAdmin)
#admin.site.register(Sucursal)
admin.site.register(Venta, VentaAdmin)
admin.site.register(Usuario)
admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(Pedido,PedidoAdmin)