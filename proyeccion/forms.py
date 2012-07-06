from django import forms
from proyeccion.models import Producto
from proyeccion.models import Sucursal

productos = Producto.objects.all()
sucursales = Sucursal.objects.all()

LISTA_PRODUCTOS = []
LISTA_SUCURSALES = []

for producto in productos:
    producto_obj = (producto.id, producto.nombre)
    LISTA_PRODUCTOS.append(producto_obj)

for sucursal in sucursales:
    sucursal_obj = (sucursal.id, sucursal.nombre)
    LISTA_SUCURSALES.append(sucursal_obj)


TIPOS_GRAFICOS = (
    ('torta', 'Torta'),
    ('barra', 'Barra'),
    ('otro', 'otro'),
)
class ConsultaForm(forms.Form):
    sucursal        =   forms.ChoiceField(choices=LISTA_SUCURSALES)
    producto        =   forms.ChoiceField(choices=LISTA_PRODUCTOS)
    fecha_inicio    =   forms.DateField() 
    fecha_termino   =   forms.DateField()
    tipo_grafico    =   forms.MultipleChoiceField(choices=TIPOS_GRAFICOS)