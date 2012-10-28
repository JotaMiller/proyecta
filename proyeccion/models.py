# Modelos de Aplicacion Proyecta
 
from django.db import models
from django.contrib.auth.models import User

#Perfil de usurio
class UserProfile(models.Model):
    user        =   models.OneToOneField(User)
    empresa     =   models.ForeignKey("Empresa")
    avatar      =   models.ImageField(upload_to='avatar')
    cargo       =   models.CharField( max_length = 100 )

#Clase producto
class Producto(models.Model):
    nombre      =   models.CharField( max_length = 100 )
    tipo        =   models.CharField( max_length = 100 )
    precio      =   models.IntegerField()
    stock       =   models.IntegerField()
    fabricante  =   models.CharField( max_length = 100 )
    #ventas      = models.ManyToManyField("Venta")
    
    def __str__(self):
        return self.nombre

#Clase Ventas
class Venta(models.Model):
    producto       =   models.ForeignKey("Producto")
    tiempo              =   models.ForeignKey("Tiempo")
    sucursal            =   models.ForeignKey("Sucursal")
    cantidad_vendida    =   models.IntegerField()
    total_venta         =   models.IntegerField()

#Clase Sucursal
class Sucursal(models.Model):
    empresa     =   models.ForeignKey("Empresa")
    nombre      =   models.CharField( max_length = 100 )
    direccion   =   models.CharField( max_length = 200 )
    zona        =   models.CharField( max_length = 100 )
    provincia   =   models.CharField( max_length = 100 )
    localidad   =   models.CharField( max_length = 100 )
    #ventas      =   models.ManyToManyField("Venta")
    
    def __str__(self):
        return self.nombre
    
#Clase Empresa
class Empresa(models.Model):
    nombre      =   models.CharField( max_length = 100 )
    rut         =   models.CharField( max_length = 20 )
    logo        =   models.ImageField( upload_to='logos' )
    telefono    =   models.CharField( max_length = 50 )
    
    def __str__(self):
        return self.nombre

#Clase tiempo
class Tiempo(models.Model):

    fecha       =   models.DateField()
    dia_semana  =   models.CharField( max_length = 20 )
    dia_mes     =   models.IntegerField()
    semana_ano  =   models.IntegerField()
    mes         =   models.IntegerField()
    trimestre   =   models.CharField( max_length = 20 )
    ano         =   models.IntegerField()
    
    


