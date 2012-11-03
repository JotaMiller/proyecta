from proyeccion.models import Empresa
from proyeccion.models import Producto
from proyeccion.models import Tiempo
from proyeccion.models import Sucursal
from proyeccion.models import Venta
from django.contrib import admin
 
#class SucursalInLine(admin.TabularInline):
#    model = Sucursal
#    extra = 2
    
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'precio','stock', 'fabricante')
    
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut', 'telefono')
    
class SucursalAdmin(admin.ModelAdmin):
#    inlines = [SucursalInLine]
    list_display = ('nombre', 'direccion', 'zona', 'localidad', 'provincia')
    
class VentaAdmin(admin.ModelAdmin):
    list_display = ( 'sucursal', 'cantidad_vendida','total_venta')

class TiempoAdmin(admin.ModelAdmin):
    list_display = ('fecha','mes', 'ano')
    
#class VentaAdmin(admin.ModelAdmin):
#    list_display = ('sucursal', 'fecha')

admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Sucursal, SucursalAdmin)
admin.site.register(Venta, VentaAdmin)
admin.site.register(Tiempo, TiempoAdmin)