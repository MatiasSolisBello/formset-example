from django import forms
from django.urls import reverse
from django.utils.translation import gettext as _
from django.forms.models import inlineformset_factory
from core.models import Author, Book
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Div, Layout, Row, Submit

class ConfirmDeleteForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = []
        
        
class AuthorForm(forms.ModelForm):
    name = forms.CharField(max_length=100, label="Nombre")

    class Meta:
        model = Author
        fields = (
            'name',
        )
        
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('title', 'published_year')
        
        
BookFormSet = inlineformset_factory(
    Author,
    Book,
    form=BookForm,
    extra=1,
    min_num=1,
    can_delete=True
)