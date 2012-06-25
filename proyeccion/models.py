from django.db import models

# Create your models here.
 
class Producto(models.Model):
    """ Clase producto """
    nombre  =   models.CharField(max_length=200)
    tipo    =   models.CharField(max_length=100)
    precio  =   models.FloatField()
    stock   =   models.IntegerField()
    
    def __str__(self):
        return self.nombre

class Empresa(models.Model):
    """ Clase empresa """
    nombre  =   models.CharField(max_length=200)
    rut     =   models.CharField(max_length=200)
    
    def __str__(self):
        return self.nombre
    
class Sucursal(models.Model):
    """ Clase Scursal """
    empresa     =   models.ForeignKey(Empresa)
    nombre      =   models.CharField(max_length=200)
    direccion   =   models.CharField(max_length=200)
    
    def __str__(self):
        return self.nombre
    
class Venta(models.Model):
    """ Clase venta """
    sucursal    =   models.ForeignKey(Sucursal)
    fecha       =   models.DateTimeField()

class Contiene(models.Model):
    """ Clase Contiene - relacion entre producto y venta"""
    producto    =   models.ForeignKey(Producto)
    venta       =   models.ForeignKey(Venta)    

class Usuario(models.Model):
    """ Clase Usuario """
    nombre  =   models.CharField(max_length=200)
    cargo   =   models.CharField(max_length=200)
    usuario =   models.CharField(max_length=100)
    password=   models.CharField(max_length=200)
    
    def __str__(self):
        return self.nombre
    
class Proveedor(models.Model):
    """ Clase proveedor """
    tipo        =   models.CharField(max_length=100)
    nombre      =   models.CharField(max_length=200)
    numero      =   models.CharField(max_length=100)
    direccion   =  models.CharField(max_length=200)
    
    def __str__(self):
        return self.nombre
    
class Pedido(models.Model):
    """ Clase Pedido """
    proveedor       =   models.ForeignKey(Proveedor)
    producto        =   models.ForeignKey(Producto)
    sucursal        =   models.ForeignKey(Sucursal)
    fecha           =   models.DateTimeField()
    cantidad        =   models.IntegerField()
    precio          =   models.FloatField()
    product_manager =   models.CharField(max_length=200)