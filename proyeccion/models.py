# Modelos de Aplicacion Proyecta
 
from django.db import models
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

#Clase producto
class Producto(models.Model):
    """
    productos que fueron vendidos y con los cuales se realizaran los
    calculos estadisticos
    """
    venta       =   models.ForeignKey("Venta")
    nombre      =   models.CharField( max_length = 100 )
    tipo        =   models.CharField( max_length = 100 )
    precio      =   models.IntegerField()
    stock       =   models.IntegerField()
    fabricante  =   models.CharField( max_length = 100 )
    #ventas      = models.ManyToManyField("Venta")
    
    def __str__(self):
        return self.nombre

# validacion de las ventas
def validarVentas(value):
    if value > total_venta:
        raise ValidationError("El 'Total Venta' no puede ser inferior a la Cantidad Vendida")

#Clase Ventas
class Venta(models.Model):
    """
    Ventas realizadas
    """
    #producto            =   models.ForeignKey("Producto")
    #tiempo              =   models.ForeignKey("Tiempo")
    sucursal            =   models.ForeignKey("Sucursal")
    cantidad_vendida    =   models.IntegerField()
    total_venta         =   models.IntegerField()
    
    def __str__(self):
        return str(self.sucursal)

    def clean(self):
        # Don't allow draft entries to have a pub_date.
        if self.total_venta <= self.cantidad_vendida:
            raise ValidationError('La Cantidad vendida no puede ser mayor al Total Venta')

#Clase Sucursal
class Sucursal(models.Model):
    """
    Lista de sucursales asociadas a una empresa
    """
    empresa     =   models.ForeignKey("Empresa")
    nombre      =   models.CharField( max_length = 100 )
    direccion   =   models.CharField( max_length = 200 )
    zona        =   models.CharField( max_length = 100 )
    provincia   =   models.CharField( max_length = 100 )
    localidad   =   models.CharField( max_length = 100 )
    #ventas      =   models.ManyToManyField("Venta")
    
    def __str__(self):
        return self.nombre
    
def validarRut(value):
    rut_ing = value.replace(".", "");
    rut_ing = rut_ing.upper()
    numero = rut_ing.split("-")

    if not numero[0].isnumeric():
        raise ValidationError("El rut debe tener solo NUMERO y Guion")

    rut = digito(int(numero[0]))

    if rut != rut_ing:
        raise ValidationError("El Rut ingresado no existe")

#Clase Empresa
class Empresa(models.Model):
    """
    Clase encargada a guardar las empresas registradas en el sistema
    """
    nombre      =   models.CharField( max_length = 100 )
    rut         =   models.CharField( max_length = 20, validators=[validarRut] )
    logo        =   models.ImageField( upload_to='logos' )
    telefono    =   models.CharField( max_length = 50 )
    
    def __str__(self):
        return self.nombre

def digito(num):
    ini=num
    conta=2
    suma=0
    while num>0:
        suma= suma + (conta * (num % 10) )
        conta=conta+1
        if conta==8:
            conta=2     
        num=num/10
    conta=suma%11
    valor=11-conta
    if valor==10:
        valor="K"   
    if valor==11:
        valor="0"
    return "%s-%s"%(ini,valor)

#Clase tiempo
class Tiempo(models.Model):
    
    venta       =   models.ForeignKey("Venta")
    fecha       =   models.DateField()
    dia_semana  =   models.CharField( max_length = 20 )
    dia_mes     =   models.IntegerField()
    semana_ano  =   models.IntegerField()
    mes         =   models.IntegerField()
    trimestre   =   models.CharField( max_length = 20 )
    ano         =   models.IntegerField()
    
    def __str__(self):
        return str(self.fecha)


   
User.add_to_class('direccion', models.CharField( max_length = 100,null=True,blank=True))
User.add_to_class('telefono', models.CharField( max_length = 100, null=True,blank=True))
User.add_to_class('avatar', models.ImageField( upload_to = "avatar",null=True,blank=True))
User.add_to_class('empresa', models.ForeignKey(Empresa,null=True,blank=True))

