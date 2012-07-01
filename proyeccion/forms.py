from django import forms

TIPOS_REPORTES = (
    ('normal', 'Normal'),
    ('basico', 'Basico'),
    ('detallado', 'Detallado'),
)

TIPOS_GRAFICOS = (
    ('torta', 'Torta'),
    ('barra', 'Barra'),
    ('otro', 'otro'),
)
class ConsultaForm(forms.Form):
    tipo            =   forms.ChoiceField(choices=TIPOS_REPORTES)
    fecha_inicio    =   forms.DateField() 
    fecha_termino   =   forms.DateField()
    tipo_grafico    =   forms.MultipleChoiceField(choices=TIPOS_GRAFICOS)
    message         =   forms.CharField()
    sender          =   forms.EmailField(required=False)