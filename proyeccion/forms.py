from django import forms
from django.contrib.auth.models import User
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
    
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 
                  'last_name', 
                  'email',
                  'avatar',
                  'telefono',
                  'empresa'
                  )