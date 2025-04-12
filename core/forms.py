from django import forms
from django.urls import reverse
from django.utils.translation import gettext as _
from core.models import Author
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Div, Layout, Row, Submit

class ConfirmDeleteForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = []
        
        
class AuthorForm(forms.ModelForm):
    name = forms.CharField(max_length=100, label="Nombre")
    
    """ class Media:
        js = (
            'parsley/parsley.min.js',
            'parsley/i18n/es.js',
            'parsley/custom_validators.js',
            'forms/form_validators.js',
        )

        css = {
            'all': ('parsley/parsley.css',)
        } """

    class Meta:
        model = Author
        fields = ['name']

        labels = {
            'name': _("Nombre"),
        }

        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'text',
                    'required': 'required'
                }
            ),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        url = reverse('list_authors')
        text_submit = _("Guardar")
        self.helper.form_action = url
        self.helper.form_class = 'form-parsley'
        self.helper.layout = Layout(
            Div(
                Row(
                    Column('name', css_class='col-md-12'),
                ),
                Row(
                    HTML(
                        '<a class="btn btn-lg btn-warning"'
                        'href="' + url + '" %}>Cancelar</a>'
                    ),
                    Submit(
                        'submit', text_submit,
                        css_class='btn btn-primary btn-lg float-right'
                    ),
                    css_class="d-flex justify-content-end"
                )
                
            ),

        )