#proyecta
========

Calculo y proyecciones de ventas desarrollado pensado en el sector retail.

#Datos Tecnicos
========

Desarrollado con Python, uso del Framework Django para la interfaz web y del
proyecto R-project para el calculo de las proyecciones, tambien se hace uso de 
Rpy2 para la conexion de R y Python.

La base de datos implementada es Postgres, pero con Django puedes utilizar
la que se te venga en gana, basta cambiar la config inicial y podras utilizar
MySQL, Postgres, o la que acepte Django.

#Requisitos
========
R-project - Software de calculo estadistico
Rpy2 - Conector para python con R-project

#Instalacion y modo de uso
=======

1) Comienza descargando el codigo fuente de la aplicacion:
 git clone git://github.com/HenuXmail/proyecta.git

2) Crea y configura la base de datos en el archivo settings.py del directorio raiz

3) Instala las aplicaciones que son requisito para el uso de proyecta:
    R-project
    Rpy2
    python-django-extensions
    python-psycopg2
    grappelli

4) Actualiza la base de datos con los modelos de la aplicacion:
    python manage.py syncdb
    
5) Listo, ahora solo queda probar y utilizar proyecta en su sistema!!! :D

6) Para reportar fallas, o sugerencias, las puedes hacer via Github por medio
de los issues o al correo hola@jotamiller.cl.
