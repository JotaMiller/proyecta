# Modelos de Aplicacion Proyecta
#
# @author: JMiller
 
from django.db import models

# Create your models here.
class TipoProducto(models.Model):
    """ Clase tipo de producto """
    nombre  =   models.CharField(max_length=100)
    descripcion = models.TextField()
    
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
    
    # Se agrega terminacion en plural
    class Meta:
        verbose_name_plural = "Sucursales"
        
    def __str__(self):
        return self.nombre
   
class Producto(models.Model):
    """ Clase producto """
    tipo    =   models.ForeignKey(TipoProducto)
    nombre  =   models.CharField(max_length=200)
    precio  =   models.FloatField()
    stock   =   models.IntegerField()
    #venta   =   models.ManyToManyField(Venta)
    
    def __str__(self):
        return self.nombre

class Venta(models.Model):
    """
    Clase venta
    """
    sucursal    =   models.ForeignKey(Sucursal)
    fecha       =   models.DateField()
    productos    =   models.ManyToManyField(Producto)
    
    def total_ventas(self):
        """
        Retorna el total de las ventas el periodo
        """
        return 'total'
    
        
    # @param producto: id del producto a consultar
    # @param inicio: Fecha de inicio de la consulta
    # @param fin: feche fin de la consulta
    # @param n_periodos: Cant. de periodos a realizar la proyeccion
    # @type producto: int
    # @type inicio: date
    # @type fin: date
    # @type n_periodos: int
    # @return: tupla - ventas
    def proyeccion_venta(self, producto, inicio, fin, n_periodos):
        """
        Funcion que retoma la proyeccion de venta en periodos futuros
        """
#        import datetime
#        #result = 'jimmy', 'miller', 'mella'
#        result = []
#        for item in self.objects.all():  
#            result.append(item)
#        return result
#        

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
    
    # Se agrega terminacion en plural
    class Meta:
        verbose_name_plural = "proveedores"
        
    def __str__(self):
        return self.nombre
    
class Pedido(models.Model):
    """ Clase Pedido """
    proveedor       =   models.ForeignKey(Proveedor)
    producto        =   models.ForeignKey(Producto)
    sucursal        =   models.ForeignKey(Sucursal)
    fecha           =   models.DateField()
    cantidad        =   models.IntegerField()
    precio          =   models.FloatField()
    product_manager =   models.CharField(max_length=200)